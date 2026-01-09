#!/usr/bin/env python3
"""Recover the 2 missing words from the scrape."""

import asyncio
import json
import sys
from pathlib import Path

# Add scraper directory to path
sys.path.insert(0, str(Path(__file__).parent))

import httpx
from parser import parse_search_results
from urllib.parse import quote

MISSING_WORDS = ['marlu']
OUTPUT_FILE = Path('../data/raw2/dictionary.jsonl')


async def scrape_word(client: httpx.AsyncClient, word: str):
    """Scrape a single word."""
    encoded = quote(word, safe='')
    url = f"https://www.dixionline.net/index.php?inputWord={encoded}"

    response = await client.get(url)
    response.raise_for_status()

    entries = parse_search_results(response.text, word)
    return entries


async def main():
    print("Recovering missing words...")

    async with httpx.AsyncClient(timeout=30) as client:
        all_entries = []

        for word in MISSING_WORDS:
            print(f"  Scraping: {word}")
            try:
                entries = await scrape_word(client, word)
                print(f"    Found {len(entries)} entries")
                all_entries.extend(entries)
            except Exception as e:
                print(f"    Error: {e}")

    if all_entries:
        print(f"\nAppending {len(all_entries)} entries to {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            for entry in all_entries:
                f.write(entry.to_json() + '\n')

        print("Done!")
    else:
        print("No entries found.")


if __name__ == "__main__":
    asyncio.run(main())
