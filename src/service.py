"""Human-reviewed routing policies on top of learned sentiment probabilities."""
from __future__ import annotations

import re
import pandas as pd

from src.data import normalize, redact, validate_text
from src.model import SentimentEngine

THEMES = {
    'Waiting & delivery': r'\b(wait\w*|slow|delay\w*|delivery|late|queue)\b',
    'Service & staff': r'\b(staff|service|rude|friendly|waiter|manager|helpful)\b',
    'Quality': r'\b(food|taste\w*|cold|fresh|quality|broken|defective)\b',
    'Billing & value': r'\b(price\w*|expensive|bill\w*|refund\w*|charged|money|cost)\b',
    'Cleanliness': r'\b(clean\w*|dirty|hygiene|filthy)\b',
}
SAFETY = r'\b(poison\w*|unsafe|injur\w*|allerg\w*|harass\w*|threat\w*|fraud)\b'


def analyze_review(engine: SentimentEngine, text: str) -> dict:
    text = redact(validate_text(text))
    normalized = normalize(text)
    p = float(engine.probabilities([text])[0])
    confidence = max(p, 1-p)
    supported = engine.supported(text)
    accepted = supported and confidence >= engine.threshold
    label = 'positive' if p >= 0.5 else 'negative'
    flags = sorted(set(re.findall(SAFETY, normalized)))
    themes = [name for name, pattern in THEMES.items() if re.search(pattern, normalized)]
    reasons = []
    if flags:
        priority, rank = 'Inspect safety mention', 0
        reasons.append('Keyword mention: ' + ', '.join(flags) + '; verify context manually')
    elif not accepted:
        priority, rank = 'Resolve uncertainty', 1
    elif label == 'negative':
        priority, rank = 'Review negative feedback', 2
    else:
        priority, rank = 'Routine review', 3
    if not supported:
        reasons.append('Unsupported script or no recognized vocabulary')
    elif not accepted:
        reasons.append(f'Model confidence below validation-selected threshold {engine.threshold:.2f}')
    else:
        reasons.append(f'Model suggests {label}; human confirmation required')
    return {'text': text, 'sentiment': label if accepted else 'uncertain',
            'model_label': label, 'positive_probability': round(p, 6),
            'confidence': round(confidence, 6), 'accepted': accepted,
            'priority': priority, 'priority_rank': rank,
            'themes': ', '.join(themes) or 'Other', 'reason': '; '.join(reasons),
            'explanation': engine.explain(text)}


def analyze_batch(engine: SentimentEngine, reviews: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in reviews.to_dict('records'):
        result = analyze_review(engine, row['text'])
        result.pop('explanation')
        rows.append({**row, **result})
    return pd.DataFrame(rows).sort_values(['priority_rank', 'confidence'],
                                          ascending=[True, False], kind='stable').reset_index(drop=True)


def location_summary(results: pd.DataFrame) -> pd.DataFrame:
    return results.assign(negative=results.sentiment.eq('negative'),
                          uncertain=results.sentiment.eq('uncertain'),
                          safety=results.priority_rank.eq(0)).groupby('location').agg(
        reviews=('text', 'size'), negative=('negative', 'sum'),
        uncertain=('uncertain', 'sum'), safety_mentions=('safety', 'sum')).reset_index()
