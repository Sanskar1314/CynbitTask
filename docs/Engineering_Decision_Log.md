# Engineering Decision Log

Decision chronology: research/design choices were recorded in docs/04_Technical_Design.md at commit 6ac1fd5, before model code. The explanations below expand those choices and record observed revisions; they do not claim unperformed experiments. Date: 2026-10-16.

## 1. Model choice: sparse logistic regression

**WHAT:** Learn binary sentiment from TF-IDF word unigrams and bigrams.

**WHY:** The task has small labelled text data and needs fast, explainable scores.

**HOW:** Pipeline fits vocabulary/IDF and L2 logistic weights on training only. C is chosen from 0.25, 1 and 4 using validation macro-F1.

**ALTERNATIVES:** Naive Bayes is evaluated; transformers/LLMs were considered but not executed.

**DECISION:** Before test evaluation, choose logistic regression for probability outputs and exact feature contributions. After evaluation, retain this prototype without claiming it beats Naive Bayes: NB test F1 is higher, logistic Brier is lower. No post-test retuning.

**INPUT:** Normalized sentence strings and 0/1 training labels.

**PROCESSING:** Sparse x -> weighted sum z -> sigmoid probability p.

**OUTPUT:** Positive probability, suggested label and explainable contributions.

**EXAMPLE:** 'Terrible food and rude service.' receives negative sentiment, with 'terrible' and 'rude' lowering positive log-odds.

**LIMITATIONS:** Local word patterns miss sarcasm, implicit context and multilingual meaning; probability is not guaranteed correctness.

## 2. Dataset choice: public benchmark plus separate synthetic demo

**WHAT:** Use UCI Sentiment Labelled Sentences for evaluation; authored fictional rows for UI demonstration.

**WHY:** No authentic Cynbit reviews or labels were available. Licensed public labels allow a real experiment.

**HOW:** Download three named raw files and record hashes, DOI, access date and CC BY 4.0 attribution.

**ALTERNATIVES:** Scraped reviews lack verified permission/labels; entirely synthetic training would weaken validity.

**DECISION:** Keep benchmark and demo provenance visibly separate. No claim that these are Revio records.

**INPUT:** Public archive and manually authored sample CSV.

**PROCESSING:** Parse labelled records; validate demo schema independently.

**OUTPUT:** Reproducible corpus and an 18-row interactive demonstration.

**EXAMPLE:** Jaipur East (fictional) is a sample location, never a company client claim.

**LIMITATIONS:** Old balanced English sentences do not match natural review prevalence, languages or current products.

## 3. Preprocessing and parsing

**WHAT:** Canonicalize Unicode/whitespace, redact contact patterns, preserve negation and remove duplicate benchmark text.

**WHY:** Stable representations reduce noise; duplicates can inflate test estimates; negation changes sentiment.

**HOW:** normalize() uses NFKC and lowercase. Hash canonical text, remove conflicts, retain one copy. Raw parsing joins continuation lines until the final-tab label.

**ALTERNATIVES:** CSV quote parsing can misread raw quotation marks. Dropping stop words can remove important 'not' terms. Stemming adds complexity without an established need.

**DECISION:** Initial smoke testing found two multiline IMDb records and punctuation-only examples. The parser was corrected to preserve all 3,000 labelled records before deduplication. Runtime validation remains stricter for new user input.

**INPUT:** Raw labelled text or a review string.

**PROCESSING:** Normalize -> redact -> hash/deduplicate for benchmark only.

**OUTPUT:** 2,979 unique benchmark rows, 21 removed duplicates and zero conflicting rows.

**EXAMPLE:** '  Not GOOD! ' becomes 'not good!', preserving the negation word.

**LIMITATIONS:** Original group IDs are missing; near duplicates can remain. Contact regexes miss names and may redact number patterns that are not personal.

## 4. Architecture and dependencies

**WHAT:** One local Streamlit process with modular Python services.

**WHY:** The assessment needs a reliable demo with little infrastructure overhead.

**HOW:** app/app.py calls src/data.py, src/model.py and src/service.py. Streamlit caches a model trained only on the public split.

**ALTERNATIVES:** FastAPI plus a separate frontend, vector database, hosted inference, orchestration framework.

**DECISION:** These add deployment work without improving the selected narrow workflow. Pin direct dependencies and record the environment.

**INPUT:** Local code, public raw data and user review text.

**PROCESSING:** Initialize model once, handle per-session input, render outputs.

**OUTPUT:** Browser UI and downloadable CSV.

**EXAMPLE:** A laptop can run the full demo without an API key or downloaded neural weights.

**LIMITATIONS:** Local app has no authentication or tenant isolation; a production service requires additional design.

## 5. Training and evaluation separation

**WHAT:** Fixed 60/20/20 train/validation/test split stratified by source and label.

**WHY:** Training fit, model selection and final estimation serve different purposes.

**HOW:** Seed 42; train-only IDF and classifier; validation C/threshold selection; one held-out report. Save IDs and hashes for every split.

**ALTERNATIVES:** A single random split with test tuning would bias the estimate; cross-validation is useful but unnecessary for this small candidate grid and bounded assessment.

**DECISION:** Preserve the fitted training model without refitting validation so the selected threshold remains tied to the same model. Add separate leave-Yelp-out stress testing.

**INPUT:** Deduplicated text, source and labels.

**PROCESSING:** Partition -> fit candidates -> select -> freeze -> evaluate.

**OUTPUT:** metrics.json, predictions, errors and split_manifest.csv.

**EXAMPLE:** C=4 wins validation F1, but its test F1 is 0.792 versus NB's 0.804; the report preserves this outcome.

**LIMITATIONS:** Small validation/test sets; hidden grouping; bootstrap interval conditions on one trained model.

## 6. Abstention and support checks

**WHAT:** Route uncertain or unsupported inputs for manual review.

**WHY:** A forced binary answer hides uncertainty and unsupported language.

**HOW:** confidence=max(p,1-p); threshold grid 0.50 to 0.90. Select highest validation coverage meeting accuracy>=0.85 and coverage>=0.30. Require >=80% ASCII letters and a nonzero TF-IDF vector. No eligible threshold means 1.01, forcing abstention.

**ALTERNATIVES:** Always classify, fixed arbitrary confidence, or a trained language detector.

**DECISION:** Use a simple transparent guard and validation criterion; label it a heuristic, not language detection or calibrated certainty.

**INPUT:** Review, features and model probability.

**PROCESSING:** Check representation and threshold.

**OUTPUT:** Positive/negative suggestion or 'uncertain'.

**EXAMPLE:** The Hindi demo abstains even if the model's intercept produces a numeric probability.

**LIMITATIONS:** Romanized Hindi and other Latin-script languages may pass. Test accepted accuracy 82.5% misses the 85% target. Uncertain is not neutral.

## 7. Policy rules and explanations

**WHAT:** Keyword themes/safety flags, explicit queue ordering and feature contributions.

**WHY:** Operators should understand what is learned and what is prescribed by policy.

**HOW:** Regex themes can overlap. Safety mentions override queue priority. Remaining order: uncertainty, negative, routine. Explanations use w_i*x_i.

**ALTERNATIVES:** Learned urgency or aspect sentiment needs dedicated labels. LLM rationale can sound convincing without matching the classifier.

**DECISION:** Use auditable heuristics without calling them ML. Preserve false-positive examples in the demo.

**INPUT:** Redacted text and sentiment outputs.

**PROCESSING:** Match patterns, assign queue, rank, calculate contributions.

**OUTPUT:** Priority, themes, reasons and evidence table.

**EXAMPLE:** 'There was no injury' triggers inspection because the policy sees 'injury'; the UI explicitly requires context verification.

**LIMITATIONS:** Negation, topic ambiguity, spurious feature associations; no validated urgency accuracy or causal explanation.

## 8. Application integration and error handling

**WHAT:** Bounded CSV schema, stable review IDs, user-facing errors and formula-safe export.

**WHY:** The model is useful only if malformed input fails clearly and exports are reviewable.

**HOW:** Require four columns, valid ISO dates, nonblank/unique IDs and bounded strings. Reject entire invalid upload. Redact metadata as well as text. Reject ID collisions after redaction. Escape formula prefixes in custom exports and displayed tables.

**ALTERNATIVES:** Silently dropping bad rows obscures coverage. Rendering user text as HTML adds risk. Automatically truncating reviews changes meaning.

**DECISION:** Fail explicitly with corrective instructions. Use Streamlit text/dataframe rendering, not raw user HTML.

**INPUT:** Text or UTF-8 bytes.

**PROCESSING:** Decode -> schema check -> type/content validation -> redaction -> service.

**OUTPUT:** Validated rows or a clear ValueError shown in the UI.

**EXAMPLE:** 2026-02-30 is rejected as an impossible date; a missing text column produces the required-column message.

**LIMITATIONS:** CSV-only ingestion; no partial batch recovery; redaction is incomplete and the browser still sees entered data.

## 9. Deployment and measurement gates

**WHAT:** Localhost demo and documented future supervised pilot.

**WHY:** No production credentials, tenant model or target-domain evidence exists.

**HOW:** Bind Streamlit to 127.0.0.1, test health endpoint and app flow; keep public training data in Git; no uploaded data logging.

**ALTERNATIVES:** Public hosting would require authorization and additional controls; automatic replies would create a different risk profile.

**DECISION:** Complete local deliverables and Git synchronization; do not submit or deploy externally. Keep business benefit hypothetical until measured.

**INPUT:** Requirements, corpus and local Python runtime.

**PROCESSING:** Install -> test -> evaluate -> run -> inspect.

**OUTPUT:** Functional demo and reproducible evidence package.

**EXAMPLE:** The server's /_stcore/health returns 'ok', while Streamlit AppTest verifies real interaction separately.

**LIMITATIONS:** Health alone does not prove inference. Model-only timing excludes UI and policy processing. Container configuration remains untested unless explicitly executed.
