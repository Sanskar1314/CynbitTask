# Revio StockSense
## AI Opportunity Report

Prepared for the Cynbit AI/ML Engineer Internship assessment. Research checked 17 October 2026. This is an independent proposal, not a Cynbit product announcement.

## Executive summary

StockSense helps a kirana owner decide what to replenish, what to pause and which batches need attention. It combines sales forecasts with explicit inventory rules and qualitative customer requests. The working prototype uses synthetic records, local CSV imports and a Streamlit dashboard. It has no supported Revio integration and no measured real-store financial benefit.

The opportunity is to connect customer-feedback investigation with operational decisions. Before product investment, Cynbit should confirm existing feature overlap, access to merchant sales data and willingness to pay. Public silence does not establish that an inventory feature is missing.

## Company and existing product context

Cynbit's site lists software, AI automation, cloud and marketing services [1]. Its product page advertises Revio for review aggregation, AI responses, sentiment/crisis signals and multi-location roles; TenantEase for property/rent administration; and Studio for adaptive coding and career support [2]. These are verified advertisements, not independently tested product performance.

Revio's advertised users include brand managers and location advisors. StockSense's proposed users are kirana owners and purchasing staff. Their overlap is a hypothesis; no evidence establishes that kiranas are current Revio customers. No inventory limitation, customer list, supported API or private roadmap was verified.

## Industry evidence and merchant problem

ONDC's DigiDukaan describes fragmented kirana procurement and the value of digitized replenishment and inventory visibility [3]. This supports investigating the problem, not a causal claim about savings. Zoho already documents reorder levels and batch dates [4,5]. Therefore, inventory alerts and expiry records are established capabilities, not novel inventions.

A store may sell out of a popular drink while money is tied up in slow biscuits. Daily sales understate demand when the shelf is empty. Perishable batches can expire before a conventional reorder calculation consumes them. Reviews can reveal unavailable variants but cannot reliably tell an owner how many units to purchase. The prototype explicitly models these distinctions.

## Opportunity comparison

Scores are analyst judgments, not measured company economics. Impact: potential customer value (1 low, 5 high). Feasibility: small-team prototype practicality. Data readiness: likely obtainable data, with no internal access assumed. Weighted score = 0.4 impact + 0.35 feasibility + 0.25 data readiness. Existing marketed functionality is treated as context for improvements, not as a new invention.

| Proposed opportunity | Product/context | Impact | Feasibility | Data readiness | Score |
|---|---|---|---|---|---|
| Demand + expiry-aware purchasing | Revio-adjacent StockSense | 5 | 4 | 2 | 3.85 |
| Evidence-grounded response quality checks | Revio, improve existing AI replies | 4 | 4 | 3 | 3.75 |
| Repeated issue-to-resolution tracking | Revio operational follow-through | 4 | 4 | 3 | 3.75 |
| Payment anomaly triage with human review | TenantEase | 4 | 3 | 2 | 3.15 |
| Maintenance request clustering/routing | TenantEase extension hypothesis | 3 | 4 | 3 | 3.35 |
| Learning-intervention evaluation | Studio, improve existing adaptive paths | 4 | 3 | 2 | 3.15 |

StockSense scores well for demonstrable operational decisions and measurable forecast/inventory tests. Its weak data readiness is material: merchants must supply reliable sales, stock and expiry records. If integration is difficult, a narrower Revio quality or issue-resolution enhancement may be more feasible. Small changes in subjective weights can change the ranking.

## Why choose StockSense for this assessment?

It demonstrates forecasting, leakage control, validation, deterministic decision logic, NLP and user-facing explanations in one coherent workflow. The choice is suitable for an engineering proof of concept; it does not establish commercial superiority. It moves beyond repeating sentiment classification already advertised by Revio.

## Proposed solution and users

The owner imports six related CSV tables: products, sales, batches, purchase orders, reviews and a locally maintained event calendar. The dashboard estimates 7-, 14- and 30-day demand, produces constrained draft purchase quantities, flags expiry/overstock and surfaces customer requests. Staff verify stock records and supplier dates. The owner approves any actual purchasing outside this application.

A future optional module could obtain authorized feedback through a supported Revio interface and sales through a POS connector. The prototype simulates this with imported reviews. Review mentions create an investigation queue; they do not create invented sales observations or automatic forecast multipliers.

## Business value and measurement plan

Potential benefits are fewer avoidable stockouts, less expiry loss, less excess inventory and faster purchasing review. None has been measured in a live shop. Run a shadow pilot first: owners see suggestions but retain existing purchasing policy. Record recommendation acceptance, overrides, data completeness, stockout hours, expiry cost and time spent reviewing orders. Then compare matched periods or randomized store groups while accounting for promotions, seasonality and supplier changes.

Measure forecast MAE/WAPE by SKU and volume group, plus bias and coverage. Evaluate inventory outcomes separately: a lower forecast error does not automatically reduce waste, because costs and supplier constraints matter. Predefine stop conditions for bad stock records, repeated shortages and deteriorating bias. Do not claim percentage savings without an appropriate pilot.

## Competitive differentiation

The proposed combination is transparent forecast selection, expiry-aware batch simulation, receipt timing and review-based assortment investigations. Basic reordering and batch tracking already exist elsewhere [4,5]. This implementation does not establish a proprietary moat, market-first capability or superiority over commercial inventory products. Its differentiator for the assessment is explainable integration of the components and candid handling of uncertainty.

## Prototype scope and measured evidence

Implemented: synthetic data generation, schema checks, four forecasting candidates, chronological evaluation, FEFO expiry simulation, periodic-review quantities, receipt-life/storage caps, descriptive seasonal/event analysis, English review rules, seven dashboard sections, CSV export/import and SQLite persistence.

Measured on 4,200 synthetic uncensored product-days across 360 rolling test days: seasonal Poisson MAE 2.860, RMSE 3.921, WAPE 18.520%, bias -0.040. On the same revised data, boosting MAE is 2.964 and moving-average MAE is 3.374. The 3.5% and 15.2% respective reductions are simulation-only, not business ROI. No-history products receive no exact demand forecast.

## Risks and limitations

Data readiness is the largest adoption risk. Sales censored by stockouts and missing batch labels distort recommendations. Festivals vary by region and year; the public Google Calendar snapshot was imported retrospectively and is not continuously synchronized. Regional differences and tentative dates require review. Review rules can misread negation, languages and multi-product text. Model selection is pooled across products and may conceal weak SKUs. There is no authenticated multi-tenant deployment, supported Revio API, purchase execution or calibrated service guarantee.

## Production roadmap and investment gates

1. Discovery: verify Cynbit overlap and supported interfaces; interview kirana owners and inspect consented data samples.
2. Data pilot: reconcile sales, receipts, returns and batch balances; require recorded availability and verified regional events.
3. Shadow operation: backtest real demand, evaluate SKU-level failures, collect override reasons and compare policies without executing orders.
4. Controlled rollout: authenticated tenant isolation, audit history, monitored model versions, supplier-confirmed receipts and approval workflow.
5. Expansion only after evidence: multi-store transfers, supplier reliability, calibrated uncertainty and budget optimization.

## References

[1] Cynbit services, https://www.cynbit.in/services (accessed 2026-10-17).

[2] Cynbit products, https://www.cynbit.in/products (accessed 2026-10-17). Public product positioning; no independent performance verification.

[3] ONDC DigiDukaan, https://www.ondc.org/pages/digidukaan.html (accessed 2026-10-17). Industry program positioning, not a StockSense outcome study.

[4] Zoho Inventory reorder levels, https://www.zoho.com/inventory/help/items/additional-features.html (accessed 2026-10-17).

[5] Zoho Inventory batch tracking, https://www.zoho.com/us/inventory/help/advanced-inventory-tracking/batch-tracking.html (accessed 2026-10-17; localized redirect may apply).
