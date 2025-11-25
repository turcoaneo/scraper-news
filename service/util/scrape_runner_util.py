# service/util/scrape_runner_util.py

import threading
from datetime import datetime, timezone, timedelta
from functools import lru_cache

from transformers import T5Tokenizer, T5ForConditionalGeneration

from app.utils.env_vars import HF_TOKEN
from model.article import Article
from service.util.cooldown_util import update_scrape_time, get_last_scrape_times
from service.util.logger_util import get_logger
from service.util.path_util import T5_MODEL_PATH
from service.util.timing_util import elapsed_time, log_thread_id

logger = get_logger()


class ScrapeRunnerUtil:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_model_and_tokenizer():
        tokenizer = T5Tokenizer.from_pretrained(T5_MODEL_PATH, token=HF_TOKEN)
        model = T5ForConditionalGeneration.from_pretrained(T5_MODEL_PATH, token=HF_TOKEN)
        model.eval()
        return tokenizer, model

    @staticmethod
    def merge_articles(p_deltas: dict, previous_map: dict[str, Article], p_site_name: str) -> list[Article]:
        removed_delta = p_deltas["removed"]
        logger.info(f"{p_site_name} has {len(removed_delta)} articles to be removed")
        for removed in removed_delta:
            url = removed.url if hasattr(removed, "url") else removed.get("url")
            previous_map.pop(url, None)

        updated_delta = p_deltas["updated"]
        logger.info(f"{p_site_name} has {len(updated_delta)} articles to be updated")
        for updated in updated_delta:
            url = updated.url if hasattr(updated, "url") else updated.get("url")
            previous_map[url] = updated

        new_delta = p_deltas["new"]
        logger.info(f"{p_site_name} has {len(new_delta)} new articles")
        for new in new_delta:
            url = new.url if hasattr(new, "url") else new.get("url")
            previous_map[url] = new

        return list(previous_map.values())

    @staticmethod
    def dict_to_article(row: dict, p_site_name: str) -> Article:
        return Article(
            site=p_site_name,
            timestamp=row["timestamp"],
            title=row["title"],
            entities=row.get("entities", ""),
            keywords=row.get("keywords", ""),
            summary=row.get("summary", ""),
            url=row["url"],
            comments=int(row.get("comments", 0)),
        )

    @staticmethod
    def compute_weights(sites):
        total_traffic = sum(site.traffic for site in sites)
        checked_traffic = 0
        for site in sites:
            site.compute_weight(total_traffic)
            logger.debug(f"{site.name}: {site.weight} / {total_traffic}")
            checked_traffic += site.weight
        logger.debug(f"Total: {checked_traffic}")

    @staticmethod
    @elapsed_time("process_site")
    def process_site(site, minutes=1440):
        now = datetime.now(timezone.utc)
        cooldown = 60 if site.name.lower() == "sport" else 0

        if cooldown:
            last = get_last_scrape_times().get(site.name)
            if last and (now - last) < timedelta(minutes=cooldown):
                logger.info(f"Skipping {site.name} scrape (cooldown active)")
                return
            update_scrape_time(site.name, now)

        logger.info(f"Scraping {log_thread_id(threading.get_ident(), site.name)}")
        site.scrape_recent_articles(minutes)

    @staticmethod
    @elapsed_time("save_site")
    def save_site(site):
        logger.info(f"Saving CSV for {log_thread_id(threading.get_ident(), site.name)}")
        site.save_to_csv(use_temp=True)
