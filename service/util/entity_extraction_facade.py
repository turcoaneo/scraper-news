# entity_extraction_facade.py

import os
import time
from typing import List, Dict

from model.model_type import ModelType
from service.claude_prompt_builder import ClaudePromptBuilder
from service.extractor_ents_keys import EntityKeywordExtractor
from service.gpt_prompt_builder import GptPromptBuilder
from service.util.spacy_ents_keys import SpacyEntsKeys


class EntityExtractorFacade:
    @staticmethod
    def extract_by_model(summary: str, model_type: ModelType, training_data: List[Dict]) -> Dict[str, List[str]]:
        start_time = time.time()

        if model_type == ModelType.CLAUDE:
            result = ClaudePromptBuilder(summary).extract_entities_and_keywords(training_data)

        elif model_type == ModelType.GPT:
            result = GptPromptBuilder(summary).extract_entities_and_keywords(training_data)

        elif model_type == ModelType.BERT:
            model_pt_path = os.path.join("..", "..", "model.pt")
            tokenizer_path = os.path.join("..", "..", "dumitrescustefan_token_output", "checkpoint-200")
            extractor = EntityKeywordExtractor(model_pt_path, use_torchscript=True, tokenizer_path=tokenizer_path)
            result = extractor.extract_with_roberta(summary)

        elif model_type == ModelType.SPACY:
            result = SpacyEntsKeys.extract_spacy(summary)

        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        elapsed = time.time() - start_time
        print(f"[{model_type.value.upper()}] Inference time: {elapsed:.3f}s")

        return result
