#!/usr/bin/env python3
"""
Main scraper for dixionline.net Aromanian dictionary.

This scraper:
1. Fetches all letter index pages to discover words
2. Fetches each word's search results page
3. Parses the HTML and extracts structured data
4. Exports to JSON, JSONL, and CSV formats

Usage:
    python scraper.py                    # Scrape all letters
    python scraper.py --letters a b c    # Scrape specific letters
    python scraper.py --resume           # Resume from last checkpoint
    python scraper.py --test             # Test with first 10 words only
"""

import argparse
import asyncio
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

import httpx
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from models import DictionaryEntry
from parser import parse_letter_index, parse_search_results, get_word_count_from_index
from exporter import DictionaryExporter


# Configuration
BASE_URL = "https://www.dixionline.net"
REQUEST_DELAY_MIN = 1.0  # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX = 2.0  # Maximum delay (for politeness)
TIMEOUT = 30.0
MAX_CONCURRENT = 1  # Keep it at 1 for politeness
CHECKPOINT_FILE = "../data/checkpoint.json"
USER_AGENT = "Mozilla/5.0 (compatible; AromanianDictBot/1.0; +https://github.com/your-repo)"


class DictionaryScraper:
    """Scrapes the dixionline.net dictionary."""

    def __init__(self, delay_min: float = REQUEST_DELAY_MIN, delay_max: float = REQUEST_DELAY_MAX):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.client: httpx.AsyncClient | None = None
        self.entries: list[DictionaryEntry] = []
        self.scraped_words: set[str] = set()
        self.failed_words: set[str] = set()
        self.checkpoint_path = Path(CHECKPOINT_FILE)
        self.exporter = DictionaryExporter()

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=TIMEOUT,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def delay(self):
        """Polite delay between requests."""
        delay = random.uniform(self.delay_min, self.delay_max)
        await asyncio.sleep(delay)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def fetch(self, url: str) -> str:
        """Fetch a URL with retry logic."""
        await self.delay()
        response = await self.client.get(url)
        response.raise_for_status()
        return response.text

    async def get_words_for_letter(self, letter: str) -> list[str]:
        """Get all words starting with a given letter."""
        url = f"{BASE_URL}/index.php?l={letter}"
        print(f"\nFetching index for letter '{letter.upper()}'...")

        try:
            html = await self.fetch(url)
            words = parse_letter_index(html)
            count = get_word_count_from_index(html)
            print(f"  Found {len(words)} words (reported: {count})")
            return words
        except Exception as e:
            print(f"  Error fetching letter {letter}: {e}")
            return []

    async def scrape_word(self, word: str) -> list[DictionaryEntry]:
        """Scrape a single word's dictionary entries."""
        # URL encode the word for the request
        encoded_word = quote(word, safe='')
        url = f"{BASE_URL}/index.php?inputWord={encoded_word}"

        try:
            html = await self.fetch(url)
            entries = parse_search_results(html, word)
            return entries
        except Exception as e:
            print(f"  Error scraping word '{word}': {e}")
            self.failed_words.add(word)
            return []

    def save_checkpoint(self, current_letter: str, current_word_idx: int):
        """Save progress checkpoint."""
        checkpoint = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_letter": current_letter,
            "current_word_idx": current_word_idx,
            "scraped_words": list(self.scraped_words),
            "failed_words": list(self.failed_words),
            "entries_count": len(self.entries),
        }

        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    def load_checkpoint(self) -> dict | None:
        """Load progress from checkpoint file."""
        if not self.checkpoint_path.exists():
            return None

        with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)

        self.scraped_words = set(checkpoint.get('scraped_words', []))
        self.failed_words = set(checkpoint.get('failed_words', []))

        # Load existing entries from JSONL
        jsonl_path = self.exporter.output_dir / "dictionary.jsonl"
        if jsonl_path.exists():
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.entries.append(DictionaryEntry(**data))

        print(f"Resumed from checkpoint: {len(self.scraped_words)} words scraped, {len(self.entries)} entries loaded")
        return checkpoint

    async def scrape_letters(self, letters: list[str], resume: bool = False, test_mode: bool = False):
        """Scrape all words for the given letters."""
        start_letter_idx = 0
        start_word_idx = 0

        if resume:
            checkpoint = self.load_checkpoint()
            if checkpoint:
                # Find starting position
                current_letter = checkpoint.get('current_letter', 'a')
                if current_letter in letters:
                    start_letter_idx = letters.index(current_letter)
                    start_word_idx = checkpoint.get('current_word_idx', 0)

        all_words_by_letter = {}

        # First, collect all words for all letters
        print("\n=== Phase 1: Collecting word lists ===")
        for letter in letters:
            words = await self.get_words_for_letter(letter)
            all_words_by_letter[letter] = words

        total_words = sum(len(words) for words in all_words_by_letter.values())
        print(f"\nTotal words to scrape: {total_words}")

        if test_mode:
            print("\n[TEST MODE] Only scraping first 10 words per letter")

        # Now scrape each word
        print("\n=== Phase 2: Scraping entries ===")

        for letter_idx, letter in enumerate(letters):
            if letter_idx < start_letter_idx:
                continue

            words = all_words_by_letter[letter]

            if test_mode:
                words = words[:10]

            # Determine starting word index
            word_start = start_word_idx if letter_idx == start_letter_idx else 0

            print(f"\n--- Letter {letter.upper()} ({len(words)} words) ---")

            pbar = tqdm(enumerate(words[word_start:], start=word_start), total=len(words) - word_start, desc=f"Letter {letter.upper()}")

            for word_idx, word in pbar:
                # Skip already scraped words
                if word in self.scraped_words:
                    continue

                pbar.set_postfix(word=word[:20])

                entries = await self.scrape_word(word)

                if entries:
                    self.entries.extend(entries)
                    self.scraped_words.add(word)

                    # Save incrementally
                    for entry in entries:
                        self.exporter.export_incremental_jsonl(entry)

                # Save checkpoint every 50 words
                if (word_idx + 1) % 50 == 0:
                    self.save_checkpoint(letter, word_idx)

            # Save checkpoint after each letter
            self.save_checkpoint(letter, len(words))

        print(f"\n=== Scraping complete ===")
        print(f"Total entries: {len(self.entries)}")
        print(f"Failed words: {len(self.failed_words)}")

        if self.failed_words:
            print(f"Failed words: {list(self.failed_words)[:20]}...")

    def finalize_export(self):
        """Generate final export files from collected entries."""
        print("\n=== Generating final exports ===")

        # Deduplicate entries by headword + source
        seen = set()
        unique_entries = []
        for entry in self.entries:
            key = (entry.headword, entry.source or '')
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)

        print(f"Unique entries after deduplication: {len(unique_entries)}")

        # Sort by headword
        unique_entries.sort(key=lambda e: e.headword.lower())

        # Export all formats
        self.exporter.export_json(unique_entries)
        self.exporter.export_csv(unique_entries)

        # JSONL is already written incrementally, but rewrite with deduplicated/sorted data
        self.exporter.export_jsonl(unique_entries)

        print("\nExport complete!")


async def main():
    parser = argparse.ArgumentParser(description="Scrape dixionline.net dictionary")
    parser.add_argument('--letters', nargs='+', default=list('abcdefghijklmnopqrstuvwxyz'),
                        help='Letters to scrape (default: all)')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from last checkpoint')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: only scrape first 10 words per letter')
    parser.add_argument('--delay-min', type=float, default=REQUEST_DELAY_MIN,
                        help=f'Minimum delay between requests (default: {REQUEST_DELAY_MIN})')
    parser.add_argument('--delay-max', type=float, default=REQUEST_DELAY_MAX,
                        help=f'Maximum delay between requests (default: {REQUEST_DELAY_MAX})')

    args = parser.parse_args()

    letters = [l.lower() for l in args.letters]

    print("=" * 60)
    print("Dixionline.net Dictionary Scraper")
    print("=" * 60)
    print(f"Letters to scrape: {', '.join(l.upper() for l in letters)}")
    print(f"Request delay: {args.delay_min}-{args.delay_max}s")
    print(f"Resume mode: {args.resume}")
    print(f"Test mode: {args.test}")
    print("=" * 60)

    async with DictionaryScraper(delay_min=args.delay_min, delay_max=args.delay_max) as scraper:
        await scraper.scrape_letters(letters, resume=args.resume, test_mode=args.test)
        scraper.finalize_export()


if __name__ == "__main__":
    asyncio.run(main())
