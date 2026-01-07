#!/usr/bin/env python3
"""
Post-processing cleanup script for scraped dictionary data.

This script:
1. Removes test entries (aaaa1, etc.)
2. Cleans up redundant definition fields
3. Deduplicates entries
4. Regenerates clean export files
"""

import json
import re
from pathlib import Path
from exporter import DictionaryExporter
from models import DictionaryEntry


def is_test_entry(entry: dict) -> bool:
    """Check if an entry appears to be test data."""
    headword = entry.get('headword', '')

    # Check for obvious test headwords
    if headword and re.match(r'^[a-z]{4,}\d+$', headword.lower()):
        test_patterns = ['aaaa', 'bbbb', 'cccc', 'test', 'asdf']
        if any(headword.lower().startswith(p) for p in test_patterns):
            return True

    # Check for obvious test translations
    test_translations = {'rom', 'e1', 'f1', 'test', 'xxx'}
    for key in ['translation_ro', 'translation_en', 'translation_fr']:
        val = entry.get(key)
        if val and val.lower() in test_translations:
            return True

    return False


def clean_definition(entry: dict) -> dict:
    """Clean up redundant definition field."""
    definition = entry.get('definition')
    if definition:
        # Remove {ro:...} pattern if it's redundant with translation_ro
        if definition.startswith('{ro:'):
            # The definition is just the Romanian translation in braces
            # Check if we already have translation_ro
            if entry.get('translation_ro'):
                del entry['definition']
            else:
                # Extract the content and use it as translation_ro
                match = re.search(r'\{ro:\s*([^}]+)\}', definition)
                if match:
                    entry['translation_ro'] = match.group(1).strip()
                    del entry['definition']
    return entry


def deduplicate_entries(entries: list[dict]) -> list[dict]:
    """Remove duplicate entries based on headword + source."""
    seen = set()
    unique = []

    for entry in entries:
        # Create a unique key
        key = (entry.get('headword', ''), entry.get('source', ''))
        if key not in seen:
            seen.add(key)
            unique.append(entry)

    return unique


def main():
    data_dir = Path('../data')
    input_file = data_dir / 'dictionary.jsonl'

    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        return

    print("Loading entries...")
    entries = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    print(f"Loaded {len(entries)} entries")

    # Remove test entries
    print("\nFiltering test entries...")
    original_count = len(entries)
    entries = [e for e in entries if not is_test_entry(e)]
    removed_test = original_count - len(entries)
    print(f"  Removed {removed_test} test entries")

    # Clean definitions
    print("\nCleaning definitions...")
    cleaned_defs = 0
    for entry in entries:
        old_def = entry.get('definition')
        clean_definition(entry)
        if old_def and 'definition' not in entry:
            cleaned_defs += 1
    print(f"  Cleaned {cleaned_defs} redundant definitions")

    # Deduplicate
    print("\nDeduplicating...")
    original_count = len(entries)
    entries = deduplicate_entries(entries)
    removed_dupes = original_count - len(entries)
    print(f"  Removed {removed_dupes} duplicates")

    # Sort by headword
    entries.sort(key=lambda e: e.get('headword', '').lower())

    # Convert back to DictionaryEntry objects
    print("\nRegenerating export files...")
    entry_objects = []
    for e in entries:
        try:
            entry_objects.append(DictionaryEntry(**e))
        except Exception as ex:
            print(f"  Skipping invalid entry: {ex}")

    # Export
    exporter = DictionaryExporter()
    exporter.export_json(entry_objects, 'dictionary_clean.json')
    exporter.export_jsonl(entry_objects, 'dictionary_clean.jsonl')
    exporter.export_csv(entry_objects, 'dictionary_clean.csv')

    print(f"\nDone! Final count: {len(entry_objects)} entries")

    # Print statistics
    print("\n=== Statistics ===")
    with_ro = len([e for e in entries if e.get('translation_ro')])
    with_en = len([e for e in entries if e.get('translation_en')])
    with_fr = len([e for e in entries if e.get('translation_fr')])
    with_examples = len([e for e in entries if e.get('examples')])
    with_pronunciation = len([e for e in entries if e.get('pronunciation')])

    print(f"Entries with Romanian translation: {with_ro} ({100*with_ro/len(entries):.1f}%)")
    print(f"Entries with English translation: {with_en} ({100*with_en/len(entries):.1f}%)")
    print(f"Entries with French translation: {with_fr} ({100*with_fr/len(entries):.1f}%)")
    print(f"Entries with pronunciation: {with_pronunciation} ({100*with_pronunciation/len(entries):.1f}%)")
    print(f"Entries with examples: {with_examples} ({100*with_examples/len(entries):.1f}%)")


if __name__ == "__main__":
    main()
