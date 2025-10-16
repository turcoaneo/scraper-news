import json
from pathlib import Path
from typing import List

from model.model_type import ModelType  # Assuming you have this Enum
from service.site_scraper import SiteScraper


def load_sites_from_config(config_path: str = None) -> List[SiteScraper]:
    if config_path is None:
        config_path = Path(__file__).parent / "sites_config.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    sites = []
    for entry in config:
        model_type = ModelType[entry.get("model", "BERT")]
        site = SiteScraper(
            name=entry["name"],
            base_url=entry["base_url"],
            traffic=entry["traffic"],
            time_selector=entry["time_selector"],
            block_selector=entry["block_selector"],
            link_selector=entry["link_selector"],
            title_strategy=entry["title_strategy"],
            title_attribute=entry.get("title_attribute"),
            model=model_type
        )
        site.compute_weight(entry["traffic"])
        site.load_recent_from_csv()
        sites.append(site)

    return sites
