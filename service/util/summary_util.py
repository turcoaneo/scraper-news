import re
from collections import Counter
from typing import List


def merge_summaries(summaries: List[str], max_sentences: int = 3) -> str:
    if len(summaries) < 1:
        return "No summaries"
    all_text = " ".join(summaries)

    # Normalize noisy delimiters
    all_text = all_text.replace("[...]", ".")
    all_text = all_text.replace("....", ".")
    if not all_text.strip().endswith((".", "!", "?")):
        all_text += "."

    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', all_text)

    # Score sentences by word frequency
    words = re.findall(r'\w+', all_text.lower())
    word_freq = Counter(words)

    def score(sentence: str) -> int:
        return sum(word_freq.get(word.lower(), 0) for word in re.findall(r'\w+', sentence))

    top_sentences = sorted(sentences, key=score, reverse=True)[:max_sentences]
    return " ".join(top_sentences)
