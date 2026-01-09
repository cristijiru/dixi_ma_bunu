#!/usr/bin/env python3
"""
Fix examples that were incorrectly split on semicolons inside parentheses.

The parser splits examples on "; " but doesn't account for semicolons
inside parenthetical expressions like:
    "easti-un farmazon (un mason, maltean; icã fig: om arãu)"

This script detects and merges such split examples by tracking parenthesis balance.
"""

import json
import sys


def count_parens(s: str) -> int:
    """Count unmatched parentheses. Positive = more open, negative = more close."""
    balance = 0
    for c in s:
        if c == '(':
            balance += 1
        elif c == ')':
            balance -= 1
    return balance


def fix_examples(examples: list[str]) -> tuple[list[str], bool]:
    """Merge incorrectly split examples. Returns (fixed_list, was_changed)."""
    if not examples or len(examples) < 2:
        return examples, False

    fixed = []
    i = 0
    changed = False

    while i < len(examples):
        current = examples[i]
        balance = count_parens(current)

        if balance > 0:  # More opening than closing - need to merge
            parts = [current]
            j = i + 1
            while j < len(examples) and balance > 0:
                parts.append(examples[j])
                balance += count_parens(examples[j])
                j += 1

            if len(parts) > 1:
                # Merge with "; " separator (restoring original)
                merged = "; ".join(parts)
                fixed.append(merged)
                changed = True
                i = j
                continue

        fixed.append(current)
        i += 1

    return fixed, changed


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_split_examples.py <dictionary.jsonl>")
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, 'r') as f:
        lines = f.readlines()

    fixed_lines = []
    total_fixes = 0
    fixed_entries = []

    for line_num, line in enumerate(lines, 1):
        entry = json.loads(line)
        entry_changed = False

        for ent in entry.get('entries', []):
            if 'examples' in ent:
                fixed_examples, changed = fix_examples(ent['examples'])
                if changed:
                    ent['examples'] = fixed_examples
                    entry_changed = True

        if entry_changed:
            total_fixes += 1
            fixed_entries.append((line_num, entry['id'], entry['canonical']))

        fixed_lines.append(json.dumps(entry, ensure_ascii=False))

    # Write back
    with open(filepath, 'w') as f:
        f.write('\n'.join(fixed_lines) + '\n')

    print(f"Fixed {total_fixes} entries")
    for line_num, word_id, canonical in fixed_entries:
        print(f"  Line {line_num}: {word_id} ({canonical})")


if __name__ == "__main__":
    main()
