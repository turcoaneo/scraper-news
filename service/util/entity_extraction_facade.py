# entity_extraction_facade.py
from typing import List, Dict

from model.model_type import ModelType
from service.claude_prompt_builder import ClaudePromptBuilder
from service.extractor_ents_keys import EntityKeywordExtractor
from service.gpt_prompt_builder import GptPromptBuilder
from service.util.spacy_ents_keys import SpacyEntsKeys


class EntityExtractorFacade:
    @staticmethod
    def extract_by_model(summary: str, model_type: ModelType, training_data: List[Dict]) -> Dict[str, List[str]]:
        if model_type == ModelType.CLAUDE:
            return ClaudePromptBuilder(summary).extract_entities_and_keywords(training_data)
        elif model_type == ModelType.GPT:
            return GptPromptBuilder(summary).extract_entities_and_keywords(training_data)
        elif model_type == ModelType.BERT:
            return EntityKeywordExtractor().extract_with_roberta(summary)
        elif model_type == ModelType.SPACY:
            return SpacyEntsKeys.extract_spacy(summary)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
