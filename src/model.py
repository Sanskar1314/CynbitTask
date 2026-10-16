"""Train-only TF-IDF and validation-selected logistic sentiment model."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

from src.data import load_benchmark, normalize, split_benchmark


def make_model(c: float = 1.0) -> Pipeline:
    return Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=2,
                                sublinear_tf=True, max_features=20000,
                                strip_accents='unicode')),
        ('classifier', LogisticRegression(C=c, max_iter=1000, random_state=42)),
    ])


@dataclass
class SentimentEngine:
    pipeline: Pipeline
    threshold: float
    selection: dict

    def probabilities(self, texts: list[str]) -> np.ndarray:
        return self.pipeline.predict_proba([normalize(t) for t in texts])[:, 1]

    def explain(self, text: str, top_k: int = 8) -> list[dict]:
        """Exact feature contributions to positive log-odds; not causal explanations."""
        vectorizer = self.pipeline.named_steps['tfidf']
        classifier = self.pipeline.named_steps['classifier']
        vector = vectorizer.transform([normalize(text)])
        names = vectorizer.get_feature_names_out()
        values = vector.data * classifier.coef_[0, vector.indices]
        order = np.argsort(-np.abs(values))[:top_k]
        return [{'term': str(names[vector.indices[i]]), 'contribution': float(values[i])}
                for i in order]

    def supported(self, text: str) -> bool:
        """Conservative English-script/vocabulary guard, not language detection."""
        clean = normalize(text)
        letters = [c for c in clean if c.isalpha()]
        ascii_share = sum(c.isascii() for c in letters) / max(1, len(letters))
        return ascii_share >= 0.8 and self.pipeline.named_steps['tfidf'].transform([clean]).nnz > 0


def train_engine() -> SentimentEngine:
    frame, audit = load_benchmark()
    train, val, _ = split_benchmark(frame)
    candidates = []
    fitted = []
    for c in [0.25, 1.0, 4.0]:
        model = make_model(c)
        model.fit(train.text, train.label)
        score = f1_score(val.label, model.predict(val.text), average='macro')
        candidates.append({'C': c, 'validation_macro_f1': float(score)})
        fitted.append(model)
    best = max(range(len(candidates)), key=lambda i: candidates[i]['validation_macro_f1'])
    model = fitted[best]
    probabilities = model.predict_proba(val.text)[:, 1]
    confidence = np.maximum(probabilities, 1 - probabilities)
    predictions = (probabilities >= 0.5).astype(int)
    supported = np.array([SentimentEngine(model, 0.5, {}).supported(t) for t in val.text])
    tradeoffs = []
    for threshold in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
        accepted = (confidence >= threshold) & supported
        tradeoffs.append({'threshold': threshold, 'coverage': float(accepted.mean()),
                         'accuracy': float(accuracy_score(val.label[accepted], predictions[accepted]))
                         if accepted.any() else None})
    eligible = [x for x in tradeoffs if x['accuracy'] is not None
                and x['accuracy'] >= 0.85 and x['coverage'] >= 0.30]
    # If no threshold meets the target, route everything to manual review.
    threshold = max(eligible, key=lambda x: x['coverage'])['threshold'] if eligible else 1.01
    return SentimentEngine(model, threshold, {
        'candidates': candidates, 'selected_C': candidates[best]['C'],
        'threshold': threshold, 'threshold_target': 'validation accuracy >= .85 and coverage >= .30',
        'threshold_tradeoffs': tradeoffs, 'data_audit': audit,
        'split_sizes': {'train': len(train), 'validation': len(val), 'test': len(frame)-len(train)-len(val)},
        'seed': 42, 'refit_on_validation': False,
    })
