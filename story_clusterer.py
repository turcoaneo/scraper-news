def _jaccard_similarity(set1, set2):
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) if union else 0.0


def _display_cluster_info(cluster):
    print("-" * 60)
    for article in cluster["articles"][0]:
        print(f"📰 {article.title}")
        print(f"🔗 {article.url}")
        print(f"🔑 Keywords: {', '.join(article.keywords)}")
        print(f"🏷️ Entities: {', '.join(article.entities)}")
        print("-" * 60)


def _verify_cluster(article_i, article_j, cluster_id, clusters, threshold, component_type="features"):
    component_i = article_i.features
    component_j = article_j.features
    if component_type is not None and component_type == "title":
        component_i = set(article_i.title.split(" "))
        component_j = set(article_j.title.split(" "))

    # intersection = component_i & component_j
    # union = component_i | component_j
    # jaccard = len(intersection) / len(union) if union else 0
    jaccard = _jaccard_similarity(component_i, component_j)
    if jaccard >= threshold:  # Threshold can be tuned
        # Check if either article is already in a cluster
        for cid, members in clusters.items():
            if article_i in members:
                clusters[cid].update([article_j])
                break
            elif article_j in members:
                clusters[cid].update([article_i])
                break
        else:
            clusters[cluster_id] = {article_i, article_j}
            cluster_id += 1
        return True
    return False


class StoryClusterer:
    def __init__(self, site_scrapers, minutes=180, threshold_title=0.1, threshold_features=0.1):
        self.site_scrapers = site_scrapers
        self.threshold_title = threshold_title
        self.threshold_features = threshold_features
        for site in site_scrapers:
            site.load_recent_from_csv(minutes)
        self.clusters = []

    def cluster_stories(self):
        all_articles = []
        for scraper in self.site_scrapers:
            for article in scraper.articles:
                entities = list(article.entities) if article.entities else []
                if isinstance(entities, str):
                    entities = [entities]
                keywords = list(article.keywords) if article.keywords else []
                if isinstance(keywords, str):
                    keywords = [keywords]
                article.features = set(entities) | set(keywords)
                all_articles.append(article)

        article_array = list(all_articles)
        clusters = {}
        cluster_id = 0

        for i in range(len(article_array)):
            article_i = article_array[i]
            if article_i.clustered:
                continue
            for j in range(i + 1, len(article_array)):
                article_j = article_array[j]
                if article_j.clustered:
                    continue
                is_clustered = _verify_cluster(article_i, article_j, cluster_id, clusters, self.threshold_title, "title")
                if not is_clustered:
                    is_clustered = _verify_cluster(article_i, article_j, cluster_id, clusters, self.threshold_features)
                if is_clustered:
                    article_i.clustered = True
                    article_j.clustered = True
        self.clusters.append(clusters)

    def score_clusters(self):
        scored = []
        for cluster in self.clusters:
            score = sum(
                next(scraper.weight for scraper in self.site_scrapers if scraper.name == article.site)
                for article in cluster[0]
            )
            scored.append({
                "score": round(score, 3),
                "articles": cluster
            })
        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def print_clusters(self):
        for i, cluster in enumerate(self.score_clusters(), 1):
            print(f"\n🧠 Cluster #{i} — Score: {cluster['score']}")
            _display_cluster_info(cluster)

    def print_matched_clusters(self):
        print("\n🔍 Matched Clusters Across Multiple Sites")
        print("=" * 60)
        for i, cluster in enumerate(self.score_clusters(), 1):
            sites = {article.site for article in cluster["articles"][0]}
            if len(sites) < 2:
                continue  # Skip single-source clusters

            print(f"\n🧠 Cluster #{i} — Score: {cluster['score']} — Sites: {', '.join(sites)}")
            _display_cluster_info(cluster)
