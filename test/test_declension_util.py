# tests/test_declension_util.py

import unittest

from service.util.declension_util import DeclensionUtil


class TestDeclensionUtil(unittest.TestCase):

    def test_basic_declension(self):
        self.assertEqual(DeclensionUtil.normalize("copilului"), "copil")
        self.assertEqual(DeclensionUtil.normalize("mamei"), "mama")
        self.assertEqual(DeclensionUtil.normalize("fratelui"), "frate")

    def test_phrase_level(self):
        self.assertEqual(DeclensionUtil.normalize("fotbaliștilor tineri"), "fotbaliști tineri")
        self.assertEqual(DeclensionUtil.normalize("echipelor locale"), "echipe locale")

    def test_no_transformation(self):
        self.assertEqual(DeclensionUtil.normalize("echipa primăriei"), "echipa primăriei")
        self.assertEqual(DeclensionUtil.normalize("echipei primăriei"), "echipa primăriei")


if __name__ == "__main__":
    unittest.main()
