import os
import threading
import unittest

import sentencepiece as spm
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

        # TorchScript + SentencePiece model
        sp_path = os.path.join(get_project_root(), "notebooks", "declension.model")
        pt_path = os.path.join(get_project_root(), "notebooks", "declension_sentencepiece.pt")

        cls.sp = spm.SentencePieceProcessor()
        cls.sp.load(sp_path)

        cls.scripted_model = torch.jit.load(pt_path)
        cls.scripted_model.eval()

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

    def test_long_input_truncation(self):
        long_text = " ".join(["copilului"] * 300)
        output = DeclensionUtil.predict(self.scripted_model, self.sp, long_text)
        self.assertTrue(len(output) > 0)  # Should not crash

    def test_mixed_case_and_punctuation(self):
        self.assertEqual(DeclensionUtil.predict(self.scripted_model, self.sp, "copilului"), "copil")
        self.assertEqual(DeclensionUtil.predict(self.scripted_model, self.sp, "mamei"), "mamă")
        self.assertNotEqual(DeclensionUtil.predict(self.scripted_model, self.sp, "Mamei,"), "mamă")

    def test_multithreaded_prediction(self):
        inputs = ["copilului", "mamei", "fratelui", "fotbaliștilor tineri", "echipelor locale"]
        expected = ["copil", "mamă", "frate", "fotbaliști tineri", "echipe locale"]
        results = [None] * len(inputs)

        def worker(i):
            results[i] = DeclensionUtil.predict(self.scripted_model, self.sp, inputs[i])

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(inputs))]
        for t in threads: t.start()
        for t in threads: t.join()

        for i in range(len(inputs)):
            self.assertEqual(results[i], expected[i])

    def test_multithreaded_normalize(self):
        inputs = ["copilului", "mamei", "fratelui", "fotbaliștilor tineri", "echipelor locale"]
        expected = ["copil", "mama", "frate", "fotbaliști tineri", "echipe locale"]
        results = [None] * len(inputs)

        def worker(i):
            results[i] = DeclensionUtil.normalize(inputs[i], self.model_and_tokenizer)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(len(inputs))]
        for t in threads: t.start()
        for t in threads: t.join()

        for i in range(len(inputs)):
            self.assertEqual(results[i], expected[i])


if __name__ == "__main__":
    unittest.main()
