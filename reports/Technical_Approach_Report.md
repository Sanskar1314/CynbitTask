# Technical Approach Report
## Revio Signal Desk

Reproducible supervised NLP and human-reviewed routing | 16 October 2026

## 1. Problem Statement

Evaluate whether a compact, explainable sentiment service can support a Revio review triage workflow. Cynbit's product page motivates the adjacency; no access to its implementation, customers or internal review data was available. This project is an independent proof of concept.

## 2. Project Objectives

Deliver working input-to-output inference, reproducible comparisons, clear uncertainty handling and a demo that can be explained in an interview. Separate model decisions from policy rules. Establish evidence for a later pilot, without claiming production readiness.

## 3. Functional Requirements

- Accept individual text and UTF-8 CSV files with review_id, text, location and date.
- Validate fields, dates, row limits, duplicate IDs and text length; report actionable errors.
- Redact common contact patterns; infer binary sentiment and expose exact linear contributions.
- Abstain for insufficient confidence, unsupported script or zero recognized vocabulary.
- Assign explicit review priorities and keyword themes; summarize locations.
- Filter and export a queue; display model evidence and synthetic-data labels.

## 4. Nonfunctional Requirements

Local CPU execution with no API keys, bounded uploads (2 MB, 1,000 rows, 5,000 characters per review), train-only vocabulary fitting, deterministic seed, no application persistence of uploaded reviews and no external posting. Measured timing is reported below; it is not an SLA. The UI caches only the public-data-trained model across sessions.

## 5. Proposed AI/ML Solution

TF-IDF word unigrams and bigrams feed L2 logistic regression. Validation selects regularization from C in {0.25, 1, 4}. The selected C is 4.0. A 0.55 confidence threshold maximizes validation coverage among candidates meeting 85% accuracy and 30% coverage. Unsupported input always abstains. A failed threshold search would use 1.01 and abstain on every review.

## 6. System Architecture

![System architecture](../assets/diagrams/architecture.png)

The actual runtime is browser -> local Streamlit process -> shared validation -> cached sentiment pipeline -> policy routing -> table/chart/export. There is no database, background agent, LLM or external review API in the implemented path. Mermaid sources for all diagrams are in assets/diagrams.

## 7. Technology Stack

Python 3.12.14; scikit-learn 1.9.1; NumPy 2.3.5; pandas 2.2.3; SciPy 1.18.1; Streamlit 1.66.0; pytest 9.1.1. PDF generation uses ReportLab; text/visual verification uses pypdf and pypdfium2. Exact tested direct dependencies are pinned in requirements files. Transitive versions are recorded in evaluation/environment.txt; a fresh environment installation is the reproducibility check.

## 8. Technology Selection Rationale

scikit-learn provides transparent sparse linear models and shared Pipeline preprocessing. Streamlit delivers useful interaction with limited frontend complexity. pandas handles tabular ingestion and summaries. CPU training avoids paid services and large pretrained weights. Standard-library downloads and fixed archive filenames reduce dependencies. No orchestration framework is required for a deterministic single-process flow.

## 9. Dataset Description

UCI Sentiment Labelled Sentences (Kotzias, 2015; CC BY 4.0), originally 3,000 binary-labelled English sentences from Amazon, IMDb and Yelp. After canonical-text deduplication: 2,979 rows; 21 duplicate rows removed and no conflicting-label rows found. Training/validation/test sizes: 1,787/596/596. The independent 18-row synthetic demo contains fictional locations and dates and is excluded from accuracy measurement.

## 10. Data Collection

scripts/download_data.py fetches the public UCI archive with a timeout, reads only three allowlisted filenames and records SHA-256 hashes. Raw texts are bundled with attribution in data/DATA_CARD.md. No customer data was scraped, and no production connectors were used. Dataset provenance is in data/raw/manifest.json.

## 11. Data Preprocessing

![Preprocessing](../assets/diagrams/preprocessing.png)

The loader joins continuation lines until a final-tab label; this preserves two multiline IMDb records. Punctuation-only labelled sentences remain in the benchmark even though new UI inputs must contain letters. Normalize Unicode NFKC, apostrophes, whitespace and lowercase; redact common email/phone patterns. Retain stop words to preserve negation. Hash canonical text globally, exclude conflicting duplicates, then keep one exact duplicate. Split by source+label with seed 42. Fit vocabulary and IDF only on training rows.

Original review-author and business IDs are absent, so group-level and near-duplicate leakage cannot be excluded. Global exact deduplication before splitting is a defensive control, not a complete guarantee.

## 12. Model Selection

No pretrained model or fine-tuning is required. Logistic regression provides a compact classifier with directly inspectable weights and probability outputs. Validation macro-F1 for C=0.25/1/4 was 0.7970/0.8205/0.8272. L2 regularization, limited feature count (20,000), min_df=2 and held-out validation constrain overfitting. The model is not refitted on validation after selection, preserving the threshold's relationship to its fitted weights.

## 13. Alternative Approaches

A majority baseline establishes class-prior performance. Multinomial Naive Bayes with matching TF-IDF preprocessing is a meaningful cheap text baseline. Its held-out macro-F1 is slightly better; this is reported without changing the test-selected story. Logistic regression remains the preselected prototype model because of probability behavior and exact linear explanations, not superior test F1. A new comparison of calibrated Naive Bayes would require a fresh validation protocol and another untouched test set.

A transformer might improve contextual understanding but adds model downloads and computational complexity without target-domain labels. An LLM adds cost, nondeterminism and potential unsupported output. Keyword-only sentiment cannot learn weighted domain associations. Keywords are retained only for explicit operational policy, where their limitations are visible.

## 14. Model Architecture

For a review, TF-IDF converts observed words and adjacent word pairs into a sparse vector x. The classifier computes z = b + sum(w_i * x_i), and positive probability p = 1 / (1 + exp(-z)). Negative probability is 1-p. Confidence is max(p, 1-p). Values are model estimates, not calibrated guarantees.

Each explanation displays the largest absolute w_i*x_i contributions. Their full sum plus the intercept reconstructs the decision score, verified by a test. Positive contributions support positive sentiment; negative contributions support negative sentiment. They reflect correlations and can expose spurious features such as conjunctions.

## 15. Prompt Engineering

Not applicable: the implemented system has no generative language model or prompts. No fabricated prompt pipeline is included. The text entered by a user is classified as data and is never executed as an instruction. Future response drafting would need a separate approved design and evaluation.

## 16. Inference Pipeline

![Inference](../assets/diagrams/inference.png)

Validate -> redact -> normalize -> TF-IDF -> probability -> support/confidence check -> sentiment or uncertain -> keyword themes/safety -> priority/reasons -> explanations. Safety mentions take first priority, then uncertain items, then accepted negative items, then routine positive items. Within each priority, higher confidence sorts first. This ordering is a transparent demo policy, not an optimized urgency ranking; low-confidence-first uncertainty routing is a possible later workflow experiment.

A script heuristic requires at least 80% ASCII among letters and at least one recognized vocabulary feature. It catches the Hindi demo and gibberish but is not language identification: romanized Hindi, Spanish and mixed languages can pass.

## 17. Integration Architecture

src/service.py separates the application from model and validation logic. Streamlit calls the service in-process. CSV export prefixes formula-like strings with an apostrophe. The displayed table is also sanitized so its built-in CSV download cannot bypass this protection. Input IDs that collide after redaction are rejected. Uploaded raw content is not written to disk by the app. Session memory and browser rendering still contain inputs during use.

External integrations: only the optional dataset download script accesses a public URL. No credentials, Google review sync, ticket creation, email or automatic response publishing are implemented. Future connectors would need authorization, idempotency, retries, quota handling and tenant scoping.

## 18. Evaluation Methodology

![Training and evaluation](../assets/diagrams/training.png)

Freeze candidate C values and threshold search on validation. Evaluate the selected model once on 596 held-out rows. Compare majority and Naive Bayes; report confusion matrices, negative precision/recall, macro-F1, accuracy and Brier score. Brier score is mean squared probability error (lower better); it does not by itself establish calibration. Compute 1,000 row-bootstrap resamples for a conditional 95% macro-F1 interval. This interval excludes model retraining uncertainty and may be optimistic if hidden grouping exists.

A separate domain-shift experiment fixes C=1, trains on all non-Yelp records and tests on all Yelp records. It never selects parameters on Yelp and does not replace the primary held-out estimate. Measure 20 warm batch calls, excluding UI/rendering and policy cost. Synthetic policy cases test routing semantics, not statistical urgency accuracy.

## 19. Experimental Results

| Model | Accuracy | Macro-F1 | Negative recall | Brier score |
|---|---:|---:|---:|---:|
| Logistic regression | 0.7919 | 0.7919 | 0.7886 | 0.1384 |
| TF-IDF Naive Bayes | 0.8037 | 0.8037 | 0.8054 | 0.1504 |
| Majority | 0.5000 | 0.3333 | 1.0000 | 0.2500 |

Logistic test confusion matrix (rows true negative/positive; columns predicted negative/positive): [[235, 63], [61, 237]]. There are 124 errors, all exported to evaluation/errors.csv. Negative precision is 0.7939. Bootstrap macro-F1 interval: [0.7567, 0.8222].

Accepted subset: 532/596 predictions (89.26% coverage); accuracy 82.52%. Validation accepted accuracy was 86.81%, so the target does not generalize to test. Threshold was not retuned on test. Domain-transfer macro-F1 is 0.7664 on 996 Yelp sentences. Source-specific test F1: Amazon 0.8283, IMDb 0.7737, Yelp 0.7738.

Training plus validation selection took 0.197 seconds on the recorded local environment after imports. Median warm inference for 596 texts was 5.83 ms; p95 5.95 ms across 20 repetitions. These exclude upload parsing, policy explanation loops and browser rendering. No throughput SLA or business saving is established.

Verified tests cover raw record counts, split disjointness, normalization, malformed files, inference polarity, contribution reconstruction, unsupported text, negated safety mentions, CSV formula protection, batch integration and Streamlit interaction. Actual test records are in evaluation/Test_Report.md.

## 20. Security and Privacy

Use localhost binding, bounded uploads, partial email/phone redaction and formula-safe exports. No API keys or serialized model loading. The UI has no raw-user HTML rendering. The CSS string is static. No authentication, tenant isolation, audit database, encryption-at-rest policy or complete PII detection is implemented; deployment beyond local use requires these controls. Safety terms are mentions, never verified allegations. See the opportunity report's official privacy/governance sources for pilot planning.

## 21. Scalability

Sparse inference is inexpensive at this corpus size. Current batch service loops over rows and computes explanations per review before discarding them for batch display, so model-only timing overstates end-to-end speed. Production should vectorize batch scoring, compute explanations on demand and profile with realistic review lengths. Shared model caching is safe for public training data; user results must remain tenant-separated. A database/queue is unnecessary for this bounded local assessment.

## 22. Deployment Strategy

![Implemented deployment](../assets/diagrams/deployment.png)

Create a Python 3.12 virtual environment, install requirements, run pytest and scripts/evaluate.py, then start Streamlit bound to 127.0.0.1. Raw data is included, so runtime is offline. Report dependencies are separate. A container configuration is provided for a possible local deployment but is labelled untested unless Docker is executed. No public deployment has been performed.

## 23. Execution Plan

Completed stages: identity research -> opportunity comparison -> design -> attributed dataset -> preprocessing fix -> model/routing -> evaluation -> UI -> verification -> documentation/PDF packaging. Git milestones preserve this sequence. The deadline is 18 October 2026 at 03:48 AM with timezone unverified; Asia/Kolkata is the documented planning assumption. No assessment submission is performed.

## 24. Production Roadmap

Gate 1: confirm feature gap and operator demand. Gate 2: acquire permissioned labels with two annotators and adjudication. Gate 3: compare calibrated classifiers and multilingual models using business/time-separated splits. Gate 4: shadow mode with operator corrections and failure monitoring. Gate 5: limited authenticated pilot only if error and time targets improve over manual baseline. Product owners must set acceptable urgent-review recall and alert burden; arbitrary demo thresholds are insufficient.

## 25. Limitations

No neutral class, target-customer labels, multilingual model, causal business evaluation, calibrated production confidence, learned urgency, learned aspect sentiment, persistent feedback capture or live Revio integration. Synthetic branch/date data cannot validate trends. Keyword safety matching can flag negated incidents. Old public data and hidden source grouping limit generalization. Baseline superiority on test is disclosed. The current model falls short of its selective accuracy development target.

## 26. Future Enhancements

Collect hard cases and independently annotated neutral/mixed reviews; evaluate expected calibration error and reliability diagrams; compare char n-grams and calibrated Naive Bayes; use business/time-separated target evaluation; add multilingual support; implement operator decisions and audited integrations. Reserve a new untouched holdout before iterating from observed test errors.

## Technical references

- Source data and license: https://doi.org/10.24432/C57604
- Text features: https://scikit-learn.org/stable/modules/feature_extraction.html
- Company context: https://www.cynbit.in/products
- Authorized future review API: https://developers.google.com/my-business/content/review-data
- Risk framework: https://www.nist.gov/itl/ai-risk-management-framework

Accessed 2026-10-16. Implementation-specific statements can be verified in src/, scripts/evaluate.py and tests/.
