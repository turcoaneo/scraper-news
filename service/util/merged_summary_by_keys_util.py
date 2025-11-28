import re
from typing import List, Dict
from collections import Counter

from service.util.declension_util import DeclensionUtil
from service.util.scrape_runner_util import ScrapeRunnerUtil
from service.util.spacy_ents_keys import extract_keywords_from_summary


def merge_summaries_with_keywords(summaries: List[str], max_sentences: int = 3) -> str:
    if not summaries:
        return "No summaries"

    # Step 1: Merge summaries into one text
    all_text = " ".join(summaries)
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

    # Step 8: Deduplicate and trim to max_sentences
    final_sentences: List[str] = []
    seen = set()
    for s in sorted_sentences:
        if s not in seen:
            final_sentences.append(s)
            seen.add(s)
        if len(final_sentences) >= max_sentences:
            break

    return " ".join(final_sentences)
