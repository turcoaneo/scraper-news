from typing import List

import torch.nn.functional as funk


class DeclensionNormalizer:
    def __init__(self, canonical_forms: List[str], embed_fn):
        self.canonical_forms = canonical_forms
        self.embed_fn = embed_fn
        self.embedded_forms = {
            form: embed_fn(form) for form in canonical_forms
        }

    def normalize(self, mention: str) -> str:
        mention_vec = self.embed_fn(mention)
        scores = {
            form: funk.cosine_similarity(mention_vec, vec).item()
            for form, vec in self.embedded_forms.items()
        }
        best_match, best_score = max(scores.items(), key=lambda x: x[1])
        return best_match if best_score > 0.6 else mention  # threshold can be tuned
