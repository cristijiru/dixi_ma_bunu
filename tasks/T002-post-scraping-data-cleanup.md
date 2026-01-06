# T002: Post-Scraping Data Cleanup

**Priority:** HIGH
**Status:** Pending (waiting for scraper completion)

## Description
Clean up and normalize the scraped dictionary data.

## Tasks
- [ ] Merge variant spellings (lj/l, sh/s, dh/d, gh/g, ts/ț, nj/n)
- [ ] Implement diacritic-insensitive search (a/ã/â normalization)
- [ ] Handle singular/plural form entries (word1/word2 format)
- [ ] Verify word count matches expected total
- [ ] Commit cleaned data to git

## Technical Approach
1. Normalize headwords to canonical form
2. Group entries by normalized form
3. Merge translations, keeping spelling variants as alternates
4. Create search index with ASCII-normalized versions
