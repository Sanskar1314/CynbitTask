"""Reproduce validation selection, untouched test metrics and domain-shift stress test."""
from __future__ import annotations
import json
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from src.data import load_benchmark, read_reviews, split_benchmark
from src.model import make_model, train_engine
from src.service import analyze_batch


def metrics(y, p):
    pred = (np.asarray(p) >= .5).astype(int)
    return {'accuracy': float(accuracy_score(y, pred)),
            'macro_f1': float(f1_score(y, pred, average='macro')),
            'negative_precision': float(precision_score(y, pred, pos_label=0, zero_division=0)),
            'negative_recall': float(recall_score(y, pred, pos_label=0)),
            'brier_score': float(brier_score_loss(y, p)),
            'confusion_matrix_labels_0_1': confusion_matrix(y, pred, labels=[0, 1]).tolist()}


def main():
    out = ROOT / 'evaluation'
    out.mkdir(exist_ok=True)
    start = time.perf_counter()
    engine = train_engine()
    training_seconds = time.perf_counter() - start
    data, audit = load_benchmark()
    train, val, test = split_benchmark(data)
    pd.concat([part.assign(split=name) for name, part in [('train', train), ('validation', val), ('test', test)]])[
        ['id', 'text_hash', 'source', 'label', 'split']].to_csv(out/'split_manifest.csv', index=False)
    p = engine.probabilities(test.text.tolist())
    accepted = (np.maximum(p, 1-p) >= engine.threshold) & np.array([engine.supported(t) for t in test.text])
    majority = DummyClassifier(strategy='prior').fit(np.zeros((len(train), 1)), train.label)
    nb = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True,
                                       max_features=20000, strip_accents='unicode'), MultinomialNB())
    nb.fit(train.text, train.label)
    test_results = test.copy()
    test_results['probability_positive'] = p
    test_results['prediction'] = (p >= .5).astype(int)
    test_results['accepted'] = accepted
    test_results.to_csv(out/'test_predictions.csv', index=False)
    test_results[test_results.label != test_results.prediction].to_csv(out/'errors.csv', index=False)
    rng = np.random.default_rng(42)
    scores = []
    labels = test.label.to_numpy()
    for _ in range(1000):
        indices = rng.integers(0, len(test), len(test))
        scores.append(f1_score(labels[indices], (p[indices] >= .5).astype(int), average='macro'))
    # Stress experiment uses no Yelp examples in either training or selection.
    source_train = data[data.source != 'yelp']
    source_test = data[data.source == 'yelp']
    transfer = make_model(1.0).fit(source_train.text, source_train.label)
    times = []
    for _ in range(20):
        start = time.perf_counter()
        engine.probabilities(test.text.tolist())
        times.append(time.perf_counter() - start)
    result = {'generated_at': datetime.now().astimezone().isoformat(),
              'environment': {'python': platform.python_version(), 'sklearn': sklearn.__version__,
                              'platform': platform.platform()},
              'data_audit': audit, 'selection': engine.selection,
              'test': metrics(test.label, p),
              'bootstrap_macro_f1_95_percentile': np.quantile(scores, [.025, .975]).tolist(),
              'baselines': {'majority': metrics(test.label, majority.predict_proba(np.zeros((len(test),1)))[:,1]),
                            'tfidf_naive_bayes': metrics(test.label, nb.predict_proba(test.text)[:,1])},
              'selective': {'coverage': float(accepted.mean()), 'accepted_count': int(accepted.sum()),
                            'accuracy': float(accuracy_score(labels[accepted], (p[accepted]>=.5).astype(int))) if accepted.any() else None},
              'per_source': {s: metrics(test.label[test.source==s], p[test.source.to_numpy()==s]) for s in sorted(test.source.unique())},
              'domain_shift': {'train_sources': ['amazon', 'imdb'], 'test_source': 'yelp', 'C_fixed': 1.0,
                               'train_count': len(source_train), 'test_count': len(source_test),
                               **metrics(source_test.label, transfer.predict_proba(source_test.text)[:,1])},
              'timing': {'training_selection_seconds': training_seconds, 'warm_batch_size': len(test),
                         'warm_batch_median_seconds': float(np.median(times)),
                         'warm_batch_p95_seconds': float(np.quantile(times, .95))}}
    (out/'metrics.json').write_text(json.dumps(result, indent=2)+'\n')
    sample = read_reviews((ROOT/'data/sample/reviews.csv').read_bytes())
    analyze_batch(engine, sample).to_csv(out/'synthetic_demo_results.csv', index=False)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
