import unittest

from bs4 import BeautifulSoup

from article_scraper import ArticleScraper


class TestArticleScraper(unittest.TestCase):
    def test_digisport_title(self):
        html = '<h1><span class="tag">Exclusiv</span> Daniel Pancu nu are dubii</h1>'
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title_naive(), "ExclusivDaniel Pancu nu are dubii")
        self.assertEqual(scraper.extract_title(), "Daniel Pancu nu are dubii")

    def test_gsp_title_with_multiple_tags(self):
        html = '''
        <h1>
            <span class="marcaj ">FOTO ȘI VIDEO EXCLUSIV</span>
            „Colosseumul” României e gata în proporție de 70%
        </h1>
        '''
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title_naive(), "„Colosseumul” României e gata în proporție de 70%")

    def test_title_without_span(self):
        html = '<h1>Un meci spectaculos în Liga 1</h1>'
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title_naive(), "Un meci spectaculos în Liga 1")
        self.assertEqual(scraper.extract_title(), "Un meci spectaculos în Liga 1")

    def test_custom_unwanted_tags(self):
        html = '<h1><span class="tag">Blah Blah</span> Titlu important</h1>'
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title(unwanted_tags=["Blah Blah"]), "Titlu important")


if __name__ == "__main__":
    unittest.main()
