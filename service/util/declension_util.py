# service/util/declension_util.py
import torch


class DeclensionUtil:

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
