import os
import unittest

from app.config.loader import load_sites_from_config


class TestSiteConfig(unittest.TestCase):
    def test_site_config_fields(self):
        # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # config_path = os.path.join(base_dir, "app", "config", "sites_config.json")
        # sites = load_sites_from_config(config_path)
        sites = load_sites_from_config()
        assert len(sites) == 5

        expected_fields = {
            "digisport": {
                "base_url": "https://www.digisport.ro",
                "title_strategy": "attribute",
                "title_attribute": "title"
            },
            "fanatik": {
                "base_url": "https://www.fanatik.ro",
                "title_strategy": "text",
                "title_attribute": None
            },
            "prosport": {
                "base_url": "https://www.prosport.ro",
                "title_strategy": "text",
                "title_attribute": None
            },
            "gsp": {
                "base_url": "https://www.gsp.ro",
                "title_strategy": "text",
                "title_attribute": None
            },
            "sport": {
                "base_url": "https://www.sport.ro",
                "title_strategy": "text",
                "title_attribute": None
            }
        }

        for site in sites:
            expected = expected_fields[site.name]
            assert site.base_url == expected["base_url"]
            assert site.title_strategy == expected["title_strategy"]
            assert site.title_attribute == expected["title_attribute"]
            assert isinstance(site.articles, set)


if __name__ == "__main__":
    unittest.main()
