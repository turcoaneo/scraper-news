import os
from pathlib import Path
from typing import Dict, List

import torch
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModelForTokenClassification

from app.utils.env_vars import HF_TOKEN, LLM_ROOT
from service.util.spacy_ents_keys import SpacyEntsKeys
from service.util.span_utils import SpanUtils


def resolve_model_path(model_path: str, hf_token: str = None) -> str:
    if LLM_ROOT == "local":
        return str(Path(model_path))  # Local absolute path
    else:
        filename = Path(model_path).name  # Extract "bert_model.pt"
        return hf_hub_download(
            repo_id=str(model_path),
            filename=filename,
            token=hf_token
        )


class EntityKeywordExtractor:
    def __init__(
            self,
            model_path: str = None,
            use_torch_script: bool = False,
            tokenizer_path: str = None,
            hf_token: str = None
    ):
        self.model_path = model_path
        self.use_torch_script = use_torch_script
        self.tokenizer_path = tokenizer_path or model_path
        self.hf_token = hf_token or HF_TOKEN

        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path, token=self.hf_token)

        if self.use_torch_script:
            model_file = resolve_model_path(self.model_path, self.hf_token)
            self.model = torch.jit.load(model_file)
            self.id2label = {0: 'O', 1: 'B-ENT', 2: 'B-KW'}
        elif model_path:
            base_model = AutoModelForTokenClassification.from_pretrained(model_path, token=self.hf_token)
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
