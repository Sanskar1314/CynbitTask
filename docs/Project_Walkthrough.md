# Complete project walkthrough

## Start with the business decision

A kirana owner wants to know whether to buy more of a product. A forecast answers how much demand may occur. A separate inventory policy asks whether existing stock and supplier receipts can satisfy it without expiry or excess. Customer reviews add reasons to investigate a product; they do not measure units sold.

This separation makes errors easier to understand. If demand is wrong, inspect training and recent observations. If a quantity is wrong despite a sensible forecast, inspect batch dates, receipt timing and policy constraints. No component places an order.

## Repository map

| Path | Purpose |
|---|---|
| app/app.py | Seven-section Streamlit UI, session state and cached computation |
| src/data.py | Six-table validation, CSV handling, demand masking, summaries, SQLite |
| src/forecasting.py | Origin-only features, training, prediction, metrics, chronological evaluation |
| src/inventory.py | Periodic policy, constrained rounding, daily FEFO, explanations |
| src/seasonal_model.py | Per-product joint seasonal, trend, weekday and festival count model |
| src/calendar_data.py | Public calendar snapshot normalization and provenance |
| src/seasonality.py | Monthly profile and comparable event windows |
| src/reviews.py | Product alias and English intent rules |
| scripts/generate_data.py | Seeded synthetic ledger and snapshot generator |
| scripts/evaluate.py | Reproduce model comparisons and prediction CSV |
| scripts/build_reports.py | Export editable report sources to PDFs |
| data/sample | Six CSV tables and generation metadata |
| evaluation | Measured metrics and backtest product-day predictions |
| tests | Data, business-rule, causality and UI integration checks |
| docs | Research, decisions, interview guide, recovery and development logs |
| reports | Three editable reports and rendered PDFs |

## From CSV bytes to a valid snapshot

`read_csv` accepts UTF-8 data within a10MB limit. `validate` copies each table, normalizes text, checks headers and converts numeric/date fields. It rejects nonfinite or negative quantities, malformed dates, duplicate keys, invalid references and impossible recorded stock balances. All tables must pass before the UI replaces its session snapshot. A failed form leaves the previous data active.

Dates become pandas timestamps. Blank batch dates become NaT, preserving unknown status. The latest sales date is the snapshot's as-of date: the bundled demonstration remains reproducible instead of drifting with the computer clock. SQLite roundtrip serializes dates back to ISO strings and validates them again on load. Writes use a temporary database and atomic replacement.

## Observed sales versus demand

Suppose a shelf begins with three bottles and sells all three. Actual demand could be three or fifteen. The program does not know. It masks a known stockout or exhausted availability instead of training on three as if demand were fully observed. Missing dates are also unknown. A true zero with available stock stays zero.

This is a pragmatic baseline, not a complete censored-demand estimator. Discarding constrained days may select unusually quiet days and underestimate demand. The generator records latent demand so evaluation can illustrate that issue, but production data cannot supply it directly.

## Legacy boosting comparator training rows

Take an origin at the end of18 June2026 and a target seven days later. History features use observations no later than18 June. The target weekday/month and event proximity are known calendar features for25 June. The target is observed uncensored sales on25 June. A training cutoff earlier than25 June would forbid this row.

`features` creates30 rows per eligible origin, one per future horizon. `train` samples origins weekly to keep the demonstration lightweight. It stacks all SKUs into a global dataset; product identity is categorical. The model learns nonlinear splits such as different calendar behavior for different products. The ensemble improves successive residual errors; it does not memorize a fixed summer uplift rule.

No recursive prediction loop feeds yesterday's prediction into today's lag. This is direct multi-horizon regression: every horizon uses the same known origin history plus that horizon's calendar features. The tradeoff is more training rows and an explicit maximum30-day planning horizon.

## Why there are four predictors

A model is useful only if it improves a credible simple approach. A28-day average and weekly seasonal naive forecast are cheap, understandable benchmarks. Four validation windows select the lowest pooled MAE. Twelve later 30-day rolling test windows span 360 days. Seasonal Poisson regression wins selection and jointly fits each product’s smooth annual curve, weekdays, trend and a pooled dated festival effect. It is refitted on available history for the next30 days. With less than a full annual span it falls back to the average; without adequate recent history it withholds predictions.

For uploaded data, demo results are irrelevant. The UI starts with the moving average. Running that snapshot's chronological evaluation selects a method for that snapshot. Very short histories cannot support the full evaluation protocol. Point forecasts have data-support labels, not claimed confidence intervals.

## How to read the measured results

The selected seasonal model has rolling test MAE2.860, RMSE3.921, WAPE18.520% and bias-0.040. MAE is average absolute daily error in units; WAPE is aggregate numerical error, not classification accuracy.

The same-data boosting MAE is2.964 and average MAE3.374: relative improvements of3.5% and15.2%. There are4,200 observed product-days across360 test days. All four broad seasons improve, but not every SKU. The no-history SKU is excluded. Latent simulation diagnostics are separate. Old v1 metrics use different dates and a shorter protocol, so cannot be compared directly.

## Walk through the inventory engine

`periodic_quantity` implements the basic policy: forecast demand plus buffer minus usable stock and incoming supply plus backorders, floored at zero. With20 units/day, lead4, review7, safety30, stock80 and incoming20, target250 minus position100 gives150.

`simulate` goes day by day. Confirmed supply arrives on its expected date. Batches already expired are excluded. Demand consumes the earliest eligible expiry first. Unmet daily demand is recorded as shortage rather than automatically carried as an order. Existing backorders are a separate first-day obligation. This simplifies lost-sales behavior and should be reviewed for a real store.

`plan` subtracts projected expiry loss from effective supply during protection. It flags shortages before the new order's arrival. It caps new units by demand still unsatisfied during the new receipt's assumed life and by unit storage capacity at arrival. It then honors pack and MOQ constraints. A cap20 with pack12 can allow12, not24; if MOQ24, it withholds the order.

Unknown expiry blocks automatic ordering until stock is verified. Lead plus review greater than30 days withholds quantity because there is no supported forecast for the full period. A zero draft can therefore mean sufficient stock, a binding constraint or insufficient evidence; read the status and explanation.

## Batch expiry example

Eighty yogurt units expire after five future sellable days. Demand6/day consumes30; fifty remain at risk. With two batches, FEFO gives the earlier batch first claim on those30 units; the later batch cannot also claim them. Recorded expiry dates remain unchanged. Blank risk beyond30 days means unknown, not safe. Expired items are never recommended for sale.

## Seasons, events and reviews

The monthly chart shows historical observed means, which can reflect seasonality and trend together. The event table compares pre-event demand against a preceding baseline and requires multiple adequately observed occurrences. It does not prove a festival caused demand growth. The actual dates are imported public Google Calendar entries, with provenance in Data Management. This is a snapshot, not continuous synchronization. Seasonal evidence sits inside Product Demand Forecasting; there is one combined forecast.

The review rule pipeline finds long catalog aliases first. A request for sugar-free cola maps to that SKU instead of ordinary cola. Availability, variant and quality intents can coexist. Evidence and original text remain visible. A no-history variant gets an investigation recommendation, not a fabricated forecast. The model never receives review counts.

## Running a demonstration

1. Start the app using README commands and open the local link. State that all bundled records are synthetic.
2. Executive Dashboard: show actual recorded sales, draft quantities and the action queue.
3. Product Demand Forecasting: select Cola, switch7/14/30 days and explain the baseline comparison and dashed future line.
4. Smart Reorder Planner: inspect the formula explanation, then increase review days to observe constraints; restore default7 days.
5. Expiry Management: show yogurt risk, the expired coffee batch and the unknown chips expiry.
6. Slow-Moving Inventory: show biscuits overstock and why purchasing is paused.
7. Review Intelligence: show sugar-free requests; explain why no numeric order is invented.
8. Data Management: download templates, demonstrate an incomplete upload error and explain atomic replacement. Save/load is local and explicit.

## Debugging guide

If the interface shows imports from the previous prototype, stop the old Streamlit process and launch a fresh one; Python may retain old modules across hot reloads. If a CSV fails, inspect the table/column named in the error and compare with its template. If forecast is unsupported, inspect recent observed counts and stockout masking. If an order is zero, inspect status, unknown expiry, horizon, cap and MOQ before blaming the model.

To reproduce predictions, run scripts/evaluate.py with single-thread BLAS/OpenMP. Check evaluation/metrics.json and the detailed prediction CSV. The test suite should pass before changing model behavior; after model changes rerun both tests and evaluation. Do not hand-edit metrics to make the report look better.

## Boundaries of the demonstration

This is a local single-store proof of concept, with no purchase execution, public deployment, supported Revio/POS integration, authentication or verified ROI. Production requires consented data, real calendar maintenance, reconciliation, monitoring and human approvals. The previous unrelated review prototype is recoverable through Git, not mixed into the current implementation.
