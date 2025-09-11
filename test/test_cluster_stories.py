from datetime import datetime, timezone

from article import Article
from story_clusterer import StoryClusterer


class MockScraper:
    def __init__(self, name, weight, articles):
        self.name = name
        self.weight = weight
        self.articles = articles

    def load_recent_from_csv(self, minutes):
        pass  # no-op for testing


def test_cluster_stories_grouping():
    now = datetime.now(timezone.utc)

    arges_article_1 = Article(
        "digisport",
        now,
        "Pițurcă impresionat de Bogdan Andone",
        ["Bogdan Andone", "FC Argeș"],
        ["SuperLiga", "FC Argeș"],
        "",
        "https://a.com",
        0
    )

    arges_article_2 = Article(
        "gsp",
        now,
        "Bogdan Andone confirmă despărțirea",
        ["Bogdan Andone", "FC Argeș"],
        ["FC Argeș", "FCSB"],
        "",
        "https://b.com",
        0
    )

    craiova_article_1 = Article(
        "digisport",
        now,
        "Sancțiune istorică în România",
        ["Craiova"],
        ["FCU 1948 Craiova"],
        "",
        "https://c.com",
        0
    )

    craiova_article_2 = Article(
        "gsp",
        now,
        "Mititelu și FCU Craiova în Marca",
        ["FCU Craiova", "Adrian Mititelu", "Bănie", "Craiova"],
        ["FCU Craiova", "Marca"],
        "",
        "https://d.com",
        0
    )

    scraper1 = MockScraper("digisport", 1.0, [arges_article_1, craiova_article_1])
    scraper2 = MockScraper("gsp", 0.8, [arges_article_2, craiova_article_2])

    clusterer = StoryClusterer([scraper1, scraper2], 180, 0.05, 0.05)
    clusterer.cluster_stories()

    assert len(clusterer.clusters) == 2

    cluster_titles = [[a.title for a in cluster] for cluster in clusterer.clusters.values()]

    # Check that Argeș articles are clustered together
    assert any("Pițurcă" in t and "Andone" in t for t in cluster_titles[0] + cluster_titles[1])

    # Check that Craiova articles are clustered together
    assert any("Mititelu" in t and "Craiova" in t for t in cluster_titles[0] + cluster_titles[1])
