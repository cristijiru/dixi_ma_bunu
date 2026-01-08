"""Export dictionary entries to various formats."""

import csv
import json
from datetime import datetime
from pathlib import Path
from models import DictionaryEntry


class DictionaryExporter:
    """Exports dictionary entries to JSON, JSONL, and CSV formats.

    Exports directly to data/ for use by the backend.
    No merging step - preserves all fields including definition.
    """

    def __init__(self, output_dir: str = "../data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_all(self, entries: list[DictionaryEntry], base_name: str = "dictionary"):
        """Export entries to all formats."""
        self.export_json(entries, f"{base_name}.json")
        self.export_jsonl(entries, f"{base_name}.jsonl")
        self.export_csv(entries, f"{base_name}.csv")

    def export_json(self, entries: list[DictionaryEntry], filename: str = "dictionary.json"):
        """Export entries to a single JSON file with metadata."""
        output_path = self.output_dir / filename

        # Build metadata
        metadata = {
            "source": "dixionline.net",
            "source_url": "https://www.dixionline.net",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "total_entries": len(entries),
            "description": "Aromanian/Vlach dictionary with translations to Romanian, English, and French"
        }

        # Build output structure
        output = {
            "metadata": metadata,
            "entries": [entry.to_dict() for entry in entries]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Exported {len(entries)} entries to {output_path}")

    def export_jsonl(self, entries: list[DictionaryEntry], filename: str = "dictionary.jsonl"):
        """Export entries to JSON Lines format (one JSON object per line)."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(entry.to_json() + '\n')

        print(f"Exported {len(entries)} entries to {output_path}")

    def export_csv(self, entries: list[DictionaryEntry], filename: str = "dictionary.csv"):
        """Export entries to CSV format."""
        output_path = self.output_dir / filename

        if not entries:
            print("No entries to export")
            return

        # Define all possible fields
        fieldnames = [
            'headword',
            'pronunciation',
            'part_of_speech',
            'inflections',
            'definition',
            'translation_ro',
            'translation_en',
            'translation_fr',
            'etymology',
            'context',
            'examples',
            'expressions',
            'related_terms',
            'source',
            'source_url'
        ]

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()

            for entry in entries:
                writer.writerow(entry.to_csv_row())

        print(f"Exported {len(entries)} entries to {output_path}")

    def export_incremental_jsonl(self, entry: DictionaryEntry, filename: str = "dictionary.jsonl"):
        """Append a single entry to JSONL file (for incremental saving)."""
        output_path = self.output_dir / filename

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(entry.to_json() + '\n')
