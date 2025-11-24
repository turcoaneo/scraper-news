import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from service.util import scraper_runner


class TestCooldownPersistence(unittest.TestCase):

    def setUp(self):
        # Create a temp directory and file path
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.tempfile_path = Path(self.tempdir.name) / "cooldown.json"

        # Patch COOLDOWN_FILE to point to our temp file (Path object!)
        patcher = patch.object(scraper_runner, "COOLDOWN_FILE", self.tempfile_path)
        self.addCleanup(patcher.stop)
        patcher.start()

        # Reset global state
        scraper_runner._last_scrape_times = {}

    def test_save_and_load_cooldowns(self):
        ts = datetime.now(timezone.utc).replace(microsecond=0)
        scraper_runner._last_scrape_times = {"sport": ts}

        scraper_runner.save_cooldowns()

        # Verify file contents
        with open(self.tempfile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["sport"], ts.isoformat())

        # Reset and reload
        scraper_runner._last_scrape_times = {}
        scraper_runner.load_cooldowns()
        self.assertEqual(scraper_runner._last_scrape_times["sport"], ts)

    def test_load_cooldowns_handles_invalid_json(self):
        # Write invalid JSON
        with open(self.tempfile_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        scraper_runner._last_scrape_times = {"dummy": datetime.now(timezone.utc)}
        scraper_runner.load_cooldowns()
        self.assertEqual(scraper_runner._last_scrape_times, {})


if __name__ == "__main__":
    unittest.main()
