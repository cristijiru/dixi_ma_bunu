#!/usr/bin/env python3
"""
Verification script to ensure no entries are missed during scraping.

This script:
1. Fetches the word count for each letter from the source website
2. Compares against what we have in our checkpoint/scraped data
3. Reports any discrepancies
"""

import asyncio
import json
import re
from pathlib import Path
import httpx
from bs4 import BeautifulSoup


BASE_URL = "https://www.dixionline.net"
CHECKPOINT_FILE = Path("../data/checkpoint.json")
JSONL_FILE = Path("../data/dictionary.jsonl")


async def get_expected_word_counts() -> dict[str, int]:
    """Fetch expected word counts for each letter from the source."""
    counts = {}

    async with httpx.AsyncClient(timeout=30) as client:
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            try:
                url = f"{BASE_URL}/index.php?l={letter}"
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'lxml')

                # Look for "Zboarã cari ahurhescu cu 'X' : NNN"
                for div in soup.find_all('div', id='my_text'):
                    text = div.get_text()
                    match = re.search(r"'[A-Z]'\s*:\s*(\d+)", text)
                    if match:
                        counts[letter] = int(match.group(1))
                        break

                if letter not in counts:
                    counts[letter] = 0

                print(f"  {letter.upper()}: {counts.get(letter, 0)} words")
                await asyncio.sleep(1)  # Polite delay

            except Exception as e:
                print(f"  {letter.upper()}: Error - {e}")
                counts[letter] = -1

    return counts


def get_scraped_word_counts() -> dict[str, int]:
    """Count words scraped per letter from checkpoint."""
    if not CHECKPOINT_FILE.exists():
        return {}

    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)

    scraped_words = checkpoint.get('scraped_words', [])

    # Count by first letter
    counts = {}
    for word in scraped_words:
        if word:
            first_letter = word[0].lower()
            # Handle special characters - map to closest letter
            if first_letter in 'ãâ':
                first_letter = 'a'
            elif first_letter in 'îș':
                first_letter = 'i' if first_letter == 'î' else 's'
            elif first_letter in 'țş':
                first_letter = 't' if first_letter == 'ț' else 's'

            if first_letter.isalpha():
                counts[first_letter] = counts.get(first_letter, 0) + 1

    return counts


def get_unique_headwords_from_jsonl() -> dict[str, set]:
    """Get unique headwords from JSONL grouped by first letter."""
    if not JSONL_FILE.exists():
        return {}

    headwords_by_letter = {}

    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    headword = entry.get('headword', '')
                    if headword:
                        first_letter = headword[0].lower()
                        if first_letter in 'ãâ':
                            first_letter = 'a'
                        elif not first_letter.isalpha():
                            continue

                        if first_letter not in headwords_by_letter:
                            headwords_by_letter[first_letter] = set()
                        headwords_by_letter[first_letter].add(headword)
                except:
                    pass

    return {k: len(v) for k, v in headwords_by_letter.items()}


async def main():
    print("=" * 60)
    print("Scraper Completeness Verification")
    print("=" * 60)

    print("\n1. Fetching expected word counts from source...")
    expected = await get_expected_word_counts()

    print("\n2. Getting scraped word counts from checkpoint...")
    scraped = get_scraped_word_counts()

    print("\n3. Getting unique headwords from JSONL...")
    headwords = get_unique_headwords_from_jsonl()

    print("\n" + "=" * 60)
    print("COMPARISON REPORT")
    print("=" * 60)
    print(f"{'Letter':<8} {'Expected':<12} {'Scraped':<12} {'Headwords':<12} {'Status'}")
    print("-" * 60)

    total_expected = 0
    total_scraped = 0
    total_headwords = 0

    for letter in 'abcdefghijklmnopqrstuvwxyz':
        exp = expected.get(letter, 0)
        scr = scraped.get(letter, 0)
        hwd = headwords.get(letter, 0)

        total_expected += exp if exp > 0 else 0
        total_scraped += scr
        total_headwords += hwd

        if exp < 0:
            status = "ERROR"
        elif scr == 0 and exp > 0:
            status = "PENDING"
        elif scr < exp:
            status = f"IN PROGRESS ({100*scr/exp:.1f}%)"
        elif scr >= exp:
            status = "COMPLETE"
        else:
            status = "N/A"

        print(f"{letter.upper():<8} {exp:<12} {scr:<12} {hwd:<12} {status}")

    print("-" * 60)
    print(f"{'TOTAL':<8} {total_expected:<12} {total_scraped:<12} {total_headwords:<12}")
    print("=" * 60)

    # Check for failed words
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)

        failed = checkpoint.get('failed_words', [])
        if failed:
            print(f"\nWARNING: {len(failed)} failed words:")
            for word in failed[:20]:
                print(f"  - {word}")
            if len(failed) > 20:
                print(f"  ... and {len(failed) - 20} more")
        else:
            print("\nNo failed words.")


if __name__ == "__main__":
    asyncio.run(main())
