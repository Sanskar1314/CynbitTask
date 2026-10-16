# Pre-implementation technical design

Decision recorded before model/application code, 2026-10-16.

Build Revio Signal Desk as a local Streamlit workbench backed by a Python service. User enters one review or supplies a UTF-8 CSV with review_id, text, location and date. Validate bounded input, redact common contact details, preserve negation, predict positive/negative sentiment, flag low confidence or unsupported text, expose influential n-grams, and aggregate review queues by branch and transparent keyword themes.

Use TF-IDF word unigrams/bigrams and L2 logistic regression. This fits a small labelled text dataset, works on CPU, supports probabilities and exact linear contribution explanations. Compare majority and Multinomial Naive Bayes baselines; choose C on validation only. No LLM, prompt, embedding service or vector database is needed. Neutral is not a trained class: uncertain means abstention, not neutral.

Data: UCI Sentiment Labelled Sentences (CC BY 4.0), three sources. Parse each line from its final tab; do not use quote-aware CSV parsing for this raw format. Normalize and remove duplicate text before splitting; remove conflicting labels. Seed 42; 60/20/20 train/validation/test stratified by source and label. Fit vocabulary only on train. Select regularization and confidence threshold on validation; freeze before test. Add leave-Yelp-out domain-shift experiment. Demo branch/date records are explicitly synthetic and separate from the benchmark.

Functional: single/batch inference, confidence and reasons, queue export, location/theme summaries, model evidence panel, errors on invalid input. Nonfunctional: no paid APIs, deterministic splits, bounded uploads (2 MB/1000 rows), local execution, no uploaded-data persistence, startup failure instructions. Priority is a documented policy heuristic, not a learned urgency model. Safety keywords trigger manual inspection without claiming a verified crisis.

Evaluation: macro-F1, accuracy, negative precision/recall, confusion matrix, Brier score, selective coverage/accuracy, validation threshold tradeoff, cold training and warm inference time. Bootstrap intervals on held-out predictions; domain-shift result reported separately. Unit, integration and Streamlit AppTest checks plus HTTP startup health.

Architecture: local CSV/text -> schema validation -> redaction -> train-fitted vectorizer -> logistic model -> abstention/policy routing -> explainable table/charts/export. Runtime has no external API integrations. Training script downloads a public archive once; normal app runs from bundled attributed source text. Model trained locally from the fixed training split and cached in process; no untrusted pickle loading.

Production proposal (not implemented): authenticated Revio API adapter, tenant-isolated storage, consent/retention controls, audit trails, multilingual validation, observability and controlled pilot. Do not deploy publicly or auto-post replies.
