# model_type.py
from enum import Enum


class ModelType(Enum):
    CLAUDE = "claude"
    GPT = "gpt"
    SPACY = "spacy"
    BERT = "bert"
    BERT_LORA = "bert_lora"
