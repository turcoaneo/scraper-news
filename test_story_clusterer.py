import unittest
from datetime import datetime, timezone

from article import Article
from story_clusterer import StoryClusterer


class MockScraper:
    def __init__(self, name, weight, articles):
        self.name = name
        self.weight = weight
        self.articles = articles

    def load_recent_from_csv(self, minutes):
        pass  # No-op for testing


class TestStoryClusterer(unittest.TestCase):
    now = datetime.now(timezone.utc)

    def test_story_clusterer(self):
        articles_site1 = [
            Article(
                "SiteA",
                self.now,
                "Lionel Messi joins Inter Miami",
                [],
                ["lionel", "messi", "miami", "transfer"],
                ["Lionel Messi", "Inter Miami"],
                "https://sitea.com/messi-miami"
            ),
            Article(
                "SiteA",
                self.now,
                "Cristiano Ronaldo scores again",
                [],
                ["ronaldo", "goal", "match"],
                ["Cristiano Ronaldo"],
                "https://sitea.com/ronaldo-goal"
            )
        ]

        articles_site2 = [
            Article(
                "SiteB",
                self.now,
                "Messi signs with Miami club",
                [],
                ["Lionel Messi", "Inter Miami"],
                ["messi", "miami", "contract"],
                "https://siteb.com/messi-signs"
            )
        ]

        scraper1 = MockScraper("SiteA", 0.6, articles_site1)
        scraper2 = MockScraper("SiteB", 0.4, articles_site2)

        clusterer = StoryClusterer([scraper1, scraper2], minutes=180)
        clusterer.cluster_stories()
        # clusterer.print_clusters()
        clusterer.print_matched_clusters()

    def setUp(self):
        self.articles_site1 = [
            Article(
                "SiteA",
                self.now,
                "Cristi Chivu la Inter Milano",
                [],
                ["Cristi Chivu", "Inter Milano"],
                ["transfer", "fotbal", "milano"],
                "https://sitea.com/chivu-inter"
            ),
            Article(
                "SiteA",
                self.now,
                "Gică Hagi revine în prim-plan",
                {},
                ["Gică Hagi"],
                ["revine", "antrenor", "fotbal"],
                "https://sitea.com/hagi-revine"
            )
        ]

        self.articles_site2 = [
            Article(
                "SiteB",
                self.now,
                "Cristi Chivu dorit de Inter",
                {},
                ["Cristi Chivu", "Inter Milano"],
                ["milano", "fotbal", "contract"],
                "https://siteb.com/chivu-dorit"
            )
        ]

        self.scraper1 = MockScraper("SiteA", 0.6, self.articles_site1)
        self.scraper2 = MockScraper("SiteB", 0.4, self.articles_site2)

        self.clusterer = StoryClusterer([self.scraper1, self.scraper2], 180, 0.4, 0.5)
        self.clusterer.cluster_stories()

    def test_cluster_stories(self):
        clusters = self.clusterer.clusters
        self.assertEqual(len(clusters), 1)  # One cluster for Chivu, none for Hagi
        chivu_cluster = clusters[0]
        titles = [article.title for article in chivu_cluster[0]]
        self.assertIn("Cristi Chivu la Inter Milano", titles)
        self.assertIn("Cristi Chivu dorit de Inter", titles)

    def test_score_clusters(self):
        scored = self.clusterer.score_clusters()
        self.assertEqual(len(scored), 1)
        scores = [cluster["score"] for cluster in scored]
        self.assertTrue(all(isinstance(score, float) for score in scores))
        self.assertAlmostEqual(scores[0], 1.0, places=2)  # 0.6 + 0.4 for Chivu cluster

    def test_entity_string_bug(self):
        buggy_article = Article(
            "BugSite",
            "Buggy Entity Article",
            "https://bugsite.com/buggy",
            "Cristi Chivu",  # ❌ Should be a list!
            ["fotbal", "Milano"]
        )

        scraper_bug = MockScraper("BugSite", 0.5, [buggy_article])
        clusterer_bug = StoryClusterer([scraper_bug], minutes=180)
        clusterer_bug.cluster_stories()

        cluster_set = self.clusterer.clusters[0][0]
        features = next(iter(cluster_set)).features
        # Expecting 'Cristi Chivu' as one entity, but instead we get individual letters
        self.assertNotIn("C", features)
        self.assertIn("Cristi Chivu", features)

    def test_entity_list_ok(self):
        good_article = Article(
            "GoodSite",
            "Proper Entity Article",
            "https://goodsite.com/proper",
            ["Cristi Chivu", "Inter Milano"],  # ✅ Correct format
            ["fotbal", "Milano"]
        )

        scraper_good = MockScraper("GoodSite", 0.5, [good_article])
        clusterer_good = StoryClusterer([scraper_good], minutes=180)
        clusterer_good.cluster_stories()

        cluster_set = self.clusterer.clusters[0][0]
        features = next(iter(cluster_set)).features
        self.assertIn("Cristi Chivu", features)
        self.assertIn("Inter Milano", features)
        self.assertNotIn("C", features)
        self.assertNotIn("I", features)


if __name__ == "__main__":
    unittest.main()
