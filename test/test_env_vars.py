# tests/test_env_vars.py

import unittest

from app.utils import env_vars


class TestEnvVars(unittest.TestCase):
    def test_app_env(self):
        self.assertIn(env_vars.APP_ENV, ["local", "docker", "uat"])

    def test_logging_debug_level(self):
        self.assertIsInstance(env_vars.LOG_LEVEL, str)

    def test_scraper_config(self):
        cfg = env_vars.SCRAPER_CONFIG
        self.assertIsInstance(cfg["looped"], bool)
        self.assertGreaterEqual(cfg["sleep_time"], 0)
        self.assertGreaterEqual(cfg["interval"], 0)
        self.assertGreaterEqual(cfg["article_time_cutoff"], 0)

    def test_filter_place_keys(self):
        keys = env_vars.FILTER_PLACE_KEYS
        for k in ["place", "including", "excluding"]:
            self.assertIn(k, keys)
            self.assertIsInstance(keys[k], list)


if __name__ == "__main__":
    unittest.main()
