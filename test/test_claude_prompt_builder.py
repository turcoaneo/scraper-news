import os
import unittest

from dotenv import load_dotenv

from service.claude_prompt_builder import ClaudePromptBuilder, load_training_data

load_dotenv()


class TestClaudePromptBuilder(unittest.TestCase):
    def setUp(self):
        self.sample_summary = "Simona Halep a câștigat turneul de la Madrid."
        self.builder = ClaudePromptBuilder(self.sample_summary)
        self.sample_data = [
            {
                "summary": "FC Steaua a învins Dinamo pe Arena Națională.",
                "expected_entities": ["FC Steaua", "Dinamo", "Arena Națională"],
                "expected_keywords": ["învinge", "Arena Națională", "Dinamo"]
            }
        ]

    def test_load_training_data(self):
        import tempfile, json
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            json.dump(self.sample_data, tmp)
            tmp_path = tmp.name

        data = load_training_data(tmp_path)
        self.assertEqual(data[0]["summary"], self.sample_data[0]["summary"])

    def test_send_prompt_to_claude(self):
        if not os.getenv("ANTHROPIC_API_KEY"):
            self.skipTest("ANTHROPIC_API_KEY not set")

        prompt = self.builder.build_inference_prompt()
        response = self.builder.send_prompt_to_claude(prompt)
        self.assertIsInstance(response, str)
        self.assertIn("Entities", response)

    def test_extract_entities_and_keywords(self):
        if not os.getenv("ANTHROPIC_API_KEY"):
            self.skipTest("ANTHROPIC_API_KEY not set")

        result = self.builder.extract_entities_and_keywords(self.sample_data)
        self.assertIn("entities", result)
        self.assertIn("keywords", result)
        self.assertIsInstance(result["entities"], list)
        self.assertIsInstance(result["keywords"], list)


if __name__ == "__main__":
    unittest.main()
