# Model card: Revio Signal Desk

Version: assessment v1, 2026-10-16. Owner context: independent internship assessment; not an official Cynbit production model.

Intended use: supervised demonstration of English binary sentiment and reviewable routing. Not intended for automatic replies, emergency detection, personnel evaluation, tenant decisions or autonomous business actions.

Architecture: TF-IDF words/bigrams, min_df=2, sublinear TF, max_features=20000, Unicode accent stripping; L2 logistic regression C=4, max_iter=1000, random_state=42. Model and vectorizer fitted only on 1,787 training records. No persisted pickle is loaded.

Data: public UCI Sentiment Labelled Sentences (CC BY 4.0); details in data/DATA_CARD.md. Validation/test each 596. Exact normalized duplicate controls applied; unknown group/near-duplicate dependence remains.

Metrics: test macro-F1 .791944, accuracy .791946, negative recall .788591, negative precision .793919, Brier .138399. NB test F1 .803691. Confidence threshold .55 selected on validation; test accepted accuracy .825188, coverage .892617. Target .85 not met on test. Row-bootstrap F1 interval [.756674,.822179] excludes training uncertainty. Independent source-transfer F1 .766432.

Human oversight: all predictions are suggestions. Unsupported or low-confidence records become uncertain. No neutral class. Safety mentions and topics are explicit rules, not capabilities of the sentiment classifier.

Known failure modes: negation scope, sarcasm, implicit context, spelling variation, Latin-script non-English inputs, historical domain mismatch, probability miscalibration and keyword false positives. Demographic fairness cannot be measured from this corpus; no demographic attributes are inferred.

Next gate: permissioned target-domain annotation with neutral/mixed labels, language slices, business/time holdout, calibration assessment and an operator study. Do not tune repeatedly on this released test set.
