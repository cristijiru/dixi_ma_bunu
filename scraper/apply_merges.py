"""Apply merge decisions and generate the final merged dataset."""

import json
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class MergedWord:
    """A word with multiple entries from different sources."""
    id: str
    canonical: str
    variants: list[str] = field(default_factory=list)
    entries: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class MergeApplier:
    """Applies merge decisions to create the final merged dataset."""

    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.entries: list[dict] = []
        self.decisions: dict = {}
        self.merged_words: list[MergedWord] = []

    def load_entries(self, filename: str = "dictionary.jsonl"):
        """Load all dictionary entries."""
        filepath = self.data_dir / filename
        self.entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.entries.append(json.loads(line))
        print(f"Loaded {len(self.entries)} entries")

    def load_decisions(self, filename: str = "merge_decisions.json"):
        """Load merge decisions."""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self.decisions = json.load(f)
            auto_count = len(self.decisions.get("auto", []))
            manual_count = len(self.decisions.get("manual", []))
            print(f"Loaded {auto_count} auto decisions, {manual_count} manual decisions")
        else:
            print("No decisions file found, will use auto-merge only")
            self.decisions = {"auto": [], "manual": []}

    def normalize_diacritics(self, word: str) -> str:
        """Normalize â/ã/ă variants."""
        w = word.lower()
        w = w.replace('ã', 'â')
        w = w.replace('ă', 'â')
        return w

    def build_merge_map(self) -> dict[str, str]:
        """Build a mapping from headword to canonical form."""
        merge_map = {}

        # Apply manual merge decisions
        for decision in self.decisions.get("manual", []):
            if decision.get("action") == "merge":
                canonical = decision["canonical"]
                for hw in decision["headwords"]:
                    merge_map[hw] = canonical

        return merge_map

    def apply_merges(self):
        """Apply all merges and create merged word groups."""
        merge_map = self.build_merge_map()

        # Group entries by their merge target
        # First, group by normalized diacritics (auto-merge)
        by_diacritic_norm = defaultdict(list)
        for entry in self.entries:
            hw = entry['headword']
            # Check if this headword has a manual merge decision
            if hw in merge_map:
                # Use the canonical from manual decision
                norm = self.normalize_diacritics(merge_map[hw])
            else:
                # Use diacritic normalization (auto-merge)
                norm = self.normalize_diacritics(hw)
            by_diacritic_norm[norm].append(entry)

        # Now apply manual merge decisions to combine groups
        # Build a map of which normalized forms should merge together
        group_merges = defaultdict(set)
        for decision in self.decisions.get("manual", []):
            if decision.get("action") == "merge":
                canonical = decision["canonical"]
                canonical_norm = self.normalize_diacritics(canonical)
                for hw in decision["headwords"]:
                    hw_norm = self.normalize_diacritics(hw)
                    group_merges[canonical_norm].add(hw_norm)

        # Merge groups that were marked for manual merging
        final_groups = {}
        merged_norms = set()

        for norm, entries in by_diacritic_norm.items():
            if norm in merged_norms:
                continue

            # Check if this norm should be merged with others
            all_entries = list(entries)
            all_norms = {norm}

            for canonical_norm, to_merge in group_merges.items():
                if norm in to_merge or norm == canonical_norm:
                    # Merge all related groups
                    for related_norm in to_merge:
                        if related_norm in by_diacritic_norm and related_norm not in merged_norms:
                            all_entries.extend(by_diacritic_norm[related_norm])
                            all_norms.add(related_norm)
                    if canonical_norm in by_diacritic_norm and canonical_norm not in merged_norms:
                        all_entries.extend(by_diacritic_norm[canonical_norm])
                        all_norms.add(canonical_norm)

            merged_norms.update(all_norms)
            # Use the lowest norm alphabetically as the key
            final_key = min(all_norms)
            final_groups[final_key] = all_entries

        # Create MergedWord objects
        word_id = 0
        for norm_key, entries in sorted(final_groups.items()):
            # Get all unique headwords
            headwords = sorted(set(e['headword'] for e in entries))

            # Pick canonical: prefer the one from merge decision, otherwise first alphabetically
            canonical = headwords[0]
            for decision in self.decisions.get("manual", []):
                if decision.get("action") == "merge":
                    if any(hw in headwords for hw in decision["headwords"]):
                        canonical = decision["canonical"]
                        break

            merged = MergedWord(
                id=f"word_{word_id:06d}",
                canonical=canonical,
                variants=headwords,
                entries=entries
            )
            self.merged_words.append(merged)
            word_id += 1

        print(f"Created {len(self.merged_words)} merged word groups")

    def export_jsonl(self, filename: str = "dictionary_merged.jsonl"):
        """Export merged words to JSONL."""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for word in self.merged_words:
                f.write(word.to_json() + '\n')
        print(f"Exported {len(self.merged_words)} merged words to {filepath}")

    def export_json(self, filename: str = "dictionary_merged.json"):
        """Export merged words to JSON with metadata."""
        filepath = self.data_dir / filename

        metadata = {
            "source": "dixionline.net",
            "source_url": "https://www.dixionline.net",
            "merged_at": datetime.now().astimezone().isoformat(),
            "total_words": len(self.merged_words),
            "total_entries": sum(len(w.entries) for w in self.merged_words),
            "description": "Merged Aromanian dictionary with grouped spelling variants"
        }

        output = {
            "metadata": metadata,
            "words": [w.to_dict() for w in self.merged_words]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Exported to {filepath}")

    def print_stats(self):
        """Print statistics about the merged dataset."""
        print("\n--- Merged Dataset Statistics ---")
        print(f"Total merged words: {len(self.merged_words)}")

        multi_entry = sum(1 for w in self.merged_words if len(w.entries) > 1)
        multi_variant = sum(1 for w in self.merged_words if len(w.variants) > 1)
        total_entries = sum(len(w.entries) for w in self.merged_words)

        print(f"Words with multiple entries: {multi_entry}")
        print(f"Words with spelling variants: {multi_variant}")
        print(f"Total entries (sum): {total_entries}")

        # Show some examples
        print("\n--- Sample merged words with multiple entries ---")
        samples = [w for w in self.merged_words if len(w.entries) > 1][:5]
        for w in samples:
            sources = set(e.get('source', 'unknown') for e in w.entries)
            print(f"  {w.canonical}: {len(w.entries)} entries, variants={w.variants}, sources={sources}")


def main():
    """Apply merges and generate final dataset."""
    applier = MergeApplier()
    applier.load_entries()
    applier.load_decisions()
    applier.apply_merges()
    applier.export_jsonl()
    applier.export_json()
    applier.print_stats()


if __name__ == "__main__":
    main()
