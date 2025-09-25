import unittest
from service.claude_prompt_builder import ClaudePromptBuilder, load_training_data


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

    def test_build_training_prompt(self):
        prompt = self.builder.build_training_prompt(self.sample_data)
        self.assertIn("FC Steaua", prompt)
        self.assertIn("Entities:", prompt)
        self.assertIn("Keywords:", prompt)

    def test_build_inference_prompt(self):
        prompt = self.builder.build_inference_prompt()
        self.assertIn("Simona Halep", prompt)
        self.assertTrue(prompt.startswith("Extract entities"))

    def test_load_training_data(self):
        # Create a temporary JSON file for testing
        import tempfile
        import json
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            json.dump(self.sample_data, tmp)
            tmp_path = tmp.name

        data = load_training_data(tmp_path)
        self.assertEqual(data[0]["summary"], self.sample_data[0]["summary"])
        self.assertIn("expected_entities", data[0])
        self.assertIn("expected_keywords", data[0])


if __name__ == "__main__":
    unittest.main()