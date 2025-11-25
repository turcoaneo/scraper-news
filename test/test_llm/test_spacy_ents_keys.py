import unittest
from service.util.spacy_ents_keys import SpacyEntsKeys, extract_keywords_from_summary


class TestSpacyEntsKeys(unittest.TestCase):
    def setUp(self):
        self.sample_summary = (
            "Simona Halep a câștigat turneul de la Madrid, dominând adversara cu un joc foarte agresiv."
        )

    def test_extract_keywords_from_summary_filters_stopwords(self):
        keywords = extract_keywords_from_summary(self.sample_summary)
        self.assertNotIn("foarte", keywords)
        self.assertNotIn("este", keywords)
        self.assertTrue(all(len(word) >= 5 for word in keywords))

    def test_extract_keywords_from_summary_returns_top_words(self):
        summary = "Rapid București a câștigat câștigat câștigat meciul meciul meciul pe stadionul Giulești."
        keywords = extract_keywords_from_summary(summary)
        self.assertEqual(keywords[0], "câștigat")
        self.assertIn("Giulești", keywords)

    def test_extract_spacy_integration(self):
        result = SpacyEntsKeys.extract_spacy(self.sample_summary)
        self.assertIn("entities", result)
        self.assertIn("keywords", result)
        self.assertIsInstance(result["entities"], list)
        self.assertIsInstance(result["keywords"], list)
        self.assertGreater(len(result["keywords"]), 0)


if __name__ == "__main__":
    unittest.main()
