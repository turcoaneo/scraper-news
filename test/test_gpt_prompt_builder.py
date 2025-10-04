import json
import os
import tempfile
import unittest


from service.claude_prompt_builder import load_training_data
from service.gpt_prompt_builder import GptPromptBuilder


class TestGptPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.sample_summary = (
            "Echipa Rapid București a obținut o victorie dramatică împotriva CFR Cluj "
            "în semifinala Cupei României, disputată pe Stadionul Giulești."
        )
        self.sample_data = [
            {
                "summary": "FCSB a remizat cu Universitatea Craiova în etapa a 10-a din Superliga.",
                "expected_entities": ["FCSB", "Universitatea Craiova", "Superliga"],
                "expected_keywords": ["remiză", "etapa", "Superliga"]
            },
            {
                "summary": "Naționala României va juca împotriva Portugaliei în preliminariile Euro 2028.",
                "expected_entities": ["Naționala României", "Portugalia", "Euro 2028"],
                "expected_keywords": ["preliminarii", "meci", "Euro"]
            }
        ]
        self.builder = GptPromptBuilder(self.sample_summary)

    def test_build_prompt(self):
        prompt = self.builder.build_prompt(self.sample_data)
        self.assertIn("entities", prompt.lower())
        self.assertIn("keywords", prompt.lower())
        self.assertIn("Rapid București", prompt)

    def test_extract_entities_and_keywords(self):
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("OPENAI_API_KEY not set")

        result = self.builder.extract_entities_and_keywords(self.sample_data)

        self.assertIn("entities", result)
        self.assertIn("keywords", result)
        self.assertIsInstance(result["entities"], list)
        self.assertIsInstance(result["keywords"], list)

        expected_entities = ['Echipa Rapid București', 'CFR Cluj', 'semifinala Cupei României', 'Stadionul Giulești']
        expected_keywords = ['victorie dramatică', 'semifinala', 'Cupa României']

        for entity in expected_entities:
            self.assertIn(entity, result["entities"], f"Missing entity: {entity}")

        for keyword in expected_keywords:
            self.assertIn(keyword, result["keywords"], f"Missing keyword: {keyword}")

    def test_load_training_data(self):
        # noinspection DuplicatedCode
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            json.dump(self.sample_data, tmp)
            tmp_path = tmp.name

        data = load_training_data(tmp_path)
        self.assertEqual(data[0]["summary"], self.sample_data[0]["summary"])
        self.assertEqual(data[1]["expected_entities"][1], "Portugalia")


if __name__ == "__main__":
    unittest.main()
