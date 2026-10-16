"""Run: python -m streamlit run app/app.py"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
import streamlit as st
from src.data import read_reviews, safe_csv, safe_frame
from src.model import train_engine
from src.service import analyze_batch, analyze_review, location_summary

st.set_page_config(page_title='Revio Signal Desk', page_icon='◈', layout='wide')
st.markdown('''<style>
.block-container {padding-top:4rem;max-width:1400px}
[data-testid="stMetric"] {background:white;border:1px solid #e1e7ef;border-radius:12px;padding:16px}
h1 {letter-spacing:-1.3px} .stCaption {color:#52627a}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return train_engine()

with st.sidebar:
    st.markdown('### ◈ SIGNAL DESK')
    st.caption('CYNBIT / REVIO OPPORTUNITY PROTOTYPE')
    page = st.radio('Workspace', ['Review inbox', 'Inspect one review', 'Model evidence'])
    st.divider()
    st.markdown('**Local analysis. Human decisions.**')
    st.caption('English sentiment model. No paid API. Uploaded data stays in this session; it is not saved by the application.')
    st.caption('Contact-pattern redaction is partial. Avoid confidential data.')
    st.link_button('Research basis ↗', 'https://www.cynbit.in/products')

st.caption('REPUTATION INTELLIGENCE / ASSESSMENT DEMO')
st.title('Revio Signal Desk')
st.write('Turn customer feedback into a reviewable action queue.')
try:
    with st.spinner('Preparing the reproducible sentiment model…'):
        engine = get_engine()
except Exception as exc:
    st.error('Model could not start. Install requirements and verify data/raw; see README troubleshooting.')
    st.code(str(exc))
    st.stop()

if page == 'Review inbox':
    st.subheader('Your review inbox')
    st.caption('Inspect safety mentions, resolve uncertainty, then review sentiment. Priority and themes use explicit rules.')
    upload = st.file_uploader('Upload review CSV', type=['csv'], help='Columns: review_id, text, location, date (YYYY-MM-DD). Up to 1,000 rows / 2 MB.')
    st.download_button('Download sample CSV', (ROOT/'data/sample/reviews.csv').read_bytes(), 'sample_reviews.csv', 'text/csv')
    if upload is None:
        st.info('Showing 18 synthetic reviews across fictional locations. These are not Cynbit customer records.')
        raw = (ROOT/'data/sample/reviews.csv').read_bytes()
    else:
        raw = upload.getvalue()
    try:
        reviews = read_reviews(raw)
        with st.spinner('Scoring reviews and assembling reasons…'):
            results = analyze_batch(engine, reviews)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    a,b,c,d = st.columns(4)
    a.metric('Reviews', len(results))
    b.metric('Safety mentions', int(results.priority_rank.eq(0).sum()))
    c.metric('Uncertain', int(results.sentiment.eq('uncertain').sum()))
    d.metric('Negative signals', int(results.sentiment.eq('negative').sum()))
    st.caption('Safety mentions are keyword matches requiring investigation, not verified incidents. Uncertain is not a neutral class.')
    left,right = st.columns([2,1])
    with left:
        location = st.selectbox('Location', ['All locations'] + sorted(results.location.unique().tolist()))
    with right:
        priority = st.selectbox('Queue filter', ['All priorities'] + results.priority.unique().tolist())
    filtered = results.copy()
    if location != 'All locations': filtered = filtered[filtered.location == location]
    if priority != 'All priorities': filtered = filtered[filtered.priority == priority]
    st.dataframe(safe_frame(filtered)[['review_id','priority','sentiment','confidence','themes','text','location','reason']],
                 hide_index=True, width='stretch', column_config={
                     'confidence': st.column_config.ProgressColumn('Model confidence',min_value=0,max_value=1,format='%.2f'),
                     'text': st.column_config.TextColumn('Review',width='large'),
                     'reason': st.column_config.TextColumn('Why it is here',width='large')})
    st.download_button('Export filtered action queue', safe_csv(filtered), 'revio_action_queue.csv', 'text/csv')
    st.subheader('Location overview')
    summary = location_summary(results)
    st.bar_chart(summary.set_index('location')[['negative','uncertain','safety_mentions']])
    st.caption('Counts can overlap: a review may have both a safety mention and uncertain sentiment. This chart summarizes the full upload.')
    with st.expander('Inspect the model evidence for a review'):
        chosen = st.selectbox('Review ID', results.review_id.tolist())
        text = results.loc[results.review_id == chosen, 'text'].iloc[0]
        st.write(text)
        explanation = engine.explain(text)
        st.dataframe(pd.DataFrame(explanation), hide_index=True)
        st.caption('Positive contributions raise positive log-odds; negative contributions lower them. Correlations are not causes.')
elif page == 'Inspect one review':
    st.subheader('Inspect a single review')
    with st.form('single_review'):
        text = st.text_area('Review text', 'The food was cold and the service was terrible.', max_chars=5000, height=140)
        submitted = st.form_submit_button('Analyze review', type='primary')
    if submitted:
        try:
            result = analyze_review(engine, text)
            a,b,c = st.columns(3)
            a.metric('Suggested sentiment', result['sentiment'].title())
            b.metric('Model confidence', f"{result['confidence']:.1%}")
            c.metric('Queue', str(result['priority_rank']+1))
            st.subheader(result['priority'])
            st.write(result['reason'])
            st.write('**Themes (keyword rules):** ' + result['themes'])
            st.write('**Redacted text:**')
            st.text(result['text'])
            st.dataframe(pd.DataFrame(result['explanation']), hide_index=True)
            st.caption('Model probability is not a guarantee. Every result requires human confirmation. No reply is generated or posted.')
        except ValueError as exc:
            st.error(str(exc))
else:
    st.subheader('Evidence before automation')
    st.write('TF-IDF word n-grams → logistic regression → validation-selected abstention → explicit routing policy.')
    path = ROOT/'evaluation/metrics.json'
    if path.exists():
        metrics = json.loads(path.read_text())
        a,b,c,d = st.columns(4)
        a.metric('Test macro-F1', f"{metrics['test']['macro_f1']:.3f}")
        b.metric('Negative recall', f"{metrics['test']['negative_recall']:.1%}")
        c.metric('Accepted coverage', f"{metrics['selective']['coverage']:.1%}")
        d.metric('Accepted accuracy', f"{metrics['selective']['accuracy']:.1%}")
        comparison = [{'Model':'Logistic regression', **metrics['test']}]
        comparison += [{'Model':name, **values} for name,values in metrics['baselines'].items()]
        st.dataframe(pd.DataFrame(comparison)[['Model','accuracy','macro_f1','negative_recall','brier_score']],hide_index=True)
        st.warning('Measured on a small curated English public corpus. These are not Revio production results. Accepted means a sentiment suggestion passes the threshold; it never authorizes an automatic action.')
        st.write(f"Hold out all Yelp data: macro-F1 {metrics['domain_shift']['macro_f1']:.3f}. This is a separate domain-shift stress experiment.")
    else:
        st.info('Run python scripts/evaluate.py to generate held-out metrics.')
    st.write(f"Selected C: {engine.selection['selected_C']}; confidence threshold: {engine.threshold:.2f}.")
    st.dataframe(pd.DataFrame(engine.selection['threshold_tradeoffs']),hide_index=True)
    st.caption('Threshold selected on validation only to maximize coverage subject to ≥85% accuracy and ≥30% coverage. These are development targets, not service guarantees.')
    st.markdown('**Limits:** binary English sentiment; no trained neutral class; sarcasm and domain shift; approximate contact redaction; keyword-only themes and safety flags; no authenticated Revio integration.')
