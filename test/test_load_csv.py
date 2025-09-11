import csv
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from site_scraper import SiteScraper  # Assuming Article is now imported from site_scraper


def create_csv(filename, rows):
    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "site", "timestamp", "title", "entities", "keywords", "summary", "url", "comments"
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class TestLoadCsv(unittest.TestCase):

    def test_load_recent_from_csv_with_romanian_quotes(self):
        scraper = SiteScraper("gsp", "https://example.com", 100, "", "", "", "text")
        now = datetime.now(timezone.utc)
        rows = [{
            "site": "gsp",
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "title": "„Demisia, demisia!” » Prima „ciocnire” a sezonului",
            "entities": "['Farul', 'Petrolul', 'Liviu Ciobotariu']",
            "keywords": "farul, „demisia”, petrolul",
            "summary": "Suporterii au scandat „Demisia” și „Jucați fotbal”",
            "url": "https://gsp.ro/article",
            "comments": "2"
        }]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            create_csv(tmp.name, rows)
            scraper.load_recent_from_csv(minutes=180, filename_override=tmp.name)

        self.assertEqual(len(scraper.articles), 1)
        article = scraper.articles.pop()
        self.assertIn("Demisia", article.title)
        self.assertIn("Jucați fotbal", article.summary)
        self.assertEqual(article.comments, 2)

    def test_load_recent_from_csv_all_loaded(self):
        scraper = SiteScraper("digisport", "https://example.com", 100, "", "", "", "text")
        now = datetime.now(timezone.utc)
        rows = [
            {
                "site": "digisport",
                "timestamp": (now - timedelta(minutes=10)).isoformat(),
                "title": "Title A",
                "entities": "['A']",
                "keywords": "key1,key2",
                "summary": "Summary A",
                "url": "https://a.com",
                "comments": "0"
            },
            {
                "site": "digisport",
                "timestamp": (now - timedelta(minutes=20)).isoformat(),
                "title": "Title B",
                "entities": "['B']",
                "keywords": "key3,key4",
                "summary": "Summary B",
                "url": "https://b.com",
                "comments": "1"
            }
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            create_csv(tmp.name, rows)
            scraper.load_recent_from_csv(minutes=180, filename_override=tmp.name)

        self.assertEqual(len(scraper.articles), 2)
        urls = {article.url for article in scraper.articles}
        self.assertIn("https://a.com", urls)
        self.assertIn("https://b.com", urls)

    def test_load_recent_from_csv_none_loaded(self):
        scraper = SiteScraper("oldnews", "https://example.com", 100, "", "", "", "text")
        old_time = datetime.now(timezone.utc) - timedelta(days=1)
        rows = [{
            "site": "oldnews",
            "timestamp": old_time.isoformat(),
            "title": "Old Title",
            "entities": "['X']",
            "keywords": "old1,old2",
            "summary": "Old Summary",
            "url": "https://old.com",
            "comments": "0"
        }]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            create_csv(tmp.name, rows)
            scraper.load_recent_from_csv(minutes=180, filename_override=tmp.name)

        self.assertEqual(len(scraper.articles), 0)
