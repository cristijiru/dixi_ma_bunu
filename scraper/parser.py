"""HTML parser for dixionline.net dictionary entries."""

import re
from bs4 import BeautifulSoup, Tag
from models import DictionaryEntry


def parse_letter_index(html: str) -> list[str]:
    """
    Parse a letter index page and extract all word links.

    Returns a list of words (inputWord values) found on the page.
    """
    soup = BeautifulSoup(html, 'lxml')
    words = []

    # Find the div containing word links
    word_div = soup.find('div', id='my_text')
    if word_div:
        # There are multiple divs with id='my_text', find the one with links
        for div in soup.find_all('div', id='my_text'):
            links = div.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'inputWord=' in href:
                    # Extract word from URL
                    match = re.search(r'inputWord=([^&]+)', href)
                    if match:
                        word = match.group(1)
                        words.append(word)

    return words


def get_word_count_from_index(html: str) -> int:
    """Extract the total word count from a letter index page."""
    soup = BeautifulSoup(html, 'lxml')

    for div in soup.find_all('div', id='my_text'):
        text = div.get_text()
        # Look for pattern like "Zboarã cari ahurhescu cu 'A' : 5016"
        match = re.search(r':\s*(\d+)', text)
        if match:
            return int(match.group(1))

    return 0


def clean_text(text: str | None) -> str | None:
    """Clean and normalize text."""
    if text is None:
        return None
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove common artifacts
    text = text.replace('\u2026', '...')  # ellipsis
    text = text.replace('\u00a0', ' ')  # non-breaking space
    return text if text else None


def parse_search_results(html: str, query_word: str) -> list[DictionaryEntry]:
    """
    Parse search results page and extract all dictionary entries.

    The search results contain multiple <article class="article"> elements,
    each representing a dictionary entry.
    """
    soup = BeautifulSoup(html, 'lxml')
    entries = []

    articles = soup.find_all('article', class_='article')

    for article in articles:
        entry = parse_article(article, query_word)
        if entry:
            entries.append(entry)

    return entries


def is_test_entry(headword: str, translations: dict) -> bool:
    """Check if an entry appears to be test data."""
    # Check for obvious test headwords
    if headword and re.match(r'^[a-z]{4,}\d+$', headword.lower()):
        # Pattern like "aaaa1", "test1", etc.
        test_patterns = ['aaaa', 'bbbb', 'cccc', 'test', 'asdf']
        if any(headword.lower().startswith(p) for p in test_patterns):
            return True

    # Check for obvious test translations
    test_translations = {'rom', 'e1', 'f1', 'test', 'xxx'}
    for val in translations.values():
        if val and val.lower() in test_translations:
            return True

    return False


def parse_article(article: Tag, source_query: str) -> DictionaryEntry | None:
    """Parse a single article element into a DictionaryEntry."""
    try:
        # Extract headword from h2 > a
        h2 = article.find('h2')
        if not h2:
            return None

        headword_link = h2.find('a')
        headword = clean_text(headword_link.get_text() if headword_link else h2.get_text())

        if not headword:
            return None

        # Get the paragraph containing all data
        p = article.find('p')
        if not p:
            return DictionaryEntry(headword=headword)

        p_text = p.get_text()
        p_html = str(p)

        # Initialize entry
        entry = DictionaryEntry(headword=headword, source_url=f"https://www.dixionline.net/index.php?inputWord={source_query}")

        # Extract translations - first try curly brace format: {ro: ...} {fr: ...} {en: ...}
        # This is the most reliable as it's in the text content itself
        ro_match = re.search(r'\{ro:\s*([^}]+)\}', p_text)
        if ro_match:
            entry.translation_ro = clean_text(ro_match.group(1))

        fr_match = re.search(r'\{fr:\s*([^}]+)\}', p_text)
        if fr_match:
            entry.translation_fr = clean_text(fr_match.group(1))

        en_match = re.search(r'\{en:\s*([^}]+)\}', p_text)
        if en_match:
            entry.translation_en = clean_text(en_match.group(1))

        # If curly brace format not found, try the simpler RO:/EN:/FR: format
        # For "Mariana Bara" dictionary entries
        if not entry.translation_ro:
            # Look for "RO:" prefix followed by span
            ro_span = p.find('span', class_='highlight_ro')
            if ro_span:
                # Make sure it's preceded by "RO:" and not inside a {fr:} pattern
                ro_text = ro_span.get_text()
                if not ro_text.startswith('{'):
                    entry.translation_ro = clean_text(ro_text)

        if not entry.translation_en:
            en_span = p.find('span', class_='highlight_eng')
            if en_span:
                en_text = en_span.get_text()
                # Filter out the § symbol which uses the same class
                if en_text.strip() != '§' and not en_text.startswith('{'):
                    entry.translation_en = clean_text(en_text)

        if not entry.translation_fr:
            fr_span = p.find('span', class_='highlight_fran')
            if fr_span:
                fr_text = fr_span.get_text()
                if not fr_text.startswith('{'):
                    entry.translation_fr = clean_text(fr_text)

        # Check if this is test data and skip it
        translations = {
            'ro': entry.translation_ro,
            'en': entry.translation_en,
            'fr': entry.translation_fr
        }
        if is_test_entry(headword, translations):
            return None

        # Extract etymology
        et_match = re.search(r'Et:\s*([^<\n]+)', p_text)
        if et_match:
            et = clean_text(et_match.group(1))
            if et and et not in ['', 'Et:']:
                entry.etymology = et

        # Extract context
        context_match = re.search(r'Context:\s*([^<\n]+)', p_text)
        if context_match:
            ctx = clean_text(context_match.group(1))
            if ctx:
                entry.context = ctx

        # Extract pronunciation - usually in parentheses after headword
        # Format: headword (pronunciation) sf/sm/vb
        pvorb_span = p.find('span', class_='highlight_pvorb')
        if pvorb_span:
            # Get text after the headword span
            next_text = pvorb_span.next_sibling
            if next_text and isinstance(next_text, str):
                # Look for pronunciation in parentheses
                pron_match = re.search(r'\(([^)]+)\)', next_text)
                if pron_match:
                    entry.pronunciation = pron_match.group(1)

                # Look for part of speech
                pos_match = re.search(r'\b(sf|sm|sn|vb|adg|adv|prep|conj|interj|pron|articul)\b', next_text, re.IGNORECASE)
                if pos_match:
                    entry.part_of_speech = pos_match.group(1).lower()

        # Also check for part of speech in expr spans
        expr_span = p.find('span', class_='highlight_expr')
        if expr_span:
            expr_text = expr_span.get_text()
            pos_match = re.search(r'\b(sf|sm|sn|vb|adg|adv|prep|conj|interj|pron|articul)\b', expr_text, re.IGNORECASE)
            if pos_match and not entry.part_of_speech:
                entry.part_of_speech = pos_match.group(1).lower()

        # Extract examples (ex: prefix)
        similar_span = p.find('span', class_='highlight_similar')
        if similar_span and 'ex:' in similar_span.get_text():
            # Get text after ex:
            next_sib = similar_span.next_sibling
            if next_sib:
                example_text = str(next_sib) if isinstance(next_sib, str) else next_sib.get_text() if hasattr(next_sib, 'get_text') else ''
                example_text = clean_text(example_text)
                if example_text:
                    # Split on semicolons for multiple examples
                    examples = [e.strip() for e in example_text.split(';') if e.strip()]
                    entry.examples = examples[:10]  # Limit to 10 examples

        # Extract source from the "more" link
        source_links = p.find_all('a', class_='more')
        for link in source_links:
            link_text = link.get_text()
            if 'Dictsiunar' in link_text or 'T.Cunia' in link_text or 'Mariana Bara' in link_text:
                # Clean up source name
                source = clean_text(link_text)
                if source:
                    # Remove DB reference
                    source = re.sub(r'\s*Data DB:\d+>[\d\-\s:\.]+\s*', '', source)
                    source = re.sub(r'\s*»\s*$', '', source)
                    entry.source = source.strip()
                    break

        # Extract related terms (marked with §)
        related = []
        eng_spans = p.find_all('span', class_='highlight_eng')
        for span in eng_spans:
            if span.get_text().strip() == '§':
                # Next sibling should contain the related term
                next_sib = span.next_sibling
                if next_sib:
                    related_text = str(next_sib) if isinstance(next_sib, str) else ''
                    # Extract the term (usually up to parenthesis or span)
                    term_match = re.search(r'([a-zA-ZãâîșțşçăĂÂÎȘŢÇ\-/]+)', related_text)
                    if term_match:
                        related.append(term_match.group(1))

        if related:
            entry.related_terms = list(set(related))[:20]  # Dedupe and limit

        # Extract definition (main Aromanian text before translations)
        # Note: highlight_arm span often contains {ro:...} which is redundant
        arm_span = p.find('span', class_='highlight_arm')
        if arm_span:
            def_text = clean_text(arm_span.get_text())
            # Skip if it's just the Romanian translation in curly braces
            if def_text and not def_text.startswith('{ro:'):
                entry.definition = def_text

        # Extract expressions (expr: markers)
        expr_spans = p.find_all('span', class_='highlight_ex')
        expressions = []
        for span in expr_spans:
            if 'expr:' in span.get_text().lower():
                # Get surrounding text for context
                parent_text = span.parent.get_text() if span.parent else ''
                expr_match = re.search(r'expr:\s*([^;]+)', parent_text, re.IGNORECASE)
                if expr_match:
                    expressions.append(clean_text(expr_match.group(1)))

        if expressions:
            entry.expressions = list(set(expressions))[:10]

        return entry

    except Exception as e:
        print(f"Error parsing article: {e}")
        return None


def parse_all_letters() -> list[str]:
    """Return all letters in the alphabet for iteration."""
    return list('abcdefghijklmnopqrstuvwxyz')
