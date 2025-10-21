import os
import threading
import time

from transformers import T5Tokenizer, T5ForConditionalGeneration

from app.config.loader import load_sites_from_config
from model.model_type import ModelType
from service.util.declension_util import DeclensionUtil
from service.util.path_util import PROJECT_ROOT


def get_model_and_tokenizer():
    model_path = os.path.join(PROJECT_ROOT, "t5_decorator_model")
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    model.eval()
    return tokenizer, model


def run_scraper(minutes=360):
    start_time = time.time()
    sites = load_sites_from_config()
    total_traffic = sum(site.traffic for site in sites)

    def process_site(site):
        print(f"Scraping {site.name}")
        s_time = time.time()
        site.compute_weight(total_traffic)
        site.scrape_recent_articles(minutes)

        duration = time.time() - s_time
        print(f"[Scraping for {site.name}] has taken: {duration:.3f}s")

    def save_site(site):
        print(f"Saving CSV for {site.name}")
        site.save_to_csv(use_temp=True)

    # Phase 1: Scraping (parallel)
    threads = [threading.Thread(target=process_site, args=(site,)) for site in sites]
    for t in threads: t.start()
    for t in threads: t.join()
    # for site in sites:
    #     process_site(site)

    # Phase 2: Declension (single-threaded, safe)
    tokenizer, model = get_model_and_tokenizer()
    for site in sites:
        if site.model_type == ModelType.BERT:
            print(f"Declension for {site.name}")
            start_time = time.time()
            try:
                for article in site.articles:
                    article.entities = [DeclensionUtil.normalize(ent, (tokenizer, model)) for ent in article.entities]
                    article.keywords = [DeclensionUtil.normalize(kw, (tokenizer, model)) for kw in article.keywords]
            except Exception as e:
                print(f"[Declension Error] {site.name}: {e}")
            elapsed = time.time() - start_time
            print(f"[Declension for {site.name}] has taken: {elapsed:.3f}s")

    # Phase 3: Saving (parallel)
    threads = [threading.Thread(target=save_site, args=(site,)) for site in sites]
    for t in threads: t.start()
    for t in threads: t.join()
    elapsed = time.time() - start_time
    print(f"Scraping all sites has taken: {elapsed:.3f}s")
