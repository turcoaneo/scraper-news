import os

from app.config.loader import load_sites_from_config


def test_site_config_fields():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "app", "config", "sites_config.json")

    sites = load_sites_from_config(config_path)
    assert len(sites) == 4

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
        }
    }

    for site in sites:
        expected = expected_fields[site.name]
        assert site.base_url == expected["base_url"]
        assert site.title_strategy == expected["title_strategy"]
        assert site.title_attribute == expected["title_attribute"]
        assert isinstance(site.articles, set)
