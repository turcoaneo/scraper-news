import re
from typing import List, Dict
from collections import Counter

from service.util.declension_util import DeclensionUtil
from service.util.scrape_runner_util import ScrapeRunnerUtil
from service.util.spacy_ents_keys import extract_keywords_from_summary


def clean_summary_text(text: str) -> str:
    # Remove stray numbers after sentence punctuation or quotes
    text = re.sub(r'([.!?])\s*["“”\']?\d+\b', r'\1', text)
    # Remove trailing digits glued to words (but keep structured numbers like years or scores)
    text = re.sub(r'\b([A-Za-zĂÂÎȘȚăâîșț]+)\d+\b', r'\1', text)
    return text


def normalize_sentence(text: str) -> str:
    # unify 'este' → 'e'
    text = re.sub(r'\b[Ee]ste\b', 'e', text)
    return text


def merge_summaries_with_keywords(
    summaries: List[str],
    max_sentences: int = 3,
    overlap_threshold: int = 8
) -> str:
    if not summaries:
        return "No summaries"

    # Step 1: Clean and merge summaries
    cleaned_summaries = [clean_summary_text(s) for s in summaries]
    all_text = " ".join(cleaned_summaries)
    all_text = all_text.replace("[...]", ".").replace("....", ".")
    if not all_text.strip().endswith((".", "!", "?")):
        all_text += "."

    # Step 2: Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', all_text)

    # Step 3: Extract and normalize keywords
    keywords = extract_keywords_from_summary(all_text)
    tokenizer, model = ScrapeRunnerUtil.get_model_and_tokenizer()
    keywords = [DeclensionUtil.normalize(kw, (tokenizer, model)) for kw in keywords]

    # Step 4: Build dictionary {keyword: [sentences containing it]}
    keyword_sentences: Dict[str, List[str]] = {}
    for kw in keywords:
        kw_sentences = [s for s in sentences if kw.lower() in s.lower()]
        if kw_sentences:
            keyword_sentences[kw] = kw_sentences

    if not keyword_sentences:
        # fallback: just return first few sentences
        return " ".join(sentences[:max_sentences])

    # Step 5: Flat map all sentences across keywords
    all_keyword_sentences = [s for sent_list in keyword_sentences.values() for s in sent_list]

    # Step 6: Count frequency of each sentence
    sentence_counts = Counter(all_keyword_sentences)

    # Step 7: Sort sentences by frequency (desc), then by original order
    sorted_sentences = sorted(
        sentence_counts.keys(),
        key=lambda s: (-sentence_counts[s], sentences.index(s))
    )

    # Step 8: Deduplicate, normalize, remove similar sentences, and trim
    final_sentences: List[str] = []
    for s in sorted_sentences:
        s_norm = normalize_sentence(s)
        words = set(re.findall(r'\w+', s_norm.lower()))
        # Adaptive overlap threshold: min(8, half of sentence length)
        adaptive_threshold = min(overlap_threshold, max(2, len(words) // 2))
        too_similar = any(
            len(words & set(re.findall(r'\w+', normalize_sentence(prev).lower())))
            >= adaptive_threshold
            for prev in final_sentences
        )
        if too_similar:
            continue
        final_sentences.append(s_norm)
        if len(final_sentences) >= max_sentences:
            break

    # Hard cap length
    return " ".join(final_sentences[:max_sentences])
