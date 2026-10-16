# Development log

Timestamps use Asia/Kolkata. Each subsequent milestone records the preceding commit hash and verified push, avoiding a self-referential commit loop.

| Date | Milestone | Files | Commit message | Testing / push |
|---|---|---|---|---|
| 2026-10-16 | Initialize resumable assessment | README, AGENTS, ignore, docs logs/state | chore: initialize resumable assessment workspace | Remote read verified; commit/push follows |

- Initialization commit `3b7588a` pushed and remote main verified.
- 2026-10-16: company/industry research, six-opportunity scoring and pre-implementation design completed. Source links checked; all scores qualitative. Commit: `docs: verify Cynbit and select explainable Revio triage`.

- Research/design commit `6ac1fd5` pushed and remote verified.
- 2026-10-16: licensed UCI corpus downloaded with SHA-256 provenance; shared normalization, deduplication, CSV schema and safe export implemented. Commit: `feat: add attributed benchmark and validated review ingestion`.

- Dataset commit `4aa48c5` and parser fix `23d8b4a` pushed. Parser smoke test now passes (3000 raw / 2979 unique).
- 2026-10-16: model, explainable routing, fixed splits, baselines and domain-shift evaluation implemented. 23 core tests passed. Test macro-F1 0.791944; Naive Bayes 0.803691; accepted accuracy 0.825188 misses validation target. No test-driven threshold retuning. Commit: `feat: implement and evaluate explainable sentiment triage`.

- 2026-10-16: Streamlit inbox, single-review inspector, evidence view, upload validation, filters and safe CSV export implemented. Full suite: 24 passed, including Streamlit navigation and invalid-input handling. Commit: `feat: build interactive Revio review workbench`.

- Model/evaluation commit `d2a6354` and UI commit `9782012` were pushed and remote main verified on 2026-10-16.
- 2026-10-17: resumed final review. Fixed display/export sanitization without coercing string IDs, added redacted-ID collision protection and corrected top spacing. Core plus Streamlit suite: 26 passed. Files: src/data.py, app/app.py, tests/test_pipeline.py, evaluation test evidence. Commit: `fix: preserve review identity in safe display and exports`.

- Reliability correction `afaede9` pushed and remote SHA verified on 2026-10-17.
- 2026-10-17: completed company-specific opportunity/technical reports, nine detailed engineering decisions, full walkthrough, model card, 30 interview questions and demo guide. Added exact run instructions, optional untested Docker recipe, data checksum verifier and recovery/acceptance records. Fresh isolated environment: 26 tests passed. Commit: `docs: complete assessment reports and interview preparation`.

- Documentation milestone `2e58be7` pushed and remote SHA verified on 2026-10-17.
- 2026-10-17: packaged three generated PDFs (9/8/23 pages), eight diagram source/image pairs and an actual application screenshot. Visual contact-sheet review completed; automated checks found all 150 source headings, no blank pages and no broken local document links. Added reproducible PDF builder and verification script. Commit: `docs: package verified PDFs diagrams and application evidence`.

- Artifact milestone `ead0907d4c709739930612adab0c2fba1374e742` pushed and remote main verified on 2026-10-17.
- Final completion record: source hashes, document links, PDF heading coverage, 26-test primary/clean-environment runs and local HTTP health verified. No credential-pattern matches in tracked textual project files. Commit: `chore: finalize verified assessment recovery records`. This entry records the previous verified push to avoid a self-referential commit loop.

## Verified milestone history before the final log commit

Every listed commit was pushed and is included in verified remote main at ead0907. Timestamps below are Git author timestamps with their explicit offset.

| Timestamp | Commit | Message | Files changed | Push |
|---|---|---|---:|---|
| 2026-10-16T20:19:43+05:30 | 3b7588a | chore: initialize resumable assessment workspace | 6 | Verified |
| 2026-10-16T20:22:37+05:30 | 6ac1fd5 | docs: verify Cynbit and select explainable Revio triage | 5 | Verified |
| 2026-10-16T20:24:18+05:30 | 4aa48c5 | feat: add attributed benchmark and validated review ingestion | 12 | Verified |
| 2026-10-16T20:25:59+05:30 | 23d8b4a | fix: preserve multiline and punctuation benchmark records | 2 | Verified |
| 2026-10-16T20:28:34+05:30 | d2a6354 | feat: implement and evaluate explainable sentiment triage | 12 | Verified |
| 2026-10-16T20:28:40+05:30 | 9782012 | feat: build interactive Revio review workbench | 4 | Verified |
| 2026-10-17T00:27:35+05:30 | afaede9 | fix: preserve review identity in safe display and exports | 7 | Verified |
| 2026-10-17T00:27:57+05:30 | 2e58be7 | docs: complete assessment reports and interview preparation | 19 | Verified |
| 2026-10-17T00:28:23+05:30 | ead0907 | docs: package verified PDFs diagrams and application evidence | 26 | Verified |
