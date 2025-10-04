import os
import json
import re
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GptPromptBuilder:
    def __init__(self, summary: str):
        self.summary = summary
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"

    def build_prompt(self, training_data: List[Dict]) -> str:
        prompt = (
            "Extract named entities and keywords from the following Romanian sports news summary.\n"
            "Only extract named entities such as people, organizations, teams, competitions, and locations. "
            "Do NOT include dates, weekdays, or generic terms.\n"
            "Extract relevant keywords that describe the themes, actions, or context of the summary. "
            "Avoid repeating named entities or generic filler words.\n\n"
        )
        for item in training_data:
            prompt += f"Summary: \"{item['summary']}\"\n"
            prompt += f"Entities: {item['expected_entities']}\n"
            prompt += f"Keywords: {item['expected_keywords']}\n\n"

        prompt += (
            f"Now analyze this summary and return a valid JSON object with two fields: \"entities\" and \"keywords\".\n"
            f"Each field should be a list of strings.\n\n"
            f"Summary: \"{self.summary}\"\n"
        )
        return prompt

    def send_prompt_to_gpt(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content

    def extract_entities_and_keywords(self, training_data: List[Dict]) -> Dict[str, List[str]]:
        prompt = self.build_prompt(training_data)
        raw_output = self.send_prompt_to_gpt(prompt)

        # Normalize markdown and spacing
        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", raw_output)
        cleaned = re.sub(r"\s+", " ", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            print(f"JSON decode error: {err}")
            print(f"Raw response: {cleaned}")
            return {"entities": [], "keywords": []}