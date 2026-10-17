# StockSense project state

Updated 2026-10-17, revision2. User requested one season-aware demand forecast and actual Google Calendar festival dates.

## Implemented

- Per-product Poisson count regression jointly learns smooth annual patterns, weekdays, trend and festival preparation windows. Original boosting and two simple baselines remain comparators. Sparse annual history falls back explicitly; no-history products remain unsupported.
- Public Holidays in India snapshot imported via connected Google Calendar:28 selected dates2024–2027. No personal appointments read. App uses a saved snapshot, not continuous synchronization; Data Management supports inspect/download/apply.
- Synthetic demo regenerated with the same seed and actual calendar dates. No uploaded or saved user sales rewritten. Old v1 metrics archived; old data available in Git.
- Seven UI sections. Seasonal/event evidence is inside Product Demand Forecasting, with one future demand line and event markers. Same forecast feeds inventory planning.
- Existing FEFO, receipt timing, reorder constraints, reviews, atomic uploads and local SQLite behavior retained.

## Measured verification

25 pytest tests pass. Full evaluation executed: four validation origins choose seasonal Poisson by MAE3.088 vs boosting3.117. Twelve later disjoint30-day windows span360 test days. Observed synthetic n4,201: MAE2.884, RMSE3.958, WAPE18.673%, bias-0.052. Same-data boosting MAE2.990, average3.389. Relative reductions3.5% and14.9%; all four broad season groups improve, not every SKU. No merchant accuracy or ROI established. Calendar retrieval is retrospective, not a historical point-in-time feed.

## Completion

Live browser verified: seven sections, seasonal model selected, one future line with Dussehra/Diwali markers, integrated explanation and public calendar controls. Forecast/dashboard screenshots refreshed. All25 report pages rendered and visually checked (opportunity5, technical7, explanation13). Latest suite25 passed; no known failing checks. Local app http://127.0.0.1:8501/. README includes launch/evaluation commands. User .DS_Store change preserved and excluded from commits.

## Git and boundaries

Repository https://github.com/Sanskar1314/CynbitTask.git, main. Previous verified milestonefffff03a7c8b829a924d114a177cce28033f48bd. Commit meaningful milestones, push immediately, verify remote HEAD; no force push. No public deployment, assessment submission, recruiter contact or visibility changes authorized. Logs record previous hashes to avoid recursion.

Production requires consented real data, regional calendar maintenance, supported POS/Revio integration, shadow-policy evaluation, authenticated tenant separation and calibrated uncertainty. Current synthetic single-store results do not establish production readiness.
