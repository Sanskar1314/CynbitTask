import io
import numpy as np
import pandas as pd
import pytest
from src.data import load_benchmark, normalize, read_reviews, safe_csv, split_benchmark, validate_text, ROOT
from src.model import train_engine
from src.service import analyze_batch, analyze_review, location_summary

@pytest.fixture(scope='session')
def engine():
    return train_engine()

def test_benchmark_record_integrity():
    data, audit = load_benchmark()
    assert audit['raw_rows'] == 3000
    assert len(data) == 2979
    train, val, test = split_benchmark(data)
    for a,b in [(train,val),(train,test),(val,test)]:
        assert not set(a.text_hash) & set(b.text_hash)
    assert set(data.label) == {0,1}

def test_normalization_preserves_negation_and_redacts():
    assert normalize('  Not GOOD! a@example.com +91 9876543210 ') == 'not good! [email] [phone]'

@pytest.mark.parametrize('value', ['', '  ', None, 12, '12345', 'a'*5001])
def test_invalid_text(value):
    with pytest.raises(ValueError): validate_text(value)

@pytest.mark.parametrize('raw', [b'', b'x\n1', b'\xff', b'x'*2000001,
    b'review_id,text,location,date\na,good,b,2026-02-30',
    b'review_id,text,location,date\na,good,b,2026-01-01\na,bad,b,2026-01-02',
    b'review_id,text,location,date\na,,b,2026-01-01',
    b'review_id,text,location,date\na,good,b,01/02/2026'])
def test_invalid_csv(raw):
    with pytest.raises(ValueError): read_reviews(raw)

def test_model_fit_and_polarity(engine):
    p = engine.probabilities(['Excellent wonderful amazing!', 'Terrible awful waste of money.'])
    assert 0 <= p[1] < .5 < p[0] <= 1
    assert engine.selection['selected_C'] in [.25,1.,4.]

def test_explanation_reconstructs_logit(engine):
    text = 'The food was terrible and the service was slow.'
    contributions = engine.explain(text, top_k=100000)
    score = sum(x['contribution'] for x in contributions) + engine.pipeline.named_steps['classifier'].intercept_[0]
    assert 1 / (1+np.exp(-score)) == pytest.approx(engine.probabilities([text])[0])

def test_unknown_and_hindi_abstain(engine):
    for text in ['zxqvpk zqqxx', 'खाना अच्छा था।']:
        assert analyze_review(engine,text)['sentiment'] == 'uncertain'

def test_safety_is_explicit_policy_even_when_negated(engine):
    result = analyze_review(engine,'There was no injury and everyone was friendly.')
    assert result['priority_rank'] == 0
    assert 'verify context' in result['reason']

def test_batch_end_to_end(engine):
    data = read_reviews((ROOT/'data/sample/reviews.csv').read_bytes())
    results = analyze_batch(engine,data)
    assert len(results) == 18
    assert results.priority_rank.is_monotonic_increasing
    assert location_summary(results).reviews.sum() == 18
    assert '9876543210' not in results.to_csv()
    assert set(results.review_id) == set(data.review_id)

def test_csv_formula_protection():
    exported = safe_csv(pd.DataFrame({'text':['=2+2',' @SUM(A1)','normal']})).decode()
    assert "'=2+2" in exported and "' @SUM(A1)" in exported

def test_schema_row_limit():
    raw = pd.DataFrame({'review_id':range(1001),'text':'good','location':'a','date':'2026-01-01'}).to_csv(index=False).encode()
    with pytest.raises(ValueError): read_reviews(raw)
