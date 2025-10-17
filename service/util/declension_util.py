# service/util/declension_util.py
import os
from functools import lru_cache

from transformers import T5Tokenizer, T5ForConditionalGeneration

from service.util.path_util import PROJECT_ROOT


class DeclensionUtil:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_model_and_tokenizer():
        model_path = os.path.abspath(os.path.join(PROJECT_ROOT, "t5_decorator_model"))
        tokenizer = T5Tokenizer.from_pretrained(model_path)
        model = T5ForConditionalGeneration.from_pretrained(model_path)
        model.eval()
        return tokenizer, model

    @staticmethod
    def normalize(text: str) -> str:
        tokenizer, model = DeclensionUtil.get_model_and_tokenizer()
        input_text = f"normalize: {text}"
        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        output_ids = model.generate(
            input_ids,
            max_length=32,
            num_beams=4,
            early_stopping=True,
            do_sample=False
        )
        return tokenizer.decode(output_ids[0], skip_special_tokens=True)
