def _normalize_list(value):
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    elif isinstance(value, list):
        return [v.strip() for v in value if isinstance(v, str) and v.strip()]
    return []


class Article:
    def __init__(self, site, timestamp, title, entities, keywords, summary=None, url=None, comments=None):
        self.site = site
        self.timestamp = timestamp
        self.title = title
        self.entities = _normalize_list(entities)
        self.keywords = _normalize_list(keywords)
        self.summary = summary
        self.url = url
        self.comments = comments
        self.features: set = set()
        self.clustered: bool = False

    def __eq__(self, other):
        return isinstance(other, Article) and self.url == other.url

    def __hash__(self):
        return hash(self.url)
