"""Interactive CLI tool for reviewing merge candidates."""

import json
import sys
from pathlib import Path
from typing import Optional


class MergeReviewer:
    """Interactive CLI for reviewing dictionary merge candidates."""

    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)
        self.candidates: list[dict] = []
        self.entries_by_headword: dict[str, list[dict]] = {}
        self.decisions: dict = {"manual": []}
        self.current_index: int = 0

    def load_candidates(self, filename: str = "merge_candidates.json"):
        """Load merge candidates."""
        filepath = self.data_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            self.candidates = json.load(f)
        print(f"Loaded {len(self.candidates)} candidates for review")

    def load_entries(self, filename: str = "dictionary.jsonl"):
        """Load entries and index by headword."""
        filepath = self.data_dir / filename
        self.entries_by_headword = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    hw = entry['headword']
                    if hw not in self.entries_by_headword:
                        self.entries_by_headword[hw] = []
                    self.entries_by_headword[hw].append(entry)
        print(f"Indexed {len(self.entries_by_headword)} unique headwords")

    def load_existing_decisions(self, filename: str = "merge_decisions.json"):
        """Load existing decisions to resume."""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.decisions = data
                # Find where to resume
                reviewed = set()
                for d in data.get("manual", []):
                    for hw in d.get("headwords", []):
                        reviewed.add(hw)

                # Find first unreviewed candidate
                for i, c in enumerate(self.candidates):
                    if not any(hw in reviewed for hw in c["headwords"]):
                        self.current_index = i
                        break
                else:
                    self.current_index = len(self.candidates)

                print(f"Resuming from candidate {self.current_index + 1}")

    def save_decisions(self, filename: str = "merge_decisions.json"):
        """Save decisions to file."""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.decisions, f, ensure_ascii=False, indent=2)

    def format_entry(self, entry: dict, indent: int = 4) -> str:
        """Format an entry for display."""
        lines = []
        prefix = " " * indent

        # Key fields to show
        if entry.get('source'):
            lines.append(f"{prefix}Source: {entry['source']}")
        if entry.get('translation_ro'):
            lines.append(f"{prefix}RO: {entry['translation_ro']}")
        if entry.get('translation_en'):
            lines.append(f"{prefix}EN: {entry['translation_en']}")
        if entry.get('translation_fr'):
            lines.append(f"{prefix}FR: {entry['translation_fr']}")
        if entry.get('definition'):
            def_text = entry['definition'][:100] + "..." if len(entry.get('definition', '')) > 100 else entry['definition']
            lines.append(f"{prefix}Def: {def_text}")
        if entry.get('part_of_speech'):
            lines.append(f"{prefix}POS: {entry['part_of_speech']}")

        return '\n'.join(lines) if lines else f"{prefix}(minimal data)"

    def display_candidate(self, candidate: dict):
        """Display a merge candidate for review."""
        print("\n" + "=" * 60)
        print(f"Candidate {self.current_index + 1}/{len(self.candidates)}")
        print(f"Normalized form: {candidate['normalized']}")
        print(f"Headwords: {candidate['headwords']}")
        if candidate.get('similarity'):
            print(f"Similarity: {candidate['similarity']:.2%}")
        print("-" * 60)

        for hw in candidate['headwords']:
            print(f"\n  [{hw}]")
            entries = self.entries_by_headword.get(hw, [])
            for i, entry in enumerate(entries):
                if len(entries) > 1:
                    print(f"    Entry {i + 1}:")
                print(self.format_entry(entry, indent=6 if len(entries) > 1 else 4))

        print("-" * 60)

    def get_input(self, prompt: str, valid_options: list[str]) -> str:
        """Get validated input from user."""
        while True:
            try:
                response = input(prompt).strip().lower()
                if response in valid_options:
                    return response
                print(f"Invalid input. Options: {', '.join(valid_options)}")
            except EOFError:
                return 'q'

    def review_candidates(self):
        """Main review loop."""
        print("\nReview Commands:")
        print("  [y] Yes, merge these entries")
        print("  [n] No, keep separate")
        print("  [s] Skip (decide later)")
        print("  [q] Quit and save")
        print("  [b] Go back one")
        print()

        while self.current_index < len(self.candidates):
            candidate = self.candidates[self.current_index]
            self.display_candidate(candidate)

            response = self.get_input(
                "Merge? [y/n/s/q/b]: ",
                ['y', 'n', 's', 'q', 'b']
            )

            if response == 'q':
                print("Saving and quitting...")
                self.save_decisions()
                break

            elif response == 'b':
                if self.current_index > 0:
                    self.current_index -= 1
                    # Remove last decision if it was for this candidate
                    if self.decisions["manual"]:
                        self.decisions["manual"].pop()
                else:
                    print("Already at the beginning")
                continue

            elif response == 's':
                self.current_index += 1
                continue

            elif response == 'y':
                # Record merge decision
                self.decisions["manual"].append({
                    "headwords": candidate["headwords"],
                    "action": "merge",
                    "canonical": candidate["headwords"][0]  # First alphabetically
                })
                self.current_index += 1

            elif response == 'n':
                # Record keep-separate decision
                self.decisions["manual"].append({
                    "headwords": candidate["headwords"],
                    "action": "separate"
                })
                self.current_index += 1

            # Auto-save every 10 decisions
            if len(self.decisions["manual"]) % 10 == 0:
                self.save_decisions()
                print("(auto-saved)")

        # Final save
        self.save_decisions()
        print(f"\nReview complete. {len(self.decisions['manual'])} decisions saved.")


def main():
    reviewer = MergeReviewer()
    reviewer.load_candidates()
    reviewer.load_entries()
    reviewer.load_existing_decisions()

    remaining = len(reviewer.candidates) - reviewer.current_index
    if remaining == 0:
        print("All candidates have been reviewed!")
        return

    print(f"\n{remaining} candidates remaining for review.")
    proceed = input("Start review? [y/n]: ").strip().lower()
    if proceed == 'y':
        reviewer.review_candidates()
    else:
        print("Review cancelled.")


if __name__ == "__main__":
    main()
