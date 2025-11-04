# service/util/declension_util.py
import torch
from storage.duplets_dictionary import duplets, new_duplets


class DeclensionUtil:

    @staticmethod
    def fallback_declension(text: str, p_duplets: list) -> str:
        if not text or text[0] not in {"Ș", "Ț"}:
            return text

        for declined, base in p_duplets:
            if text == declined:
                return base
        return text  # fallback to original if no match

    @staticmethod
    def predict(model, sp, text):
        # Encode input text to token IDs
        input_ids = torch.tensor(sp.encode(text, out_type=int)).unsqueeze(0)

        # Get max positional index from model
        max_pos = model.positional.num_embeddings

        # Warn and truncate if input is too long
        if input_ids.size(1) > max_pos:
            print(f"[Warning] Truncating input: {text[:50]}... → {input_ids.size(1)} tokens > max {max_pos}")
            input_ids = input_ids[:, :max_pos]

        # Move to model's device
        input_ids = input_ids.to(next(model.parameters()).device)

        # Run inference
        with torch.no_grad():
            logits = model(input_ids)
            output_ids = torch.argmax(logits, dim=-1)

        # Decode output token IDs to text
        return sp.decode(output_ids[0].tolist())

    @staticmethod
    def normalize(text: str, model_and_tokenizer) -> str:
        if "Ș" in text or "Ț" in text:
            return DeclensionUtil.fallback_declension(text, p_duplets=new_duplets + duplets)
        tokenizer, model = model_and_tokenizer
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
