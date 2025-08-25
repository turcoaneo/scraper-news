import re

import spacy


def is_acronym(word):
    return re.fullmatch(r'[A-ZȘȚ]{2,}', word) is not None


class NamedEntity:
    def __init__(self):
        # Load spaCy Romanian model
        self.nlp = spacy.load("ro_core_news_sm")
        # Match capitalized words, optionally hyphenated or apostrophe-linked
        self.name_pattern = re.compile(
            r'\b-?[A-ZȘȚÎÂ][a-zșțăîâ]+\b'
        )

    def extract_entities(self, text):
        doc = self.nlp(text)
        candidates = self.name_pattern.findall(text)
        final_entities = []

        # Get sentence-initial words
        sentence_initials = {sent[0].text for sent in doc.sents if len(sent) > 0}

        for candidate in candidates:
            words = candidate.split()

            # Accept if all words are acronyms
            if all(is_acronym(word) for word in words):
                final_entities.append(candidate)
                continue

            # If first word is sentence-initial and not recognized by spaCy → discard
            valid_types = {"PER", "ORG", "LOC"}
            ents = doc.ents
            if words[0] in sentence_initials:
                if not any(ent.text == candidate and ent.label_ in valid_types for ent in ents):
                    continue

            final_entities.append(candidate)

        # Remove duplicates while preserving order
        seen = set()
        deduplicated_entities = []
        for entity in final_entities:
            if entity not in seen:
                deduplicated_entities.append(entity)
                seen.add(entity)

        return deduplicated_entities

    def extract_ents(self, text):
        doc = self.nlp(text)
        seen = set()
        deduplicated_entities = []
        valid_types = {"PERSON", "PER", "ORG", "ORGANIZATION", "LOC", "GPE", "EVENT", "FACILITY"}

        ents = doc.ents
        for entity in ents:
            label = entity.label_
            ent_text = entity.text.strip()
            if ent_text not in seen and label in valid_types:
                deduplicated_entities.append(ent_text)
                seen.add(ent_text)

        return deduplicated_entities

