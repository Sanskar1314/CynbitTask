# StockSense project state

Updated 2026-10-17, revision3. User requested one season-aware demand forecast and actual Google Calendar festival dates.

## Implemented

- Per-product Poisson count regression jointly learns smooth annual patterns, weekdays, trend and festival preparation windows. Original boosting and two simple baselines remain comparators. Sparse annual history falls back explicitly; no-history products remain unsupported.
- Public Holidays in India snapshot imported via connected Google Calendar:28 selected dates2024–2027. No personal appointments read. App uses a saved snapshot, not continuous synchronization; Data Management supports inspect/download/apply.
- Synthetic demo regenerated with the same seed and actual calendar dates. No uploaded or saved user sales rewritten. Old v1 metrics archived; old data available in Git.
- Seven UI sections. Seasonal/event evidence is inside Product Demand Forecasting, with one future demand line and event markers. Same forecast feeds inventory planning.
- Existing FEFO, receipt timing, reorder constraints, reviews, atomic uploads and local SQLite behavior retained.

## Measured verification

26 pytest tests pass. Full evaluation executed: four validation origins choose seasonal Poisson by MAE3.088 vs boosting3.178. Twelve later disjoint30-day windows span360 test days. Observed synthetic n4,200: MAE2.860, RMSE3.921, WAPE18.520%, bias-0.040. Same-data boosting MAE2.964, average3.374. Relative reductions3.5% and15.2%; all four broad season groups improve, not every SKU. No merchant accuracy or ROI established. Calendar retrieval is retrospective, not a historical point-in-time feed.

## Completion

Live browser verified: seven sections, seasonal model selected, one future line with Dussehra/Diwali markers, integrated explanation and public calendar controls. Forecast/dashboard screenshots refreshed. The reports have now been rewritten in simple English: opportunity7, technical8, complete guide17 pages. All32 pages were rendered and visually checked. Latest suite26 passed; no known failing checks. Local app http://127.0.0.1:8501/. README includes launch/evaluation commands. User .DS_Store change preserved and excluded from commits.

## Git and boundaries

Repository https://github.com/Sanskar1314/CynbitTask.git, main. Previous verified milestonec1726fbf42824910f66a66fe26ebe22519fed240. Commit meaningful milestones, push immediately, verify remote HEAD; no force push. No public deployment, assessment submission, recruiter contact or visibility changes authorized. Logs record previous hashes to avoid recursion.

Production requires consented real data, regional calendar maintenance, supported POS/Revio integration, shadow-policy evaluation, authenticated tenant separation and calibrated uncertainty. Current synthetic single-store results do not establish production readiness.

## Revision3: product-pattern correction

The previous synthetic tea/coffee curve incorrectly peaked near October because it inverted the summer beverage curve. The generator now uses an explicit January-centered winter curve for hot drinks. This is a declared synthetic scenario correction, not evidence about a real merchant. Only bundled synthetic records were regenerated; user uploads and saved snapshots were untouched.

With only two or three occurrences per named festival, separate event coefficients overfit noise: tea received an unjustified Diwali dip. The model now pools festival preparation windows within each SKU while jointly fitting season, weekday and trend. This preserves a learned gifting uplift without forcing every product upward. Different named-festival effects cannot be estimated independently by this pooled model; richer history should support future hierarchical estimation.

Product checks: packaged sweets Diwali mean7.95 units/day versus4.20 on the same dates with event indicators omitted. This omitted-event value is a model diagnostic, not a second user-facing forecast or causal estimate. Tea and coffee seasonal expectations rise from October through December. Both remain within10% of their no-event values during Diwali in the synthetic no-hot-drink-festival-effect scenario. Tests cover both gifting SKUs, both hot drinks, Dussehra and Diwali. Shaded preparation windows and a summary of the same forecast clarify festival versus nonfestival days.

Full evaluation rerun: seasonal model test MAE2.860 versus same-data boosting2.964, n4,200 across360 days. These values cannot demonstrate improvement over v2 because the synthetic data changed. Repeated development against this simulation is not an untouched external benchmark. Prior metrics are retained in evaluation/archive/v2.

## Plain-English documentation update

User asked to stop model changes and simplify the PDFs. All three reports now explain the selected model and why it was chosen, error scores without a misleading accuracy percentage, dataset dates/counts/source/limits, screens, stock terms and examples. New docs/File_Guide.md explains main files and CSV columns. Complete guide now assembles walkthrough, file guide and40 short interview answers; the historical engineering log is retained separately. App code, model, dataset, tests and evaluation artifacts are unchanged. PDF build and content/layout checks completed; no model evaluation rerun was needed for this documentation-only update.
