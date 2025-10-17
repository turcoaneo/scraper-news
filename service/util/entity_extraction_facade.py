# entity_extraction_facade.py

import os
import time
from functools import lru_cache
from typing import List, Dict

from model.model_type import ModelType
from service.claude_prompt_builder import ClaudePromptBuilder
from service.extractor_ents_keys import EntityKeywordExtractor
from service.gpt_prompt_builder import GptPromptBuilder
from service.lora_extractor import LoraEntityKeywordExtractor
from service.util.path_util import PROJECT_ROOT, BERT_MODEL_PATH, BERT_MODEL_PT_PATH
from service.util.spacy_ents_keys import SpacyEntsKeys


class EntityExtractorFacade:

    @staticmethod
    @lru_cache(maxsize=2)
    def get_lora_extractor() -> LoraEntityKeywordExtractor:
        base_model_path = BERT_MODEL_PATH
        lora_path = os.path.abspath(os.path.join(PROJECT_ROOT, "declension_lora"))
        return LoraEntityKeywordExtractor(base_model_path, lora_path)

    @staticmethod
    @lru_cache(maxsize=2)
    def get_bert_extractor() -> EntityKeywordExtractor:
        model_pt_path = BERT_MODEL_PT_PATH
        tokenizer_path = BERT_MODEL_PATH
        return EntityKeywordExtractor(model_pt_path, use_torchscript=True, tokenizer_path=tokenizer_path)

    @staticmethod
    def extract_by_model(summary: str, model_type: ModelType, training_data: List[Dict]) -> Dict[str, List[str]]:
        start_time = time.time()

        if model_type == ModelType.CLAUDE:
            result = ClaudePromptBuilder(summary).extract_entities_and_keywords(training_data)

        elif model_type == ModelType.GPT:
            result = GptPromptBuilder(summary).extract_entities_and_keywords(training_data)

        elif model_type == ModelType.BERT:
            raw_result = EntityExtractorFacade.get_bert_extractor().extract_with_roberta(summary)
            from service.util.declension_util import DeclensionUtil
            result = {
                "entities": [DeclensionUtil.normalize(ent) for ent in raw_result.get("entities", [])],
                "keywords": [DeclensionUtil.normalize(kw) for kw in raw_result.get("keywords", [])]
            }

        elif model_type == ModelType.BERT_LORA:
            result = EntityExtractorFacade.get_lora_extractor().extract(summary)

        elif model_type == ModelType.SPACY:
            result = SpacyEntsKeys.extract_spacy(summary)

        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        elapsed = time.time() - start_time
        print(f"[{model_type.value.upper()}] Inference time: {elapsed:.3f}s")

        return result
