# model_type.py
from enum import Enum


class ModelType(Enum):
    SPACY = "spacy"
    CLAUDE = "claude"
    GPT = "gpt"
    BERT = "bert"
