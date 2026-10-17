# Verification record

2026-10-17. Executed Python3.12 environment with pinned dependencies.

- Unit/integration suite:19 passed, including all eight Streamlit sections and incomplete-upload preservation. Initial test path error was fixed; final suite passed.
- Forecast evaluation executed: three validation origins and final30-day test; results in evaluation/metrics.json and detailed CSV. No random split or future demand features.
- Browser rendered StockSense charts/data after restarting an old server retaining stale imports. Narrow viewport wraps content without hiding primary actions; wide tables scroll.
- All six sample files were selected through actual browser upload controls. Final submission verification recorded below when complete.
- Three PDFs generated with ReportLab, reopened and rendered with PDFium; every page inspected through contact sheets. Final layout: opportunity5 pages, technical6 pages, explanation12 pages. No clipping/overlap observed. Editable Markdown retained.
- No external assessment submission, contact or public application deployment. Local server bound127.0.0.1:8501. Public repository visibility unchanged.

Real-browser final upload: all six demo CSVs were submitted successfully in an isolated tab. The UI changed to Uploaded snapshot and explicitly selected the moving-average baseline pending snapshot-specific evaluation. Reset to demo was then exercised. The shared user tab was left separate from this test. Dependency check: no broken requirements found.

Final QA: imported-review provenance corrected; UI upload limit10MB matches parser policy. Added independent high-demand/capacity and receipt-timing assertions. Final suite19 passed. Saved actual browser screenshot in assets/dashboard.png. PDF links verified structurally (five opportunity references, two technical references). Temporary renders removed after inspection.

## Revision2 final verification — 17 October2026

25 tests passed, including one combined forecasting workspace, calendar controls, product-specific opposite seasons, exact festival dates, causal training, annual-history fallback and empty-SKU evaluation joins. Full evaluation completed: selected seasonal model MAE2.884 versus same-data boosting2.990 over360 test days (4,201 observed product-days). All four broad season groups improve; not every SKU. No real-store result claimed.

Restarted verified local Streamlit server to load new modules. Real browser shows seven sections, selected seasonal model, one forecast line with Dussehra20 October and Diwali8 November2026 markers, and integrated seasonal explanation. Screenshots assets/dashboard.png and assets/forecast.png. Public calendar management controls visible. User browser tab was not used for testing.

Updated reports rebuilt and all25 pages visually inspected (5/7/13). Earlier entries describe v1 and are retained as history. Core milestonefffff03a7c8b829a924d114a177cce28033f48bd pushed and remote verified. No deployment, submission, recruiter contact or visibility change.

2026-10-17 revision3: investigated user-reported sweets/tea/coffee patterns. Sweets already had uplift but window transitions were unclear; tea had a sparse-event negative coefficient; synthetic hot-drink phase peaked incorrectly in October. Corrected demo winter phase, pooled festival effects per product, shaded windows and summarized the same forecast. 26 tests pass; full360-day evaluation rerun, selected seasonal MAE2.860 vs same-data boosting2.964. Previous verified commit3c633e9df1550936af7023fa386f2dc2caf0cc2a. No claims of real-store improvement; v2 metrics archived.

Revision3 final QA: 26 tests passed and full evaluation completed. All26 PDF pages inspected. Live sweets chart confirms higher demand within shaded Dussehra/Diwali preparation windows. Demo hot-drink winter correction and pooled-event limitation documented; data and code changed, so no v2-versus-v3 accuracy improvement claimed.

2026-10-17 plain-English documentation milestone: rewrote all three report sources, walkthrough and40 interview answers; added file/CSV-column guide. Simplified diagrams and increased body-text size. Rebuilt PDFs (7/8/17 pages), checked required model/metric/dataset disclosures and visually inspected all32 pages, including wider file-name columns. No application/model/data/evaluation changes; existing26-test result remains the last model verification. Previous verified commitc1726fbf42824910f66a66fe26ebe22519fed240.
