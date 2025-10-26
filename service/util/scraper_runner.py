# service/util/scraper_runner.py

import os
import threading

from transformers import T5Tokenizer, T5ForConditionalGeneration

from app.config.loader import load_sites_from_config
from model.model_type import ModelType
from service.cluster_service import ClusterService
from service.util.declension_util import DeclensionUtil
from service.util.logger_util import get_logger
from service.util.path_util import PROJECT_ROOT
from service.util.timing_util import elapsed_time, log_thread_id

logger = get_logger()


def get_model_and_tokenizer():
    model_path = os.path.join(PROJECT_ROOT, "t5_decorator_model")
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    model.eval()
    return tokenizer, model


@elapsed_time("run_scraper")
def run_scraper(minutes=1440):
    logger.info(f"Running {log_thread_id(threading.get_ident(), 'scraper')}")
    sites = load_sites_from_config()
    total_traffic = sum(site.traffic for site in sites)
    for site in sites:
        site.compute_weight(total_traffic)

    @elapsed_time("process_site")
    def process_site(site):
        logger.info(f"Scraping {log_thread_id(threading.get_ident(), site.name)}")
        site.scrape_recent_articles(minutes)

    @elapsed_time("save_site")
    def save_site(site):
        logger.info(f"Saving CSV for {log_thread_id(threading.get_ident(), site.name)}")
        site.save_to_csv(use_temp=True)

    # Phase 1: Scraping (parallel)
    threads = [threading.Thread(target=process_site, args=(site,)) for site in sites]
    for t in threads: t.start()
    for t in threads: t.join()

    # Phase 2: Declension (single-threaded, safe)
    tokenizer, model = get_model_and_tokenizer()
    for site in sites:
        if site.model_type == ModelType.BERT:
            @elapsed_time(f"Declension for {site.name}")
            def process_declension():
                try:
                    for article in site.articles:
                        article.entities = [DeclensionUtil.normalize(ent, (tokenizer, model)) for ent in
                                            article.entities]
                        article.keywords = [DeclensionUtil.normalize(kw, (tokenizer, model)) for kw in
                                            article.keywords]
                except Exception as e:
                    logger.info(f"[Declension Error] {site.name}: {e}")

            process_declension()

    # Phase 3: Saving (parallel)
    threads = [threading.Thread(target=save_site, args=(site,)) for site in sites]
    for t in threads: t.start()
    for t in threads: t.join()

    # Phase 4: Clustering and buffer creation
    ClusterService.save_cluster_buffer(sites, minutes)
