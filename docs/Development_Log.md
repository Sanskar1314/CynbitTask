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
