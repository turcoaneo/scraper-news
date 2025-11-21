class ClusterFilterUtil:

    @staticmethod
    def article_blob(article, places) -> str:
        """Concatenate all values from the given places into a lowercase string."""
        values = []
        for place in places:
            val = article.get(place, "")
            if isinstance(val, list):
                values.extend(val)
            elif isinstance(val, str):
                values.append(val)
        return " ".join(values).lower()

    @staticmethod
    def cluster_matches(cluster, places, including, excluding) -> bool:
        # Check exclusion first: if any article contains an excluded word, drop cluster
        for article in cluster["articles"]:
            blob = ClusterFilterUtil.article_blob(article, places)
            if any(word.lower() in blob for word in excluding):
                return False

        # If inclusion list is non-empty, require at least one article with an included word
        if including:
            for article in cluster["articles"]:
                blob = ClusterFilterUtil.article_blob(article, places)
                if any(word.lower() in blob for word in including):
                    return True
            return False  # no included word found

        # If no inclusion list, and no exclusion triggered, keep cluster
        return True

    @staticmethod
    def apply_filter(clusters, places, including, excluding):
        if not including and not excluding:
            return clusters
        return [
            c for c in clusters
            if ClusterFilterUtil.cluster_matches(c, places, including, excluding)
        ]