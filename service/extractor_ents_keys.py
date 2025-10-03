import re
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from typing import List, Dict


def split_words(text: str) -> List[str]:
    return re.findall(r"\w+|\S", text)


class EntityKeywordExtractor:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.id2label = self.model.config.id2label

    def extract_with_roberta(self, text: str) -> Dict[str, List[str]]:
        words = split_words(text)
        encoding = self.tokenizer(
            words,
            is_split_into_words=True,
            return_tensors="pt",
            truncation=True
        )

        word_ids = encoding.word_ids(batch_index=0)
        with torch.no_grad():
            outputs = self.model(**encoding)

        predictions = torch.argmax(outputs.logits, dim=-1)[0].tolist()
        labels = [self.id2label[p] for p in predictions]

        entities, keywords = [], []
        current_words = []
        current_type = None
        previous_word_id = None

        for word_id, label in zip(word_ids, labels):
            if word_id is None:
                continue

            word = words[word_id]

            if label in ["B-ENT", "B-KW"]:
                if current_words and current_type:
                    phrase = " ".join(current_words)
                    if current_type == "B-ENT":
                        entities.append(phrase)
                    elif current_type == "B-KW":
                        keywords.append(phrase)
                current_words = [word]
                current_type = label
            elif label == current_type and word_id != previous_word_id:
                current_words.append(word)
            else:
                if current_words and current_type:
                    phrase = " ".join(current_words)
                    if current_type == "B-ENT":
                        entities.append(phrase)
                    elif current_type == "B-KW":
                        keywords.append(phrase)
                current_words = []
                current_type = None

            previous_word_id = word_id

        if current_words and current_type:
            phrase = " ".join(current_words)
            if current_type == "B-ENT":
                entities.append(phrase)
            elif current_type == "B-KW":
                keywords.append(phrase)

        return {
            "entities": sorted(set(entities)),
            "keywords": sorted(set(keywords))
        }

    def print_extraction(self, text: str) -> None:
        result = self.extract_with_roberta(text)
        print("Entities:", result["entities"])
        print("Keywords:", result["keywords"])