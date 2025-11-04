import csv
import os
from datetime import datetime
from pathlib import Path


def get_site_file_path(site_name: str, base_path: Path, use_temp: bool = False) -> Path:
    filename = f"{site_name}_{datetime.now().strftime('%Y%m%d')}"
    if use_temp:
        filename += "_buffer"
    filename += ".csv"
    return Path(base_path).joinpath(filename)


def save_articles_to_csv(site_name: str, base_url: str, articles: set, filter_keys: dict, base_path: Path,
                         use_temp: bool = False):
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)

    temp_path = get_site_file_path(site_name, base_path, use_temp=use_temp)
    final_path = get_site_file_path(site_name, base_path, use_temp=False)

    with open(temp_path, mode="w", encoding="utf-8", newline="") as file:
        columns = ["site", "timestamp", "title", "entities", "keywords", "summary", "url", "comments"]
        writer = csv.DictWriter(file, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
        # writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for article in articles:
            if base_url not in article.url or is_filtered(article, filter_keys):
                continue
            writer.writerow({
                "site": article.site,
                "timestamp": article.timestamp.isoformat(),
                "title": article.title,
                "entities": ", ".join(article.entities),
                "keywords": ", ".join(article.keywords),
                "summary": article.summary,
                "url": article.url,
                "comments": article.comments
            })

    os.replace(temp_path, final_path)  # Always move to final


def is_filtered(article, filter_place_keys):
    including = set(word.lower() for word in filter_place_keys.get("including", []))
    excluding = set(word.lower() for word in filter_place_keys.get("excluding", []))
    places = filter_place_keys.get("place", [])

    # Gather text from specified places
    text_blob = []
    for place in places:
        value = getattr(article, place, "")
        if isinstance(value, list):
            text_blob.extend(value)
        elif isinstance(value, str):
            text_blob.append(value)

    combined_text = " ".join(text_blob).lower()

    # Exclude if any exclusion keyword is found
    if any(word in combined_text for word in excluding):
        return True

    # Include only if at least one inclusion keyword is found
    if including and not any(word in combined_text for word in including):
        return True

    return False


def fix_romanian_diacritics(text):
    return (
        text.replace("ş", "ș")
        .replace("Ş", "Ș")
        .replace("ţ", "ț")
        .replace("Ţ", "Ț")
    )
