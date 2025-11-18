import csv
import io
import os
from datetime import datetime
from pathlib import Path

import boto3

from app.utils.env_vars import APP_ENV, S3_PREFIX, S3_BUCKET


def get_site_file_path(site_name: str, base_path: Path, use_temp: bool = False) -> Path:
    filename = f"{site_name}_{datetime.now().strftime('%Y%m%d')}"
    if use_temp:
        filename += "_buffer"
    filename += ".csv"
    return Path(base_path).joinpath(filename)


def get_site_file_name(site_name: str, use_temp: bool = False) -> str:
    filename = f"{site_name}_{datetime.now().strftime('%Y%m%d')}"
    if use_temp:
        filename += "_buffer"
    return filename + ".csv"


def save_articles_to_csv(site_name, base_url, articles, filter_keys, base_path: Path, use_temp=False):
    filename = get_site_file_name(site_name, use_temp)
    temp_path = Path(base_path) / filename

    output = io.StringIO()
    columns = ["site", "timestamp", "title", "entities", "keywords", "summary", "url", "comments"]
    writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
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

    csv_data = output.getvalue()

    if APP_ENV == "uat":
        s3 = boto3.client("s3")
        s3_key = f"{S3_PREFIX}/{filename}"
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=csv_data.encode("utf-8"))
    else:
        os.makedirs(base_path, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(csv_data)


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
