import os
import threading
import unittest

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

from service.util.declension_util import DeclensionUtil
from service.util.path_util import get_project_root


class TestDeclensionUtil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # T5 model
        model_path = os.path.join(get_project_root(), "t5_decorator_model")
        tokenizer = T5Tokenizer.from_pretrained(model_path)
        model = T5ForConditionalGeneration.from_pretrained(model_path)
        model.eval()
        cls.model_and_tokenizer = (tokenizer, model)

    def test_basic_declension(self):
        self.assertEqual(DeclensionUtil.normalize("bucureștean", self.model_and_tokenizer), "bucureștean")
        self.assertEqual(DeclensionUtil.normalize("bucureștenilor", self.model_and_tokenizer), "bucureșteni")
        self.assertEqual(DeclensionUtil.normalize("bucureșteanului", self.model_and_tokenizer), "bucureștean")

    def test_phrase_level(self):
        self.assertEqual(DeclensionUtil.normalize("fotbaliștilor tineri", self.model_and_tokenizer),
                         "fotbaliști tineri")
        self.assertEqual(DeclensionUtil.normalize("echipelor locale", self.model_and_tokenizer), "echipe locale")

    def test_no_transformation(self):
        self.assertEqual(DeclensionUtil.normalize("echipa primăriei", self.model_and_tokenizer), "echipa primăriei")
        self.assertEqual(DeclensionUtil.normalize("echipei primăriei", self.model_and_tokenizer), "echipa primăriei")

    def test_multithreaded_normalize(self):
        inputs = ["copilului", "mamei", "fratelui", "fotbaliștilor tineri", "echipelor locale"]
        expected = ["copil", "mamă", "frate", "fotbaliști tineri", "echipe locale"]
        results = [None] * len(inputs)

        def worker(i):
            results[i] = DeclensionUtil.normalize(inputs[i], self.model_and_tokenizer)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(inputs))]
        for t in threads: t.start()
        for t in threads: t.join()

        for i in range(len(inputs)):
            self.assertEqual(results[i], expected[i])

    def test_fallback_declension(self):
        duplets = [
            ("Șucului", "Șucu"),
            ("Țiriacului", "Țiriac"),
            ("Ștefăneștii", "Ștefănești"),
            ("Țăranului", "Țăranu"),
            ("Soranei Cîrstea", "Sorana Cîrstea"),
        ]

        self.assertEqual(DeclensionUtil.fallback_declension("Șucului", duplets), "Șucu")
        self.assertEqual(DeclensionUtil.fallback_declension("Țiriacului", duplets), "Țiriac")
        self.assertEqual(DeclensionUtil.fallback_declension("Ștefăneștii", duplets), "Ștefănești")
        self.assertEqual(DeclensionUtil.fallback_declension("Țăranului", duplets), "Țăranu")
        self.assertEqual(DeclensionUtil.fallback_declension("Soranei Cîrstea", duplets), "Soranei Cîrstea")

        # Should not transform if not starting with Ș or Ț
        self.assertEqual(DeclensionUtil.fallback_declension("copilului", duplets), "copilului")

        # Should fallback to original if no match
        self.assertEqual(DeclensionUtil.fallback_declension("Șimonului", duplets), "Șimonului")


if __name__ == "__main__":
    unittest.main()
