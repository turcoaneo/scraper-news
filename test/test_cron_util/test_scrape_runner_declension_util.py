import unittest
from unittest.mock import patch, MagicMock

from service.util.scrape_runner_declension_util import ScrapeRunnerDeclensionUtil


class TestScrapeRunnerDeclensionUtil(unittest.TestCase):

    @patch("service.util.scrape_runner_declension_util.DeltaChecker.get_all_deltas")
    @patch("service.util.scrape_runner_declension_util.ScrapeRunnerUtil.get_model_and_tokenizer")
    def test_process_declension_phase_skips(self, mock_model, mock_deltas):
        mock_deltas.return_value = {"site": ({}, {"new": [], "updated": []})}
        result = ScrapeRunnerDeclensionUtil.process_declension_phase([MagicMock(name="site")])
        self.assertIsNone(result)

    @patch("service.util.scrape_runner_declension_util.DeltaChecker.get_all_deltas")
    @patch("service.util.scrape_runner_declension_util.ScrapeRunnerUtil.get_model_and_tokenizer")
    def test_process_declension_phase_runs(self, mock_model, mock_deltas):
        mock_deltas.return_value = {"site": ({}, {"new": [MagicMock()], "updated": []})}
        mock_model.return_value = ("tok", "mod")
        site = MagicMock()
        site.name = "site"
        site.model_type = "BERT"
        result = ScrapeRunnerDeclensionUtil.process_declension_phase([site])
        self.assertIsNotNone(result)
