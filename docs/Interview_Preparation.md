# Interview Preparation Guide

Use these explanations only after reading the code and reproducing the demo. This project was developed with AI assistance; describe your own understanding and contribution honestly. Do not present fictional customer data, proposed pilots or tool-generated work as personal client experience.

## 30-second explanation

'I researched Cynbit and found that Revio already targets review intelligence. I built a local prototype that makes sentiment suggestions reviewable: it flags uncertainty, shows influential words and creates an explicit action queue. I trained a TF-IDF logistic classifier on a licensed public dataset and compared baselines. Test macro-F1 was 0.792; Naive Bayes was slightly better. That result is why I propose a supervised pilot, with no automatic customer replies.'

## Two-minute explanation

'Cynbit's website connects software services with Revio, TenantEase and Cynbit Studio. I compared six AI opportunities using impact, relevance, feasibility, data, demo quality and scalability. Review triage ranked highest under the assessment constraints because it has a direct product connection and accessible labelled data. I would first confirm whether Revio already offers an equivalent workflow.

The application accepts CSV or text, validates it, partially redacts contacts, and runs a real supervised classifier. TF-IDF captures words and adjacent pairs; logistic regression estimates sentiment. Low confidence and unsupported text route to uncertainty. Safety mentions and themes use clearly labelled rules. Explanations show feature contributions rather than generated rationales.

I removed duplicate benchmark sentences before fixed train/validation/test splits. C and the threshold were selected on validation. On 596 test sentences, macro-F1 was 0.792 and negative recall 0.789. Naive Bayes achieved 0.804 F1, while logistic regression had lower probability error. Accepted predictions reached 82.5% accuracy, below the validation target. The honest next step is permissioned multilingual evaluation and an operator study, not autonomous deployment.'

## Five-minute technical walkthrough

**0:00-0:45 — Problem and research.** Open company research and identify the official-domain cross-check. Explain that Revio already advertises AI and that feature-gap validation is still necessary. Show the weighted matrix, including the viable discovery-matcher alternative.

**0:45-1:30 — Data.** Show data/DATA_CARD.md and manifest. Explain 3,000 raw records, two multiline parser edge cases, 21 duplicates removed and 2,979 unique rows. Synthetic locations are UI examples only. Split 1,787/596/596 with seed 42 and source/label stratification.

**1:30-2:20 — Model.** Open make_model and train_engine. Describe train-only vocabulary/IDF, unigrams/bigrams, min_df=2, L2 penalty and C selection. Explain z=b+w*x, sigmoid and exact feature contributions. No LLM or prompt engineering is needed for this task.

**2:20-3:20 — Demonstration.** Show the inbox, the Hindi abstention and negated injury flag. Enter 'Terrible food and rude service.' in the single-review page. Explain why a literal safety policy can be wrong and why confidence does not guarantee correctness. Export a filtered queue.

**3:20-4:15 — Evaluation.** Open Model evidence. Compare all three baselines and the domain-shift result. State the shortfall in accepted accuracy. Explain why test-driven threshold adjustment would invalidate an untouched estimate.

**4:15-5:00 — Production path.** Discuss consented labels, multilingual/group-time validation, calibration, operator corrections, authentication and tenant isolation. Propose measuring time per correctly reviewed item and errors against manual review. Conclude with the next experimental decision, not an invented ROI.

## What matters to Cynbit

The proposed work is adjacent to Revio and potentially reusable in services engagements, but demand is a hypothesis. Its value is a cheap way to measure reliability and operator usefulness. Generic AI reply generation is already an advertised capability in the market, so the pitch should emphasize careful engineering and validation rather than novelty.

## Real problems encountered and resolved

The repository already existed, so it was reused. gh was absent and sandbox DNS blocked Git; approved Git network execution worked. A raw loader initially rejected punctuation-only labels and failed on two multiline IMDb records. Continuation-line parsing and separate benchmark/runtime validation preserved the intended 3,000 records. A pending smoke-test result was inspected after the first data commit; the parser correction was immediately committed and pushed. This is a real process mistake and its correction, not a fabricated success story.

The first model did not beat Naive Bayes on test F1. This was preserved in the report. The selected uncertainty threshold missed its test target; it was not tuned using test labels. Browser inspection exposed clipped top spacing; layout padding was corrected. Formula-safe display/export and redacted-ID collision checks strengthened input handling. Local server startup required approved loopback socket access.

## Actual error discussion

Examples in evaluation/errors.csv include a positive sentence containing 'not a weekly haunt' classified negative, an elongated spelling 'gooodd' missed by word features, and a negative context sentence about a gas station receiving a high positive score. These illustrate negation scope, spelling variation and implied meaning. They motivate future character features or contextual models, but no unrun improvement is claimed.

## Likely interview questions and natural answers

### 1. Why this problem?
Revio provides a direct product connection, and public labels let me measure a real classifier. I would still validate that operators need this particular queue and that the existing product does not already solve it.

### 2. Why not a chatbot?
The task is sorting and inspecting feedback. A classifier and explicit rules produce useful structured output without generation costs or unsupported answers.

### 3. What is genuinely machine learning here?
TF-IDF learns vocabulary/IDF from training data, and logistic regression learns sentiment weights from labels. Themes, safety matching and queue priorities are rules, and I label them that way.

### 4. What does TF-IDF mean?
Term frequency represents how much a term occurs in a review. Inverse document frequency reduces the weight of terms common across training documents. The result is normalized into a sparse vector.

### 5. Why use bigrams?
Adjacent pairs retain some local context, such as 'not good', that isolated words lose. They still cannot fully resolve long negation scope or sarcasm.

### 6. Why preserve stop words?
Words such as 'not' can reverse sentiment. Removing them indiscriminately would damage useful signals.

### 7. What does C do?
It controls inverse regularization strength. Smaller C penalizes large coefficients more strongly. I chose among three values using validation macro-F1, not test performance.

### 8. How did you prevent leakage?
I canonicalized and deduplicated text before splitting and fitted the vectorizer only on training rows. I saved split hashes to verify disjointness. Hidden author/business grouping and near duplicates remain limitations because source IDs are unavailable.

### 9. Why three splits?
Training fits parameters, validation selects design settings and test estimates performance after settings are fixed. Reusing test labels for threshold selection would bias the estimate.

### 10. Why not train on all data for the final app?
I retained the evaluated training-only model so the app matches the reported model and threshold. A production refit would need a new calibration/validation protocol and independent acceptance set.

### 11. Why macro-F1?
It treats both sentiment classes equally and summarizes precision/recall. I also report negative recall because missed negative feedback matters operationally. The benchmark is balanced, which may not match real review prevalence.

### 12. Did your model beat the baseline?
It beat the majority baseline, but not Naive Bayes on test F1: 0.792 versus 0.804. Logistic regression had better Brier score, 0.138 versus 0.150. I would not claim a decisive overall win.

### 13. Why retain logistic regression?
It was chosen before test evaluation for explainable probability-based triage. The baseline result should inform a new experiment, not a test-driven model switch presented as independent validation. A calibrated NB comparison is a sensible next step.

### 14. Is confidence calibrated?
No formal calibration guarantee is established. I report Brier score and validation threshold behavior. Reliability diagrams, calibration error and calibration on target data are future work.

### 15. What does uncertain mean?
The model did not meet its support/confidence rule. It does not mean neutral; there is no neutral training label.

### 16. Did the threshold achieve its target?
On validation, yes: 86.8% accepted accuracy. On test, no: 82.5% at 89.3% coverage. The shortfall is why I retain manual review and avoid production claims.

### 17. Why show coverage?
Accuracy can look excellent if a system accepts only a few easy cases. Coverage tells us how much work the system actually handles. Both are necessary.

### 18. How do explanations work?
For each observed n-gram, multiply its TF-IDF value by its learned coefficient. The sum plus the intercept gives the logit. The test suite reconstructs the probability from those contributions. They are model explanations, not causal explanations.

### 19. What is the domain-shift experiment?
Train on Amazon and IMDb, hold out every Yelp sentence, with C fixed at 1. It gets about 0.766 macro-F1 on Yelp. It is a separate stress test for transfer, not a production estimate.

### 20. How is data privacy handled?
The app runs locally, does not persist uploads, and redacts common email/phone patterns. That is incomplete: names and sensitive context can remain. Production needs purpose/retention controls, authentication and tenant isolation.

### 21. Why can 'no injury' trigger safety inspection?
The rule matches mentions rather than interpreting the allegation. That makes it auditable but creates false positives. The UI says to verify context, and this case is deliberately demonstrated.

### 22. Does it support Hindi?
No. A script heuristic routes the Hindi example to uncertainty. It cannot reliably identify romanized Hindi or all Latin-script languages. A multilingual model and target-language evaluation are needed.

### 23. Why is the UI sample synthetic?
I did not have authorized Cynbit customer data. Fictional locations and dates make the workflow demonstrable without pretending the sample is production evidence. They are never used for reported sentiment accuracy.

### 24. How would you deploy it?
The verified deployment is localhost Streamlit. For a pilot I would add authenticated service boundaries, tenant-scoped storage, logging without raw sensitive text, monitoring and platform-authorized connectors. I would validate a container separately before claiming it works.

### 25. How would it scale?
Vectorize batch inference, compute explanations on demand and profile full request latency. Add a queue only if workload demands it. The tiny model is not the hardest part; authorization, ingestion and data quality are likely more work.

### 26. What would you improve first?
Collect permissioned, independently annotated reviews from the intended sector and languages. Measure inter-annotator agreement and business/time-separated performance before changing model complexity.

### 27. What are the most important tests?
Split disjointness, correct raw-record parsing, exact explanation reconstruction, malformed-input rejection, unsupported-language abstention and a real Streamlit interaction test. These test behavior rather than merely checking that functions exist.

### 28. How would you measure business impact?
Randomize or counterbalance manual versus assisted review for consenting operators. Measure time per correctly reviewed item, missed urgent cases, false alerts and overrides. No saving has been measured yet.

### 29. Why not automatically respond to customers?
The prototype has not established target-domain reliability and has no approved response policy or authenticated connector. Its output is internal decision support.

### 30. What did AI assistance contribute?
AI assistance helped research, implementation, testing and documentation. I should be transparent about that and demonstrate understanding by tracing the code, reproducing results and explaining the limitations in my own words.

## Demo checklist

Start the server before the interview. Keep the README, research matrix, model code and evidence page ready. Show a correct example and a failure/abstention example. Quote test values, not validation values. Explain that the current repository was already public and that no assessment email or external application deployment was performed. Never imply that fictional reviews represent Cynbit customers.
