"""Data models for dictionary entries."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class DictionaryEntry:
    """Represents a single dictionary entry."""

    headword: str
    pronunciation: Optional[str] = None
    part_of_speech: Optional[str] = None
    inflections: Optional[str] = None
    definition: Optional[str] = None
    translation_ro: Optional[str] = None
    translation_en: Optional[str] = None
    translation_fr: Optional[str] = None
    etymology: Optional[str] = None
    context: Optional[str] = None
    examples: list[str] = field(default_factory=list)
    expressions: list[str] = field(default_factory=list)
    related_terms: list[str] = field(default_factory=list)
    source: Optional[str] = None
    source_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None and value != [] and value != "":
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_csv_row(self) -> dict:
        """Convert to flat dictionary for CSV export."""
        d = self.to_dict()
        # Flatten lists to semicolon-separated strings
        for key in ['examples', 'expressions', 'related_terms']:
            if key in d and isinstance(d[key], list):
                d[key] = '; '.join(d[key])
        return d
