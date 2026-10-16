"""Shared preprocessing, benchmark loading and bounded CSV validation."""
from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000
MAX_ROWS = 1000
MAX_TEXT = 5000


def redact(text: str) -> str:
    """Remove common contact patterns; this does not fully anonymize free text."""
    text = re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', text)
    return re.sub(r'(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)', '[PHONE]', text)


def normalize(text: str) -> str:
    """Canonicalize whitespace and apostrophes, retaining negation words."""
    text = unicodedata.normalize('NFKC', text).replace('’', "'")
    return re.sub(r'\s+', ' ', redact(text)).strip().lower()


def validate_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Review text must be a non-empty string.')
    if len(value) > MAX_TEXT:
        raise ValueError(f'Each review must contain at most {MAX_TEXT} characters.')
    if not any(c.isalpha() for c in value):
        raise ValueError('Review text must contain letters.')
    return value.strip()


def load_benchmark() -> tuple[pd.DataFrame, dict]:
    """Parse the final tab explicitly: embedded quotation marks are ordinary text."""
    rows = []
    for source, name in [('amazon', 'amazon_cells'), ('imdb', 'imdb'), ('yelp', 'yelp')]:
        path = ROOT / 'data/raw' / f'{name}_labelled.txt'
        if not path.exists():
            raise FileNotFoundError('Dataset missing. Run python scripts/download_data.py.')
        for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            text, label = line.rsplit('\t', 1)
            if label not in {'0', '1'}:
                raise ValueError(f'Invalid benchmark label: {path.name}:{line_number}')
            clean = normalize(validate_text(text))
            rows.append({'id': f'{source}-{line_number}', 'text': clean,
                         'label': int(label), 'source': source,
                         'text_hash': hashlib.sha256(clean.encode()).hexdigest()})
    frame = pd.DataFrame(rows)
    raw_count = len(frame)
    conflicts = frame.groupby('text_hash').label.nunique()
    conflicting = set(conflicts[conflicts > 1].index)
    conflict_rows = int(frame.text_hash.isin(conflicting).sum())
    frame = frame[~frame.text_hash.isin(conflicting)]
    duplicate_rows = int(frame.duplicated('text_hash').sum())
    frame = frame.drop_duplicates('text_hash').reset_index(drop=True)
    return frame, {'raw_rows': raw_count, 'conflicting_rows_removed': conflict_rows,
                   'duplicate_rows_removed': duplicate_rows, 'clean_rows': len(frame)}


def split_benchmark(frame: pd.DataFrame):
    strata = frame.source + '-' + frame.label.astype(str)
    train, rest = train_test_split(frame, test_size=0.4, random_state=42, stratify=strata)
    val, test = train_test_split(rest, test_size=0.5, random_state=42,
                               stratify=rest.source + '-' + rest.label.astype(str))
    return train.copy(), val.copy(), test.copy()


def read_reviews(raw: bytes) -> pd.DataFrame:
    """Reject invalid files as a whole; never silently discard review rows."""
    if len(raw) > MAX_BYTES:
        raise ValueError('CSV exceeds the 2 MB limit.')
    try:
        frame = pd.read_csv(io.StringIO(raw.decode('utf-8-sig')), dtype=str, keep_default_na=False)
    except (UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise ValueError('Upload a valid UTF-8 CSV with a header row.') from exc
    required = ['review_id', 'text', 'location', 'date']
    if not set(required).issubset(frame.columns):
        raise ValueError('CSV requires review_id, text, location and date columns.')
    frame = frame[required].copy()
    if not 1 <= len(frame) <= MAX_ROWS:
        raise ValueError('CSV must contain between 1 and 1000 reviews.')
    for column in ['review_id', 'location', 'date']:
        frame[column] = frame[column].str.strip()
        if frame[column].eq('').any():
            raise ValueError(f'{column} cannot be empty.')
    if frame.review_id.duplicated().any():
        raise ValueError('review_id must be unique within the upload.')
    if frame.review_id.str.len().gt(100).any() or frame.location.str.len().gt(100).any():
        raise ValueError('Review IDs and locations must be at most 100 characters.')
    frame['text'] = frame.text.map(validate_text)
    if not frame.date.str.fullmatch(r'\d{4}-\d{2}-\d{2}').all():
        raise ValueError('Dates must use YYYY-MM-DD.')
    dates = pd.to_datetime(frame.date, format='%Y-%m-%d', errors='coerce')
    if dates.isna().any():
        raise ValueError('Dates must be valid calendar dates.')
    frame['date'] = dates.dt.strftime('%Y-%m-%d')
    # Metadata can also carry contact information.
    for column in ['review_id', 'location', 'text']:
        frame[column] = frame[column].map(redact)
    return frame


def safe_csv(frame: pd.DataFrame) -> bytes:
    """Neutralize spreadsheet formula prefixes on all string cells."""
    def safe(value):
        if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
            return "'" + value
        return value
    return frame.map(safe).to_csv(index=False).encode('utf-8')
