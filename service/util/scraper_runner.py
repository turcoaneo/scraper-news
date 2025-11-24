# service/util/scraper_runner.py

import json
import threading
from datetime import datetime, timezone, timedelta
from functools import lru_cache

from transformers import T5Tokenizer, T5ForConditionalGeneration

from app.config.loader import load_sites_from_config
from app.utils.env_vars import HF_TOKEN
from model.article import Article
from model.model_type import ModelType
from service.cluster_service import ClusterService
from service.util.buffer_util import delete_delta_file_if_exists, update_delta_timestamp
from service.util.declension_util import DeclensionUtil
from service.util.delta_checker import DeltaChecker
from service.util.logger_util import get_logger
from service.util.path_util import T5_MODEL_PATH, PROJECT_ROOT
from service.util.timing_util import elapsed_time, log_thread_id

logger = get_logger()

# At module level
_last_scrape_times = {}
_lock = threading.Lock()
COOLDOWN_FILE = PROJECT_ROOT / 'storage' / 'cooldown.json'


def load_cooldowns():
    """Restore last scrape times from JSON file."""
    global _last_scrape_times
    if COOLDOWN_FILE.exists():
        try:
            with open(COOLDOWN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _last_scrape_times = {
                    site: datetime.fromisoformat(ts)
                    for site, ts in data.items()
                }
        except Exception as e:
            logger.warning(f"Failed to load cooldowns: {e}")
            _last_scrape_times = {}


def save_cooldowns():
    """Persist last scrape times to JSON file."""
    try:
        with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {site: ts.isoformat() for site, ts in _last_scrape_times.items()},
                f
            )
    except Exception as e:
        logger.warning(f"Failed to save cooldowns: {e}")


@lru_cache(maxsize=1)
def get_model_and_tokenizer():
    model_path = T5_MODEL_PATH
    hf_token = HF_TOKEN

    tokenizer = T5Tokenizer.from_pretrained(model_path, token=hf_token)
    model = T5ForConditionalGeneration.from_pretrained(model_path, token=hf_token)
    model.eval()
    return tokenizer, model


@elapsed_time("run_scraper")
def run_scraper(minutes=1440):
    load_cooldowns()  # restore cooldowns at startup

    logger.info("*" * 100)
    logger.info(f"Running {log_thread_id(threading.get_ident(), 'scraper')}")
    sites = load_sites_from_config()
    total_traffic = sum(site.traffic for site in sites)
    checked_traffic = 0
    for site in sites:
        site.compute_weight(total_traffic)
        logger.debug(f"{site.name}: {site.weight} / {total_traffic}")
        checked_traffic += site.weight
    logger.debug(f"Total: {checked_traffic}")

    @elapsed_time("process_site")
    def process_site(site):
        now = datetime.now(timezone.utc)
        cooldown = 60 if site.name.lower() == "sport" else 0

        if cooldown:
            with _lock:
                last = _last_scrape_times.get(site.name)
                if last and (now - last) < timedelta(minutes=cooldown):
                    logger.info(f"Skipping {site.name} scrape (cooldown active)")
                    return
                _last_scrape_times[site.name] = now
                save_cooldowns()  # persist after update

        logger.info(f"Scraping {log_thread_id(threading.get_ident(), site.name)}")
        site.scrape_recent_articles(minutes)

    @elapsed_time("save_site")
    def save_site(site):
        logger.info(f"Saving CSV for {log_thread_id(threading.get_ident(), site.name)}")
        site.save_to_csv(use_temp=True)

    def merge_articles(p_deltas: dict, previous_map: dict[str, Article], p_site_name: str) -> list[Article]:

        # Remove deleted
        removed_delta = p_deltas["removed"]
        logger.info(f"{p_site_name} has {len(removed_delta)} articles to be removed from")
        for removed in removed_delta:
            url = removed.url if hasattr(removed, "url") else removed.get("url")
            previous_map.pop(url, None)

        # Replace updated
        updated_delta = p_deltas["updated"]
        logger.info(f"{p_site_name} has {len(updated_delta)} articles to be updated")
        for updated in updated_delta:
            url = updated.url if hasattr(updated, "url") else updated.get("url")
            previous_map[url] = updated

        # Add new
        new_delta = p_deltas["new"]
        logger.info(f"{p_site_name} has {len(new_delta)} new articles")
        for new in new_delta:
            url = new.url if hasattr(new, "url") else new.get("url")
            previous_map[url] = new

        return list(previous_map.values())

    def dict_to_article(row: dict, p_site_name: str) -> Article:
        return Article(
            site=p_site_name,
            timestamp=row["timestamp"],
            title=row["title"],
            entities=row.get("entities", ""),
            keywords=row.get("keywords", ""),
            summary=row.get("summary", ""),
            url=row["url"],
            comments=int(row.get("comments", 0))
        )

    # Phase 1: Scraping (parallel)
    threads = [threading.Thread(target=process_site, args=(site,)) for site in sites]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    site_deltas = DeltaChecker.get_all_deltas(sites)

    is_skipped_for_all: bool = True
    for site_name, prev_and_curr_tuple in site_deltas.items():
        curr_articles = prev_and_curr_tuple[1]
        if len(curr_articles["new"]) + len(curr_articles["updated"]) != 0:
            logger.info(f"[Scraper] Deltas already detected: {site_name}. Break loop and continue with next phase.")
            is_skipped_for_all = False
            break
    if is_skipped_for_all:
        logger.info("[Scraper] No deltas detected. Skipping declension, saving, and clustering.")
        update_delta_timestamp()
        return

    # Phase 2: Declension (single-threaded, safe)
    tokenizer, model = get_model_and_tokenizer()

    for site in sites:
        deltas = site_deltas[site.name][1]
        articles_to_declension = deltas["new"] + deltas["updated"]
        logger.info(f"[Articles to Declension] {site.name}: {len(articles_to_declension)}")
    for site in sites:
        if site.model_type == ModelType.BERT:
            @elapsed_time(f"Declension for {site.name}")
            def process_declension():
                try:
                    for article in articles_to_declension:
                        article.entities = [DeclensionUtil.normalize(ent, (tokenizer, model)) for ent in
                                            article.entities]
                        article.keywords = [DeclensionUtil.normalize(kw, (tokenizer, model)) for kw in article.keywords]
                except Exception as e:
                    logger.info(f"[Declension Error] {site.name}: {e}")

            process_declension()

    # Phase 3: Merging old and deltas
    for site in sites:
        site_name = site.name
        site_delta_tuple_result = site_deltas[site_name]
        deltas = site_delta_tuple_result[1]
        raw_previous = site_delta_tuple_result[0] or {}
        previous_articles = {
            url: dict_to_article(row, site_name)
            for url, row in raw_previous.items()
        }
        merged_articles = merge_articles(deltas, previous_articles, site_name)
        site.articles = set(merged_articles)  # set instead of list
        logger.info(f"{site_name} - {len(site.articles)} articles")

    # Phase 4: Saving (parallel)
    threads = [threading.Thread(target=save_site, args=(site,)) for site in sites]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Phase 5: Clustering and buffer creation
    ClusterService.save_cluster_buffer(sites, minutes)

    # Phase 6: Delete delta file
    delete_delta_file_if_exists()
