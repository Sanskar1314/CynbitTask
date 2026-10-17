# StockSense development log

Base: 14df7c7b28cdee253171e5a78c663656bab5d557 (previous prototype). Date/time zone: Asia/Kolkata.

2026-10-17: Safe replacement baseline, prior history preserved. Commit: chore: replace previous prototype with StockSense foundation. Push verified in subsequent milestone entry.

2026-10-17: Foundation 1d3734e2cc452dc581a33a74e373a799c818b187 pushed to origin/main and remote verified. Data milestone adds reproducible synthetic tables, atomic validation, censor-aware summaries and SQLite. Seven tests passed. No real customer data.

2026-10-17: Data milestone a37bb66c3ceb85543348acfc3ee44ffad4b3321b pushed and remote verified. Core engines implemented and evaluated: 16 tests passed. Three validation origins select boosting; held-out observed MAE 2.975 versus moving-average 3.599. See evaluation/metrics.json. No production accuracy claim.

2026-10-17: Core engine milestone afca596ddc7cc5c470483a47fa2d237659e15e3d pushed and remote verified. Dashboard adds all eight sections, Plotly charts, CSV downloads, atomic uploads, local save/load and snapshot-specific model evaluation. Seventeen tests passed including navigation through all sections and invalid-upload preservation. Initial AppTest relative path corrected. Old server retained old Python imports after file replacement; restarted process to clear stale modules.

2026-10-17: Dashboard c6f4c895978a906cdf5d01afe0b9043a16a80e39 pushed and remote verified. Initial automatic approval review failed due to a usage-limit service error (no action executed); authorized retry after user resume succeeded. Documentation milestone adds opportunity/technical reports, complete walkthrough,40 interview questions and three rendered PDFs. Nineteen tests passed. Browser six-table upload successfully replaced the snapshot and correctly switched to an unevaluated baseline. Review-only upload now updates provenance rather than falsely labelling imported reviews synthetic.

2026-10-17: Documentation milestone f0eb380302e38dfefcbce5010a19bcf5af3350ea pushed and remote verified. Final integration milestone includes imported-review provenance correction,10MB upload control limits, high-demand/storage and PO-timing regression tests, actual dashboard screenshot and completed QA/state. Final19 tests passed. PDFs refined to5/6/12 pages, all visually inspected; temporary/obsolete PDF renders removed. Next commit hash intentionally not embedded in itself; verify Git HEAD against origin/main at handoff.

2026-10-17 revision2 completed: core milestonefffff03a7c8b829a924d114a177cce28033f48bd pushed and remote HEAD verified. Live chart, seven-section navigation and calendar controls verified; forecast/dashboard screenshots refreshed. Reports and interview guide updated; all25 PDF pages inspected. Final tests25 passed. Full model evaluation already completed and saved. Local app remains on127.0.0.1:8501. Imported public Google Calendar snapshot is not continuous sync. Unrelated .DS_Store remains untouched.

2026-10-17 revision3: investigated user-reported sweets/tea/coffee patterns. Sweets already had uplift but window transitions were unclear; tea had a sparse-event negative coefficient; synthetic hot-drink phase peaked incorrectly in October. Corrected demo winter phase, pooled festival effects per product, shaded windows and summarized the same forecast. 26 tests pass; full360-day evaluation rerun, selected seasonal MAE2.860 vs same-data boosting2.964. Previous verified commit3c633e9df1550936af7023fa386f2dc2caf0cc2a. No claims of real-store improvement; v2 metrics archived.

2026-10-17 plain-English documentation milestone: rewrote all three report sources, walkthrough and40 interview answers; added file/CSV-column guide. Simplified diagrams and increased body-text size. Rebuilt PDFs (7/8/17 pages), checked required model/metric/dataset disclosures and visually inspected all32 pages, including wider file-name columns. No application/model/data/evaluation changes; existing26-test result remains the last model verification. Previous verified commitc1726fbf42824910f66a66fe26ebe22519fed240.
