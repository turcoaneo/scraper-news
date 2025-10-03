import re
from typing import Dict, List

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

from service.util.span_utils import SpanUtils


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

        return SpanUtils.group_labeled_phrases(word_ids, labels, words)

    def print_extraction(self, text: str) -> None:
        result = self.extract_with_roberta(text)
        print("Entities:", result["entities"])
        print("Keywords:", result["keywords"])
