import unittest
from datetime import datetime
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from service.article_scraper import ArticleScraper
from service.util import article_timestamp_util as ts_util


class TestArticleTimestampUtil(unittest.TestCase):
    def setUp(self):
        self.scraper = ArticleScraper(
            homepage_url="https://example.com/article",
            homepage_title="Rapid București câștigă dramatic",
            time_selector="time"
        )
        self.scraper.valid = True
        self.scraper.soup = MagicMock()

    def test_digisport_cite_tag(self):
        html = '''<cite> articol scris de <a href="/autor/digisport">Digi Sport</a><br> 30.10.2025, 13:08 </cite>'''
        soup = BeautifulSoup(html, "html.parser")
        ts = ts_util.extract_timestamp_from_selector(soup, "cite")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 10)
        self.assertEqual(ts.day, 30)
        self.assertEqual(ts.hour, 11)  # UTC conversion from 13:08 EEST
        self.assertEqual(ts.minute, 8)

    def test_fanatik_date_published(self):
        html = '''<div class="date_published"> 30.10.2025 | 13:35</div>'''
        soup = BeautifulSoup(html, "html.parser")
        ts = ts_util.extract_timestamp_from_selector(soup, "div.date_published")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 10)
        self.assertEqual(ts.day, 30)
        self.assertEqual(ts.hour, 11)  # UTC conversion from 13:35 EEST
        self.assertEqual(ts.minute, 35)

    def test_prosport_display_flex(self):
        html = '''
        <div class="display-flex gap-5">
            30 oct. 2025, 12:50,
            <a class='cat cat-superliga' href='https://www.prosport.ro/fotbal-intern/superliga'>Superliga</a>
        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        ts = ts_util.extract_timestamp_from_selector(soup, "div.display-flex.gap-5")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 10)
        self.assertEqual(ts.day, 30)
        self.assertEqual(ts.hour, 10)  # UTC conversion from 12:50 EEST
        self.assertEqual(ts.minute, 50)

    def test_gsp_data_autor(self):
        html = '''
        <p class="data-autor">
            Articol de <a rel="author" href="https://www.gsp.ro/autor/daniel-grigore-3879.html">Daniel Grigore</a>
            - Publicat joi, 30 octombrie 2025,  12:51 / Actualizat joi, 30 octombrie 2025, 12:52
        </p>
        '''
        soup = BeautifulSoup(html, "html.parser")
        ts = ts_util.extract_timestamp_from_selector(soup, "p.data-autor")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 10)
        self.assertEqual(ts.day, 30)
        self.assertEqual(ts.hour, 10)  # UTC conversion from 12:52 EEST
        self.assertEqual(ts.minute, 52)

    def test_sport_span_utc(self):
        html = '''
        <div class="sport-article-block__date">Data publicarii: <span
                                data-utc-date="2025-11-23 16:57:42"
                                data-date-format="{day} {Month} {year}, {hour}:{minute}"></span>
                        </div>
        '''
        soup = BeautifulSoup(html, "html.parser")
        ts = ts_util.extract_timestamp_from_selector(soup, "div.sport-article-block__date span[data-utc-date]")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 11)
        self.assertEqual(ts.day, 23)
        self.assertEqual(ts.hour, 14)  # UTC conversion from 12:52 EEST
        self.assertEqual(ts.minute, 57)

    def test_gsp_data_autor_original(self):
        html = '''
        <p class="data-autor">
            Articol de <a rel="author" href="https://www.gsp.ro/autor/mihai-sovei-4006.html">Mihai Șovei</a>
            - Publicat joi, 30 octombrie 2025,  15:55            / Actualizat joi, 30 octombrie 2025 15:55
            </p>
        '''

        soup = BeautifulSoup(html, "html.parser")
        ts = ts_util.extract_timestamp_from_selector(soup, "p.data-autor")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 10)
        self.assertEqual(ts.day, 30)
        self.assertEqual(ts.hour, 13)  # UTC conversion from 12:52 EEST
        self.assertEqual(ts.minute, 55)

    def test_get_fallback_date(self):
        result = ts_util.get_fallback_date("Irrelevant", return_both=True)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(dt, datetime) for dt in result))
        self.assertTrue(all(dt.tzinfo is not None for dt in result))

        single = ts_util.get_fallback_date("", return_both=False)
        self.assertIsInstance(single, datetime)
        self.assertTrue(single.tzinfo is not None)

    def test_get_local_utc_date_no_comma(self):
        text = "Actualizat joi, 30 octombrie 2025 09:41"
        import re
        match_updated = re.search(r"Actualizat\s+(?:\w+,)?\s*\d{1,2}\s+\w+\s+\d{4}[,]?\s*\d{2}:\d{2}", text)
        self.assertIsNotNone(match_updated)

        result = ts_util.get_local_utc_date(match=match_updated, return_both=True)
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0].year, 2025)
        self.assertEqual(result[0].month, 10)
        self.assertEqual(result[0].day, 30)
        self.assertEqual(result[0].hour, 9)
        self.assertEqual(result[0].minute, 41)
        self.assertTrue(result[1].tzinfo is not None)

    def test_get_local_utc_date(self):
        text = "Actualizat joi, 31 iulie 2023, 10:01"
        import re
        match_updated = re.search(r"Actualizat\s+(?:\w+,)?\s*\d{1,2}\s+\w+\s+\d{4}[,]?\s*\d{2}:\d{2}", text)
        self.assertIsNotNone(match_updated)

        result = ts_util.get_local_utc_date(match=match_updated, return_both=True)
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0].year, 2023)
        self.assertEqual(result[0].month, 7)
        self.assertEqual(result[0].day, 31)
        self.assertEqual(result[0].hour, 10)
        self.assertEqual(result[0].minute, 1)
        self.assertTrue(result[1].tzinfo is not None)


if __name__ == "__main__":
    unittest.main()
