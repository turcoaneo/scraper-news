import json
from typing import List, Dict


class ClaudePromptBuilder:
    def __init__(self, summary: str):
        self.summary = summary

    def build_training_prompt(self, training_data: List[Dict]) -> str:
        prompt = "Extract entities and keywords from Romanian sports summaries.\n\n"
        for item in training_data:
            prompt += f"Summary: {item['summary']}\n"
            prompt += f"Entities: {item['expected_entities']}\n"
            prompt += f"Keywords: {item['expected_keywords']}\n\n"
        prompt += f"Now analyze this summary:\nSummary: {self.summary}\nEntities:"
        return prompt

    def build_inference_prompt(self) -> str:
        return f"""Extract entities and keywords from this Romanian sports summary:
Summary: {self.summary}
Entities:"""


def load_training_data(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
