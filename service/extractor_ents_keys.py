from typing import List, Dict

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

from service.util.spacy_ents_keys import SpacyEntsKeys
from service.util.span_utils import SpanUtils


class EntityKeywordExtractor:
    def __init__(
            self,
            model_path: str = None,
            use_torch_script: bool = False,
            tokenizer_path: str = None
    ):
        self.model_path = model_path
        self.use_torch_script = use_torch_script
        self.tokenizer_path = tokenizer_path or model_path

        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)

        if self.use_torch_script:
            self.model = torch.jit.load(model_path)
            self.id2label = {0: 'O', 1: 'B-ENT', 2: 'B-KW'}
        elif model_path:
            base_model = AutoModelForTokenClassification.from_pretrained(model_path)
            self.model = base_model
            self.id2label = base_model.config.id2label
        else:
            self.model = None
            self.id2label = {0: 'O', 1: 'B-ENT', 2: 'B-KW'}

    def extract_with_roberta(self, text: str) -> Dict[str, List[str]]:
        if not text or not self.model:
            return {"entities": [], "keywords": []}

        encoding, word_ids, words = SpacyEntsKeys.get_words_ids_encoding(text, self.tokenizer)

        with torch.no_grad():
            if self.use_torch_script:
                logits = self.model(encoding["input_ids"], encoding["attention_mask"])
            else:
                outputs = self.model(**encoding)
                logits = outputs.logits

        predictions = torch.argmax(logits, dim=-1)[0].tolist()
        labels = [self.id2label[p] for p in predictions]

        return SpanUtils.group_labeled_phrases(word_ids, labels, words)

    def print_extraction(self, text: str) -> None:
        result = self.extract_with_roberta(text)
        print("Entities:", result["entities"])
        print("Keywords:", result["keywords"])
