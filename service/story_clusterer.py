from typing import List, Dict

from service.util.summary_util import merge_summaries


def _jaccard_similarity(set1, set2):
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) if union else 0.0


def _display_cluster_info(cluster):
    print("-" * 60)
    for article in cluster:
        print(f"📰 {article.title}")
        print(f"🔗 {article.url}")
        print(f"🔑 Keywords: {article.keywords}")
        print(f"🏷️ Entities: {article.entities}")
        print("-" * 60)


def _verify_cluster(article_i, article_j, cluster_id, clusters, threshold, component_type="features"):
    component_i = article_i.features
    component_j = article_j.features
    if component_type is not None and component_type == "title":
        component_i = set(article_i.title.split(" "))
        component_j = set(article_j.title.split(" "))

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
            clusters[cluster_id[0]] = {article_i, article_j}
            cluster_id[0] = cluster_id[0] + 1
        return True
    return False


class StoryClusterer:
    def __init__(self, site_scrapers, minutes=180, threshold_title=0.1, threshold_features=0.1):
        self.site_scrapers = site_scrapers
        self.threshold_title = threshold_title
        self.threshold_features = threshold_features
        for site in site_scrapers:
            site.load_recent_from_csv(minutes)
        self.clusters = dict()

    def cluster_stories(self):
        all_articles = []
        for scraper in self.site_scrapers:
            for article in scraper.articles:
                entities = article.entities if article.entities else []
                if isinstance(entities, str):
                    entities = [entities]
                keywords = article.keywords if article.keywords else []
                if isinstance(keywords, str):
                    keywords = [keywords]
                article.features = set(entities) | set(keywords)
                all_articles.append(article)

        article_array = list(all_articles)
        clusters = {}
        cluster_id = [0]
        visited = set()

        for i in range(len(article_array)):
            article_i = article_array[i]
            if article_i.clustered or article_i.site in visited:
                continue
            visited.add(article_i.site)
            for j in range(i + 1, len(article_array)):
                article_j = article_array[j]
                if article_i.url == article_j.url:
                    print(f"Shared article {article_i.url} on {article_i.site} - {article_j.site} skipped",
                          article_j.url, article_i.site, article_j.site)
                if article_j.clustered or article_j.site in visited:
                    continue
                is_clustered = _verify_cluster(article_i, article_j, cluster_id, clusters, self.threshold_title,
                                               "title")
                if not is_clustered:
                    is_clustered = _verify_cluster(article_i, article_j, cluster_id, clusters, self.threshold_features)
                if is_clustered:
                    article_i.clustered = True
                    article_j.clustered = True
                    visited.add(article_j.site)
            visited = set()
        self.clusters = clusters
        self.print_score_by_cluster()

    def score_clusters(self):
        # Build a lookup map from site name to weight
        site_weights = {scraper.name: scraper.weight for scraper in self.site_scrapers}

        scored = []
        for key, articles in self.clusters.items():
            score = sum(site_weights.get(article.site, 0.0) for article in articles)
            scored.append({
                "score": round(score, 3),
                "cluster": key,
                "articles": articles
            })

        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def print_score_by_cluster(self):
        clusters = self.score_clusters()
        for i, cluster in enumerate(clusters, 1):
            print(f"\n🧠 Cluster #{i} — Score: {cluster['score']}")

    def print_matched_clusters(self):
        print("\n🔍 Matched Clusters Across Multiple Sites")
        print("=" * 60)
        clusters = self.score_clusters()
        for i, scored_cluster in enumerate(clusters, 1):
            articles_cluster = self.clusters[i - 1]
            sites = {article.site for article in articles_cluster}
            if len(sites) < 2:
                continue  # Skip single-source clusters

            print(f"\n🧠 Cluster #{i} — Score: {scored_cluster['score']} — Sites: {', '.join(sites)}")
            _display_cluster_info(articles_cluster)

    def get_matched_clusters(self) -> List[Dict]:
        result = []
        clusters = self.score_clusters()
        for i, scored_cluster in enumerate(clusters, 1):
            articles_cluster = self.clusters[i - 1]
            sites = {article.site for article in articles_cluster}
            if len(sites) < 2:
                print(f"[SKIP] Cluster #{i} has only one site: {sites}")
                continue

            articles = []
            summaries = []
            for article in articles_cluster:
                entities = article.entities
                if isinstance(entities, str):
                    entities = [e.strip() for e in entities.split(",") if e.strip()]
                elif not isinstance(entities, list):
                    entities = []

                keywords = article.keywords
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(",") if k.strip()]
                elif not isinstance(keywords, list):
                    keywords = []

                articles.append({
                    "site": article.site,
                    "title": article.title,
                    "url": article.url,
                    "summary": article.summary,
                    "keywords": keywords,
                    "entities": entities
                })

                summaries.append(article.summary)

            result.append({
                "score": scored_cluster["score"],
                "summary": merge_summaries(summaries),
                "sites": sorted(sites),
                "articles": articles
            })

        return result
