import json
import os
from typing import List, Dict
from dotenv import load_dotenv
import anthropic

load_dotenv()


class ClaudePromptBuilder:
    def __init__(self, summary: str):
        self.summary = summary
        self.claude = anthropic.Anthropic()
        self.model = "claude-3-5-sonnet-20240620"

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

    def send_prompt_to_claude(self, prompt: str) -> str:
        message = self.claude.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.5,
            system="Extract entities and keywords from Romanian sports summaries.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def extract_entities_and_keywords(self, training_data: List[Dict] = None) -> Dict[str, List[str]]:
        prompt = self.build_training_prompt(training_data) if training_data else self.build_inference_prompt()
        raw_output = self.send_prompt_to_claude(prompt)

        entities, keywords = [], []
        for line in raw_output.splitlines():
            if line.lower().startswith("entities:"):
                entities = [e.strip() for e in line.split(":", 1)[1].split(",") if e.strip()]
            elif line.lower().startswith("keywords:"):
                keywords = [k.strip() for k in line.split(":", 1)[1].split(",") if k.strip()]

        return {"entities": entities, "keywords": keywords}


def load_training_data(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)