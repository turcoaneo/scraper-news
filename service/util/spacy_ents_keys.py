import re
from collections import Counter

from service.util.named_entity import NamedEntity

stopwords = {
    "asta", "ăsta", "acesta", "această", "există", "care", "pentru", "este", "și", "din", "cu", "sunt",
    "mai", "mult", "foarte", "fie", "cum", "dar", "nu", "în", "la", "de", "de la", "lui", "care", "căreia", "căreia",
    "cărora", "cărora", "unui", "unei", "unuia", "uneia", "unora", "unor"
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

    @staticmethod
    def get_words_ids_encoding(text, tokenizer):
        words = re.findall(r"\w+|\S", text)
        encoding = tokenizer(
            words,
            is_split_into_words=True,
            return_tensors="pt",
            truncation=True
        )
        word_ids = encoding.word_ids(batch_index=0)
        return encoding, word_ids, words
