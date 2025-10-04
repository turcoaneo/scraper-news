import re
from collections import Counter

from service.util.named_entity import NamedEntity

stopwords = {
    "asta", "ăsta", "acesta", "această", "există", "care", "pentru", "este", "și", "din", "cu", "sunt",
    "mai", "mult", "foarte", "fie", "cum", "dar", "nu", "în", "la", "de"
}


def extract_keywords_from_summary(summary):
    words = re.findall(r'\b\w{5,}\b', summary)
    filtered_words = [word for word in words if word not in stopwords]
    word_counts = Counter(filtered_words)
    most_common = [word for word, count in word_counts.most_common(10)]
    return most_common


class SpacyEntsKeys:
    @staticmethod
    def extract_spacy(summary):
        entities = NamedEntity().extract_entities(summary)
        keywords = extract_keywords_from_summary(summary)
        return {
            "entities": entities,
            "keywords": keywords
        }
