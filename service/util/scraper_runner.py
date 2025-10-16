# service/util/scraper_runner.py

from app.config.loader import load_sites_from_config


def run_scraper(minutes=360):
    sites = load_sites_from_config()
    total_traffic = sum(site.traffic for site in sites)
    for site in sites:
        site.compute_weight(total_traffic)
        site.scrape_recent_articles(minutes)
        site.save_to_csv()
