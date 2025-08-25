def _jaccard_similarity(set1, set2):
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) if union else 0.0


def display_cluster_info(cluster):
    print("-" * 60)
    for article in cluster["articles"]:
        print(f"📰 {article['title']}")
        print(f"🔗 {article['url']}")
        print(f"🔑 Keywords: {', '.join(article['summary_keywords'])}")
        print(f"🏷️ Entities: {', '.join(article['entities'])}")
        print("-" * 60)


class StoryClusterer:
    def __init__(self, site_scrapers, minutes):
        self.site_scrapers = site_scrapers
        for site in site_scrapers:
            site.load_recent_from_csv(minutes)
        self.clusters = []

    def cluster_stories(self):
        all_articles = []
        for scraper in self.site_scrapers:
            for article in scraper.articles:
                entities = article.get("entities", [])
                if isinstance(entities, str):
                    entities = [entities]
                article["entities"] = set(entities)

                keywords = article.get("summary_keywords", [])
                if isinstance(keywords, str):
                    keywords = [keywords]
                article["summary_keywords"] = set(keywords)

                article["features"] = article["entities"] | article["summary_keywords"]
                all_articles.append(article)

        used = set()
        for i, a1 in enumerate(all_articles):
            if i in used:
                continue
            cluster = [a1]
            for j, a2 in enumerate(all_articles):
                if j != i and j not in used:
                    sim = _jaccard_similarity(a1["features"], a2["features"])
                    if sim > 0.3:
                        cluster.append(a2)
                        used.add(j)
            used.add(i)
            self.clusters.append(cluster)

    def score_clusters(self):
        scored = []
        for cluster in self.clusters:
            score = sum(
                next(scraper.weight for scraper in self.site_scrapers if scraper.name == article["site"])
                for article in cluster
            )
            scored.append({
                "score": round(score, 3),
                "articles": cluster
            })
        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def print_clusters(self):
        for i, cluster in enumerate(self.score_clusters(), 1):
            print(f"\n🧠 Cluster #{i} — Score: {cluster['score']}")
            display_cluster_info(cluster)

    def print_matched_clusters(self):
        print("\n🔍 Matched Clusters Across Multiple Sites")
        print("=" * 60)
        for i, cluster in enumerate(self.score_clusters(), 1):
            sites = {article["site"] for article in cluster["articles"]}
            if len(sites) < 2:
                continue  # Skip single-source clusters

            print(f"\n🧠 Cluster #{i} — Score: {cluster['score']} — Sites: {', '.join(sites)}")
            display_cluster_info(cluster)
