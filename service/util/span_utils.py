# span_utils.py
from typing import List


class SpanUtils:
    @staticmethod
    def suppress_sub_spans(spans: List[str]) -> List[str]:
        return sorted(set([
            span for span in spans
            if not any(span != other and span in other for other in spans)
        ]))

    @staticmethod
    def group_labeled_phrases(
        word_ids: List[int],
        labels: List[str],
        words: List[str]
    ) -> dict:
        entities, keywords = [], []
        current_phrase = []
        current_type = None
        previous_word_id = None

        for word_id, label in zip(word_ids, labels):
            if word_id is None:
                continue

            word = words[word_id]

            if label in ["B-ENT", "B-KW"]:
                if current_type == label and previous_word_id is not None and word_id == previous_word_id + 1:
                    current_phrase.append(word)
                else:
                    if current_phrase and current_type:
                        phrase = " ".join(current_phrase)
                        if current_type == "B-ENT":
                            entities.append(phrase)
                        elif current_type == "B-KW":
                            keywords.append(phrase)
                    current_phrase = [word]
                    current_type = label
            else:
                if current_phrase and current_type:
                    phrase = " ".join(current_phrase)
                    if current_type == "B-ENT":
                        entities.append(phrase)
                    elif current_type == "B-KW":
                        keywords.append(phrase)
                current_phrase = []
                current_type = None

            previous_word_id = word_id

        if current_phrase and current_type:
            phrase = " ".join(current_phrase)
            if current_type == "B-ENT":
                entities.append(phrase)
            elif current_type == "B-KW":
                keywords.append(phrase)

        return {
            "entities": SpanUtils.suppress_sub_spans(entities),
            "keywords": SpanUtils.suppress_sub_spans(keywords)
        }
