# Project state

Updated: 2026-10-17, Asia/Kolkata.

## Current phase

Final packaging and Git synchronization. The research, working prototype, evaluation, reports, educational documentation, diagrams and three PDFs exist. Do not restart completed development.

## Completed

- Official site independently verified: https://www.cynbit.in/; LinkedIn identity cross-check.
- Six opportunities scored; selected Revio Signal Desk (4.50/5), conditional on product-gap validation.
- Attributed UCI corpus, checksum manifest, duplicate controls and deterministic 60/20/20 split.
- TF-IDF logistic model, C=4; validation-selected threshold .55; exact contribution explanations.
- Local Streamlit inbox, single-review inference, model evidence, validation, partial redaction, policy routing and CSV export.
- Measured evaluation and baseline comparison; 26 passing tests after final display-preservation correction.
- Opportunity and technical reports; decision log, walkthrough, model card and 30 interview Q&A.
- Eight Mermaid/PNG diagrams and three PDFs (9, 8 and 23 pages).
- Clean isolated install succeeded; all final 26 tests passed in that environment.
- HTTP health and actual browser layout verified on 2026-10-16; local app may require restart after session interruption.

## Model evidence and known limits

Test macro-F1 .791944 versus NB .803691. Negative recall .788591. Accepted accuracy .825188 at .892617 coverage, below .85 development target. Domain-shift F1 .766432. No neutral class or reliable multilingual support; no real customer validation. Keyword safety mentions can be false positives. Contact redaction is partial. No production authentication, live integrations, persistent corrections or measured ROI.

## Files and run commands

README.md indexes all deliverables. Main code: app/app.py, src/data.py, src/model.py, src/service.py. Evaluation: scripts/evaluate.py and evaluation/. Reports: reports/*.md and *.pdf. PDF builder: scripts/build_pdfs.py.

```bash
cd /Users/sanskar/Desktop/InternshipTask
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_manifest.py
.venv/bin/python scripts/verify_deliverables.py
.venv/bin/python -m streamlit run app/app.py --server.address 127.0.0.1 --server.port 8501
```

Use Python 3.12 for a fresh installation; requirements.txt and requirements-reports.txt pin direct dependencies. No API keys required. Optional Dockerfile has not been executed.

## Git and immediate next steps

Designated origin: https://github.com/Sanskar1314/CynbitTask.git; branch main. Existing repository was public; visibility unchanged. Last previously verified push: 9782012 (UI milestone), with earlier model commit d2a6354. Final packaging commits are pending at this state snapshot; consult git log and docs/Development_Log.md for subsequent verified hashes.

Next: finish document/link verification, commit/push final reliability corrections, then reports/PDF package, then final logs. Verify local HEAD equals remote main. Leave the pre-existing tracked .DS_Store modification untouched. Never force push, submit, email recruiters, change visibility or publicly deploy.

Deadline: 18 October 2026, 03:48 AM; timezone unverified. Asia/Kolkata remains a planning assumption, not verified recruiter instruction.
