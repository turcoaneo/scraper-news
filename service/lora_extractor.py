import re
import torch
from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForTokenClassification
from peft import PeftModel

from service.util.spacy_ents_keys import SpacyEntsKeys
from service.util.span_utils import SpanUtils


class LoraEntityKeywordExtractor:
    def __init__(self, base_model_path: str, lora_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)

        base_model = AutoModelForTokenClassification.from_pretrained(
            base_model_path,
            num_labels=3,
            id2label={0: 'O', 1: 'B-ENT', 2: 'B-KW'},
            label2id={'O': 0, 'B-ENT': 1, 'B-KW': 2}
        )

        self.model = PeftModel.from_pretrained(base_model, lora_path)
        self.id2label = self.model.config.id2label

    def extract(self, text: str) -> Dict[str, List[str]]:
        if not text or not self.model:
            return {"entities": [], "keywords": []}

        encoding, word_ids, words = SpacyEntsKeys.get_words_ids_encoding(text, self.tokenizer)
        # words = re.findall(r"\w+|\S", text)
        # encoding = self.tokenizer(
        #     words,
        #     is_split_into_words=True,
        #     return_tensors="pt",
        #     truncation=True
        # )
        # word_ids = encoding.word_ids(batch_index=0)

        with torch.no_grad():
            outputs = self.model(**encoding)
            logits = outputs.logits

        predictions = torch.argmax(logits, dim=-1)[0].tolist()
        labels = [self.id2label[p] for p in predictions]

        return SpanUtils.group_labeled_phrases(word_ids, labels, words)