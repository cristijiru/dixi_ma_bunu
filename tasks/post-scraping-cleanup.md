# Post-Scraping Cleanup Tasks

## 1. Merge Variant Spellings

Aromanian has multiple spelling conventions that result in duplicate entries for the same word.

### Common Spelling Variants to Merge:
- `lj` vs `l` (e.g., `agãljisescu` / `agãlisescu`)
- `sh` vs `s` (e.g., `agrãshescu` / `agrãsescu`)
- `dh` vs `d` (e.g., `adhichipsescu` / `adichipsescu`)
- `gh` vs `g` (e.g., `aghãpisescu` / `agãpisescu`)
- `ts` vs `ț` variations
- `nj` vs `n` variations

### Approach:
1. Normalize headwords to a canonical form
2. Group entries by normalized form
3. Merge translations, keeping all spelling variants as alternates
4. Preserve source attribution for each translation

## 2. Diacritic Normalization for 'A'

Words starting with diacritical 'a' variants should be grouped:
- `a` (plain)
- `ã` (a with breve)
- `â` (a with circumflex)

### Considerations:
- `ã` and `â` are distinct phonemes in Romanian/Aromanian
- For search purposes, users may type plain 'a' expecting to find `ã`/`â` words
- Keep distinct in data, but enable diacritic-insensitive search

### Implementation:
1. Store original spelling with diacritics
2. Create search index with normalized (ASCII) versions
3. Display results with correct diacritics

## 3. Singular/Plural Form Handling

Many entries appear as `word1/word2` format (e.g., `acriri/acrire`):
- These are often singular/plural or infinitive/noun forms
- Consider splitting into separate fields or linked entries

## Prerequisites
- [ ] Scraping complete
- [ ] Word count verification passed
- [ ] Initial data committed to git

## Priority
Run after scraping is validated and committed.
