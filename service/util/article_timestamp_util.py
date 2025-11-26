# service/util/article_timestamp_util.py

import re
from datetime import datetime, timezone
from dateutil import parser
from bs4 import BeautifulSoup, Tag

from service.util.logger_util import get_logger

logger = get_logger()

RO_TO_EN_MONTHS = {
    # Full month names
    "ianuarie": "January", "februarie": "February", "martie": "March",
    "aprilie": "April", "mai": "May", "iunie": "June",
    "iulie": "July", "august": "August", "septembrie": "September",
    "octombrie": "October", "noiembrie": "November", "decembrie": "December",

    # Abbreviated forms (with and without dot)
    "ian.": "January", "feb.": "February", "mar.": "March",
    "apr.": "April", "mai.": "May", "iun.": "June",
    "iul.": "July", "aug.": "August", "sep.": "September",
    "sept.": "September", "oct.": "October", "nov.": "November", "dec.": "December",

    "ian": "January", "feb": "February", "mar": "March",
    "apr": "April", "iun": "June", "iul": "July",
    "aug": "August", "sep": "September", "sept": "September",
    "oct": "October", "nov": "November", "dec": "December"
}


def extract_time_tag(soup: BeautifulSoup, selector: str) -> Tag | None:
    return soup.select_one(selector)


def get_fallback_date(selector: str, return_both: bool = False):
    fallback = datetime.now(timezone.utc)
    logger.debug(f"[Timestamp] Fallback used for selector: {selector}")
    return (fallback, fallback) if return_both else fallback


def get_local_utc_date(match: re.Match, return_both: bool = False):
    raw = match.group()

    # Extract only the date portion (e.g., "30 octombrie 2025 09:41")
    date_match = re.search(r"\d{1,2}\s+\w+\.?\s+\d{4}[,]?\s*\d{2}:\d{2}", raw)
    if not date_match:
        raise ValueError(f"No valid datetime found in match: {raw}")
    date_str = date_match.group()

    # Translate Romanian month names to English
    for ro, en in RO_TO_EN_MONTHS.items():
        date_str = re.sub(rf"\b{re.escape(ro)}\b", en, date_str, flags=re.IGNORECASE)

    try:
        local_dt = parser.parse(date_str, dayfirst=True)
        utc_dt = local_dt.astimezone(timezone.utc)
        return (local_dt, utc_dt) if return_both else utc_dt
    except Exception as e:
        raise ValueError(f"Failed to parse translated date string: {date_str}") from e


def extract_timestamp_from_selector(soup: BeautifulSoup, selector: str, return_both: bool = False):
    tag = extract_time_tag(soup, selector)
    if not tag:
        link_tag = soup.find("a", class_="read-more-link") or soup.find("a", title="Mergi la articol")
        href = None
        if link_tag and link_tag.has_attr("href"):
            href = link_tag["href"]
        logger.debug(f"No valid timestamp found in selector: {selector} for {href}")
        return get_fallback_date(selector, return_both)

    # Sport.ro-style: <span data-utc-date="2025-11-23 16:57:42">
    if tag.has_attr("data-utc-date"):
        try:
            raw_dt = tag["data-utc-date"]
            local_dt = parser.parse(raw_dt)  # already full datetime string
            utc_dt = local_dt.astimezone(timezone.utc)
            return (local_dt, utc_dt) if return_both else utc_dt
        except Exception as e:
            logger.warning(f"[Timestamp] Failed to parse Sport.ro data-utc-date: {e}")

    # noinspection PyArgumentList
    text = tag.get_text(separator=" ", strip=True)

    # Digisport-style: 30.10.2025, 13:08
    match_digisport = re.search(r"\d{2}\.\d{2}\.\d{4}[,|]\s*\d{2}:\d{2}", text)
    if match_digisport:
        local_dt = parser.parse(match_digisport.group().replace("|", ","), dayfirst=True)
        utc_dt = local_dt.astimezone(timezone.utc)
        return (local_dt, utc_dt) if return_both else utc_dt

    # Fanatik-style: 30.10.2025 | 13:35
    match_fanatik = re.search(r"\d{2}\.\d{2}\.\d{4}\s*\|\s*\d{2}:\d{2}", text)
    if match_fanatik:
        cleaned = match_fanatik.group().replace("|", ",")
        local_dt = parser.parse(cleaned, dayfirst=True)
        utc_dt = local_dt.astimezone(timezone.utc)
        return (local_dt, utc_dt) if return_both else utc_dt

    # Golazo-style: Prefer 'Actualizat', fallback to 'Publicat'
    # Examples (observed/likely):
    # "Actualizat 25 noiembrie 2025, 12:34"
    # "Publicat 25 noiembrie 2025, 12:34"
    match_golazo_updated = re.search(
        r"Actualizat\s+(?:\w+,)?\s*\d{1,2}\s+\w+\.?\s+\d{4}[,]?\s*\d{2}:\d{2}", text, flags=re.IGNORECASE
    )
    if match_golazo_updated:
        try:
            return get_local_utc_date(match_golazo_updated, return_both)
        except Exception as e:
            logger.warning(f"[Timestamp] Failed to parse Golazo 'Actualizat': {e}")

    match_golazo_published = re.search(
        r"Publicat\s+(?:\w+,)?\s*\d{1,2}\s+\w+\.?\s+\d{4}[,]?\s*\d{2}:\d{2}", text, flags=re.IGNORECASE
    )
    if match_golazo_published:
        try:
            return get_local_utc_date(match_golazo_published, return_both)
        except Exception as e:
            logger.warning(f"[Timestamp] Failed to parse Golazo 'Publicat': {e}")

    # GSP-style: Prefer 'Actualizat', fallback to 'Publicat'
    match_updated = re.search(r"Actualizat\s+(?:\w+,)?\s*\d{1,2}\s+\w+\s+\d{4}[,]?\s*\d{2}:\d{2}", text)
    if match_updated:
        try:
            return get_local_utc_date(match_updated, return_both)
        except Exception as e:
            logger.warning(f"[Timestamp] Failed to parse 'Actualizat': {e}")

    match_published = re.search(r"Publicat\s+(?:\w+,)?\s*\d{1,2}\s+\w+\s+\d{4}[,]?\s*\d{2}:\d{2}", text)
    if match_published:
        try:
            return get_local_utc_date(match_published, return_both)
        except Exception as e:
            logger.warning(f"[Timestamp] Failed to parse 'Publicat': {e}")

    # GSP fallback: 30 octombrie 2025, 12:15
    match_gsp_fallback = re.search(r"\d{1,2}\s+\w+\s+\d{4}[,]?\s*\d{2}:\d{2}", text)
    if match_gsp_fallback:
        try:
            return get_local_utc_date(match_gsp_fallback, return_both)
        except Exception as e:
            logger.warning(f"[Timestamp] Failed to parse GSP-style fallback: {e}")

    # Prosport-style: 30 oct. 2025, 12:50
    match_prosport = re.search(r"\d{1,2}\s+\w+\.?\s+\d{4},\s*\d{2}:\d{2}", text)
    if match_prosport:
        cleaned = match_prosport.group()
        for ro, en in RO_TO_EN_MONTHS.items():
            cleaned = re.sub(rf"\b{re.escape(ro)}\b", en, cleaned, flags=re.IGNORECASE)
        local_dt = parser.parse(cleaned, dayfirst=True)
        utc_dt = local_dt.astimezone(timezone.utc)
        return (local_dt, utc_dt) if return_both else utc_dt

    return get_fallback_date(selector, return_both)
