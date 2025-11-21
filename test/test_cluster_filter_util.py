import unittest
from service.util.cluster_filter_util import ClusterFilterUtil


class TestClusterFilterUtil(unittest.TestCase):

    def setUp(self):
        self.sample_clusters = [
            {
                "summary": "Cluster 1",
                "articles": [
                    {
                        "title": "Tenisul românesc revine",
                        "url": "https://example.com/tenis",
                        "keywords": ["sport", "tenis"],
                        "entities": ["Simona Halep"],
                        "summary": "Un articol despre tenis",
                        "site": "gsp"
                    },
                    {
                        "title": "Snooker în România",
                        "url": "https://example.com/snooker",
                        "keywords": ["snooker", "campionat"],
                        "entities": ["Ronnie O'Sullivan"],
                        "summary": "Snooker revine în București",
                        "site": "digisport"
                    }
                ]
            },
            {
                "summary": "Cluster 2",
                "articles": [
                    {
                        "title": "Becali face declarații",
                        "url": "https://example.com/becali",
                        "keywords": ["fotbal", "Superliga"],
                        "entities": ["Gigi Becali"],
                        "summary": "Declarații controversate",
                        "site": "fanatik"
                    }
                ]
            },
            {
                "summary": "Cluster 3",
                "articles": [
                    {
                        "site": "digisport",
                        "title": "Turcii au publicat declarațiile lui Șumudică, după tragerea la sorți.",
                        "url": "https://www.digisport.ro/turcii",
                        "keywords": [
                            "evolua",
                            "semifinala barajului"
                        ],
                        "entities": [
                            "Cupa Mondială 2026",
                            "România",
                            "Turciei"
                        ]
                    },
                    {
                        "site": "gsp",
                        "title": "Fostul atacant al lui Galatasaray merge pe mâna României în barajul cu Turcia",
                        "url": "https://www.gsp.ro/fotbal/nationala",
                        "keywords": [
                            "barajul",
                            "evolua",
                            "finală",
                            "manșă unică",
                            "semifinala",
                            "învingătoarea"
                        ],
                        "entities": [
                            "Cupa Mondială din 2026",
                            "Kosovo",
                            "Naționala României",
                            "România",
                            "Slovacia",
                            "Turcia",
                            "Turciei"
                        ]
                    }
                ]
            }
        ]

    def test_no_filters_returns_all(self):
        result = ClusterFilterUtil.apply_filter(
            self.sample_clusters,
            places=["title", "keywords", "entities", "summary"],
            including=[],
            excluding=[]
        )
        self.assertEqual(len(result), 3)

    def test_excluding_removes_matching_cluster(self):
        result = ClusterFilterUtil.apply_filter(
            self.sample_clusters,
            places=["title", "keywords", "entities", "summary"],
            including=[],
            excluding=["snooker", "turcii"]
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["summary"], "Cluster 2")

    def test_including_only_keeps_matching_cluster(self):
        result = ClusterFilterUtil.apply_filter(
            self.sample_clusters,
            places=["title", "keywords", "entities", "summary"],
            including=["snooker"],
            excluding=[]
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["summary"], "Cluster 1")

    def test_including_and_excluding_combined(self):
        result = ClusterFilterUtil.apply_filter(
            self.sample_clusters,
            places=["title", "keywords", "entities", "summary"],
            including=["tenis", "snooker"],
            excluding=["becali"]
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["summary"], "Cluster 1")

    def test_no_matching_articles_returns_empty(self):
        result = ClusterFilterUtil.apply_filter(
            self.sample_clusters,
            places=["title", "keywords", "entities", "summary"],
            including=["handbal"],
            excluding=["video"]
        )
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
