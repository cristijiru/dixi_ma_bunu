"""Merge dictionary entries with similar headwords."""

import json
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from difflib import SequenceMatcher


@dataclass
class MergedWord:
    """A word with potentially multiple entries from different sources."""
    id: str
    canonical: str
    variants: list[str] = field(default_factory=list)
    entries: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class DictionaryMerger:
    """Merges dictionary entries based on spelling similarity."""

    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.entries: list[dict] = []
        self.merged_words: list[MergedWord] = []
        self.merge_decisions: dict = {"auto": [], "manual": []}
        self.review_candidates: list[dict] = []

    def load_entries(self, filename: str = "dictionary.jsonl"):
        """Load entries from JSONL file."""
        filepath = self.data_dir / filename
        self.entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.entries.append(json.loads(line))
        print(f"Loaded {len(self.entries)} entries")

    def normalize_diacritics(self, word: str) -> str:
        """Normalize only safe diacritical variants (â/ã)."""
        w = word.lower()
        # These are equivalent in Aromanian orthography
        w = w.replace('ã', 'â')  # Normalize to â
        return w

    def normalize_full(self, word: str) -> str:
        """Full normalization for fuzzy matching candidates."""
        w = word.lower()
        # Diacritics
        w = w.replace('ã', 'a').replace('â', 'a').replace('î', 'i')
        w = w.replace('ă', 'a').replace('ș', 's').replace('ț', 't')
        w = w.replace('ĭ', 'i')
        # Common consonant groups (for candidate detection only)
        w = w.replace('dh', 'd')
        w = w.replace('gh', 'g')
        w = w.replace('lj', 'l')
        w = w.replace('nj', 'n')
        w = w.replace('th', 't')
        w = w.replace('ch', 'k')
        w = w.replace('dz', 'z')
        return w

    def similarity(self, w1: str, w2: str) -> float:
        """Calculate similarity between two words."""
        return SequenceMatcher(None, w1, w2).ratio()

    def is_safe_diacritic_variant(self, hw1: str, hw2: str) -> bool:
        """Check if two headwords differ only by â/ã."""
        # Normalize both and compare
        norm1 = self.normalize_diacritics(hw1)
        norm2 = self.normalize_diacritics(hw2)
        return norm1 == norm2 and hw1.lower() != hw2.lower()

    def find_auto_merges(self) -> dict[str, list[dict]]:
        """Find entries that can be auto-merged (exact match or â/ã variant)."""
        # Group by normalized diacritics
        by_normalized = defaultdict(list)
        for entry in self.entries:
            norm = self.normalize_diacritics(entry['headword'])
            by_normalized[norm].append(entry)

        return dict(by_normalized)

    def find_fuzzy_candidates(self, threshold: float = 0.85) -> list[dict]:
        """Find entries that might be variants using fuzzy matching."""
        # Group by full normalization first (quick filter)
        by_full_norm = defaultdict(list)
        for entry in self.entries:
            norm = self.normalize_full(entry['headword'])
            by_full_norm[norm].append(entry)

        # Find groups where full normalization creates matches
        # but diacritic normalization doesn't (these need review)
        candidates = []

        for norm, entries in by_full_norm.items():
            if len(entries) < 2:
                continue

            # Get unique headwords
            headwords = list(set(e['headword'] for e in entries))
            if len(headwords) < 2:
                continue

            # Check if these are already covered by safe diacritic normalization
            diacritic_groups = defaultdict(list)
            for hw in headwords:
                diacritic_groups[self.normalize_diacritics(hw)].append(hw)

            # If all headwords normalize to the same diacritic form, skip (auto-merge handles it)
            if len(diacritic_groups) == 1:
                continue

            # These are fuzzy candidates needing review
            candidates.append({
                "normalized": norm,
                "headwords": sorted(headwords),
                "entries": entries,
                "similarity": self.similarity(headwords[0], headwords[1]) if len(headwords) == 2 else None
            })

        return candidates

    def run_auto_merge(self):
        """Perform auto-merges and identify review candidates."""
        print("Finding auto-merge groups...")
        auto_groups = self.find_auto_merges()

        print("Finding fuzzy match candidates for review...")
        self.review_candidates = self.find_fuzzy_candidates()

        # Build merged words from auto-merge groups
        word_id = 0
        for norm_key, entries in auto_groups.items():
            # Pick canonical form (prefer most common or first alphabetically)
            headwords = sorted(set(e['headword'] for e in entries))
            canonical = headwords[0]  # First alphabetically

            merged = MergedWord(
                id=f"word_{word_id:06d}",
                canonical=canonical,
                variants=headwords,
                entries=entries
            )
            self.merged_words.append(merged)
            word_id += 1

            # Record auto-merge decision
            if len(headwords) > 1:
                self.merge_decisions["auto"].append({
                    "canonical": canonical,
                    "variants": headwords,
                    "reason": "diacritic_variant"
                })

        print(f"Created {len(self.merged_words)} merged word groups")
        print(f"Found {len(self.review_candidates)} groups needing review")

        return self.review_candidates

    def save_review_candidates(self, filename: str = "merge_candidates.json"):
        """Save candidates needing review."""
        filepath = self.data_dir / filename

        # Simplify for review (don't include full entry data)
        simplified = []
        for c in self.review_candidates:
            simplified.append({
                "normalized": c["normalized"],
                "headwords": c["headwords"],
                "similarity": c["similarity"],
                "entry_count": len(c["entries"])
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(simplified, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(simplified)} candidates to {filepath}")

    def save_merge_decisions(self, filename: str = "merge_decisions.json"):
        """Save all merge decisions (auto + manual)."""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.merge_decisions, f, ensure_ascii=False, indent=2)
        print(f"Saved merge decisions to {filepath}")

    def export_merged(self, filename: str = "dictionary_merged.jsonl"):
        """Export merged words to JSONL."""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for word in self.merged_words:
                f.write(word.to_json() + '\n')
        print(f"Exported {len(self.merged_words)} merged words to {filepath}")


def main():
    """Run the merger and generate review candidates."""
    merger = DictionaryMerger()
    merger.load_entries()
    merger.run_auto_merge()
    merger.save_review_candidates()
    merger.save_merge_decisions()

    # Show some stats
    print("\n--- Statistics ---")
    total_entries = len(merger.entries)
    merged_groups = len(merger.merged_words)
    multi_entry = sum(1 for w in merger.merged_words if len(w.entries) > 1)
    multi_variant = sum(1 for w in merger.merged_words if len(w.variants) > 1)

    print(f"Total entries: {total_entries}")
    print(f"Merged word groups: {merged_groups}")
    print(f"Groups with multiple entries: {multi_entry}")
    print(f"Groups with spelling variants: {multi_variant}")
    print(f"Review candidates: {len(merger.review_candidates)}")


if __name__ == "__main__":
    main()
