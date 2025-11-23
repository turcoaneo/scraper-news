import json
import re
from typing import List, Dict

import anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudePromptBuilder:
    def __init__(self, summary: str):
        self.summary = summary
        self.claude = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"

    def build_prompt(self, training_data: List[Dict]) -> str:
        prompt = "Please check these sample entities and keywords from Romanian sports summaries.\n\n"
        for item in training_data:
            prompt += f"Summary: {item['summary']}\n"
            prompt += f"Entities: {item['expected_entities']}\n"
            prompt += f"Keywords: {item['expected_keywords']}\n\n"
        prompt += (f"Now please analyze this summary and provide entities and keywords:\n"
                   f"Summary: {self.summary}\nEntities:\nKeywords:")
        return prompt

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

    def extract_entities_and_keywords(self, training_data: List[Dict]) -> Dict[str, List[str]]:
        prompt = self.build_prompt(training_data)
        raw_output = self.send_prompt_to_claude(prompt)

        # Normalize markdown and spacing without stripping punctuation
        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", raw_output)  # remove bold
        cleaned = re.sub(r"\s+", " ", cleaned)  # collapse whitespace

        # Match patterns like: Entities: ['Simona Halep', 'Madrid']
        entity_match = re.search(r"Entities:\s*\[([^\]]+)\]", cleaned)
        keyword_match = re.search(r"Keywords:\s*\[([^\]]+)\]", cleaned)

        entities = [e.strip().strip("'\"") for e in entity_match.group(1).split(",")] if entity_match else []
        keywords = [k.strip().strip("'\"") for k in keyword_match.group(1).split(",")] if keyword_match else []

        return {"entities": entities, "keywords": keywords}


def load_training_data(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8", newline="") as f:
        return json.load(f)
