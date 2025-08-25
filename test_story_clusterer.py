import unittest

from story_clusterer import StoryClusterer


class MockScraper:
    def __init__(self, name, weight, articles):
        self.name = name
        self.weight = weight
        self.articles = articles

    def load_recent_from_csv(self, minutes):
        pass  # No-op for testing


class TestStoryClusterer(unittest.TestCase):

    def test_story_clusterer(self):
        articles_site1 = [
            {
                "site": "SiteA",
                "title": "Lionel Messi joins Inter Miami",
                "url": "https://sitea.com/messi-miami",
                "summary_keywords": ["lionel", "messi", "miami", "transfer"],
                "entities": ["Lionel Messi", "Inter Miami"]
            },
            {
                "site": "SiteA",
                "title": "Cristiano Ronaldo scores again",
                "url": "https://sitea.com/ronaldo-goal",
                "summary_keywords": ["ronaldo", "goal", "match"],
                "entities": ["Cristiano Ronaldo"]
            }
        ]

        articles_site2 = [
            {
                "site": "SiteB",
                "title": "Messi signs with Miami club",
                "url": "https://siteb.com/messi-signs",
                "summary_keywords": ["messi", "miami", "contract"],
                "entities": ["Lionel Messi", "Inter Miami"]
            }
        ]

        scraper1 = MockScraper("SiteA", 0.6, articles_site1)
        scraper2 = MockScraper("SiteB", 0.4, articles_site2)

        clusterer = StoryClusterer([scraper1, scraper2], minutes=180)
        clusterer.cluster_stories()
        # clusterer.print_clusters()
        clusterer.print_matched_clusters()

    def setUp(self):
        self.articles_site1 = [
            {
                "site": "SiteA",
                "title": "Cristi Chivu la Inter Milano",
                "url": "https://sitea.com/chivu-inter",
                "entities": ["Cristi Chivu", "Inter Milano"],
                "summary_keywords": ["transfer", "fotbal", "milano"]
            },
            {
                "site": "SiteA",
                "title": "Gică Hagi revine în prim-plan",
                "url": "https://sitea.com/hagi-revine",
                "entities": ["Gică Hagi"],
                "summary_keywords": ["revine", "antrenor", "fotbal"]
            }
        ]

        self.articles_site2 = [
            {
                "site": "SiteB",
                "title": "Cristi Chivu dorit de Inter",
                "url": "https://siteb.com/chivu-dorit",
                "entities": ["Cristi Chivu", "Inter Milano"],
                "summary_keywords": ["milano", "fotbal", "contract"]
            }
        ]

        self.scraper1 = MockScraper("SiteA", 0.6, self.articles_site1)
        self.scraper2 = MockScraper("SiteB", 0.4, self.articles_site2)

        self.clusterer = StoryClusterer([self.scraper1, self.scraper2], minutes=180)
        self.clusterer.cluster_stories()

    def test_cluster_stories(self):
        clusters = self.clusterer.clusters
        self.assertEqual(len(clusters), 2)  # One cluster for Chivu, one for Hagi
        chivu_cluster = clusters[0]
        titles = [article["title"] for article in chivu_cluster]
        self.assertIn("Cristi Chivu la Inter Milano", titles)
        self.assertIn("Cristi Chivu dorit de Inter", titles)

    def test_score_clusters(self):
        scored = self.clusterer.score_clusters()
        self.assertEqual(len(scored), 2)
        scores = [cluster["score"] for cluster in scored]
        self.assertTrue(all(isinstance(score, float) for score in scores))
        self.assertAlmostEqual(scores[0], 1.0, places=2)  # 0.6 + 0.4 for Chivu cluster

    def test_entity_string_bug(self):
        buggy_article = {
            "site": "BugSite",
            "title": "Buggy Entity Article",
            "url": "https://bugsite.com/buggy",
            "entities": "Cristi Chivu",  # ❌ Should be a list!
            "summary_keywords": ["fotbal", "Milano"]
        }

        scraper_bug = MockScraper("BugSite", 0.5, [buggy_article])
        clusterer_bug = StoryClusterer([scraper_bug], minutes=180)
        clusterer_bug.cluster_stories()

        features = clusterer_bug.clusters[0][0]["features"]
        # Expecting 'Cristi Chivu' as one entity, but instead we get individual letters
        self.assertNotIn("C", features)
        self.assertIn("Cristi Chivu", features)

    def test_entity_list_ok(self):
        good_article = {
            "site": "GoodSite",
            "title": "Proper Entity Article",
            "url": "https://goodsite.com/proper",
            "entities": ["Cristi Chivu", "Inter Milano"],  # ✅ Correct format
            "summary_keywords": ["fotbal", "Milano"]
        }

        scraper_good = MockScraper("GoodSite", 0.5, [good_article])
        clusterer_good = StoryClusterer([scraper_good], minutes=180)
        clusterer_good.cluster_stories()

        features = clusterer_good.clusters[0][0]["features"]
        self.assertIn("Cristi Chivu", features)
        self.assertIn("Inter Milano", features)
        self.assertNotIn("C", features)
        self.assertNotIn("I", features)


if __name__ == "__main__":
    unittest.main()
