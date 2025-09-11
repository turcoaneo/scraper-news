class Article:
    def __init__(self, site, timestamp, title, entities, keywords, summary=None, url=None, comments=None):
        self.site = site
        self.timestamp = timestamp
        self.title = title
        self.entities = entities
        self.keywords = keywords
        self.summary = summary
        self.url = url
        self.comments = comments
        self.features: set = set()
        self.clustered: bool = False

    def __eq__(self, other):
        return isinstance(other, Article) and self.url == other.url

    def __hash__(self):
        return hash(self.url)
