# Opportunity selection before implementation

Decision date: 2026-10-16. Scores are engineering judgments under the assessment constraints, not market measurements. Sources and uncertainty boundaries are in 01_Company_Research.md and 02_Industry_Analysis.md.

## Six candidate opportunities

### A. Revio Signal Desk: explainable review triage
Business problem: managers need a defensible queue for inspecting feedback. Relevance/evidence: Revio's advertised review intelligence and multi-location workflow. Approach: supervised text sentiment, confidence-based abstention, transparent policy flags and branch/theme summaries. Users: brand and location managers. Data: licensed sentiment corpus for mechanics; permissioned reviews plus operator decisions for a pilot. Complexity: medium. Expected impact: less manual sorting, hypothesis only. Feasibility: high for a local demo, uncertain for production languages. Risks: sarcasm, domain shift, false urgency and incomplete redaction. Metrics: macro-F1, negative recall, coverage/selective accuracy, Brier score, review time and override rate. Scale: batched CPU inference and tenant-isolated queues. Existing sentiment/crisis features are acknowledged; the proposed incremental focus is uncertainty and auditable decision support, whose absence in Revio is not established.

### B. TenantEase rent reconciliation anomaly assistant
Problem: identify inconsistent payment records. Evidence: TenantEase describes rent and transaction tracking. Approach: reconciliation rules plus Isolation Forest on transaction features. Users: property operators. Data: ledger, invoices and verified exceptions, currently unavailable. Complexity: medium-high due to accounting integration. Impact: potentially faster exception handling; unmeasured. Feasibility: synthetic-only demonstration is easy but business validation weak. Risks: false accusations, irregular legitimate payments and personal financial data. Metrics: exception precision, recall and reconciliation time. Scale: per-property baselines with human approval; never automated tenant eligibility decisions.

### C. Cynbit Studio learning-gap recommender
Problem: choose useful next exercises. Evidence: Studio advertises adaptive learning. Approach: knowledge tracing or content-based recommendations. Users: learners and mentors. Data: consented attempts, skill rubric and longitudinal outcomes. Complexity: high. Impact: potentially better practice allocation. Feasibility: limited by unavailable interaction histories. Risks: reinforcing early mistakes, unfair difficulty and child-data handling. Metrics: learning gains in controlled studies, completion and recommendation coverage. Scale: curriculum versioning and cohort monitoring. Must extend rather than duplicate advertised adaptation.

### D. Services discovery and requirements matcher
Problem: structure incoming project briefs. Evidence: contact page describes requirement analysis. Approach: retrieval over approved service descriptions and missing-requirement extraction. Users: solution architects. Data: public service corpus plus labelled briefs. Complexity: low-medium. Impact: potentially faster intake; volume unknown. Feasibility: high. Risks: unsupported promises, shallow retrieval, confidential briefs. Metrics: retrieval recall@k, missing-field accuracy and architect edit time. Scale: approved catalog versions and CRM integration.

### E. Support knowledge retrieval with citations
Problem: locate trustworthy product answers. Evidence: broad product/support surface; internal burden unverified. Approach: retrieval over manuals, with abstention and optional grounded generation. Users: support agents. Data: approved manuals, support questions and access rules; public corpus is thin. Complexity: medium. Impact: potentially shorter handling time. Feasibility: constrained by missing manuals. Risks: hallucinations and cross-tenant leakage. Metrics: retrieval recall, answer support and resolution time. Scale: tenant filters and document lifecycle controls.

### F. Cloud-service anomaly monitoring
Problem: surface service incidents. Evidence: cloud services and backend offerings. Approach: seasonal residuals and anomaly detection on telemetry. Users: operations engineers. Data: logs, metrics and incident labels, unavailable publicly. Complexity: high. Impact: potentially lower detection time. Feasibility: synthetic workloads only before access. Risks: alarm fatigue, changing baselines and missing context. Metrics: incident recall, false alerts/day and detection delay. Scale: streaming aggregation and service-specific thresholds.

## Weighted matrix

1 = weak; 3 = moderate; 5 = strong. For complexity-related feasibility, higher is easier. Data availability measures usable assessment data, not access to company production data.

| Opportunity | Impact 25% | Relevance 25% | Feasibility 15% | Data 15% | Demo 10% | Scale 10% | Weighted /5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A Revio triage | 4 | 5 | 5 | 4 | 5 | 4 | 4.50 |
| B Reconciliation | 4 | 5 | 3 | 2 | 4 | 4 | 3.80 |
| C Learning gaps | 4 | 5 | 3 | 2 | 4 | 5 | 3.90 |
| D Discovery matcher | 3 | 4 | 5 | 4 | 4 | 4 | 3.90 |
| E Support retrieval | 4 | 4 | 4 | 2 | 4 | 4 | 3.70 |
| F Cloud anomalies | 4 | 4 | 3 | 2 | 4 | 4 | 3.55 |

Calculation: sum(score * weight); weights total 1.00.

## Score justification, criterion by criterion

A: impact 4 because triage is a recurring task but volume unknown; relevance 5 from direct Revio fit; feasibility 5 from CPU classification; data 4 because public labels exist but target labels do not; demo 5 from interactive batch and single-review flow; scale 4 because inference is cheap but integrations need work.
B: impact 4 for costly bookkeeping exceptions; relevance 5 from TenantEase; feasibility 3 for accounting semantics; data 2 because real ledgers are absent; demo 4 for visible exceptions; scale 4 with per-property rules.
C: impact 4 for learning outcomes; relevance 5 from Studio; feasibility 3 because longitudinal evaluation is needed; data 2 for missing attempts; demo 4 for clear recommendations; scale 5 for reusable curricula.
D: impact 3 because inquiry volume is unknown; relevance 4 from discovery workflow; feasibility 5 for small-corpus retrieval; data 4 for public descriptions but no labelled briefs; demo 4 for evidence matching; scale 4 with catalog governance.
E: impact 4 for potential support workload; relevance 4 because support exists but pain is unverified; feasibility 4 for mature retrieval patterns; data 2 for missing manuals; demo 4 for cited answers; scale 4 with tenant isolation.
F: impact 4 for incident cost; relevance 4 from cloud services; feasibility 3 for seasonality and incident validation; data 2 for absent telemetry; demo 4 for time-series plots; scale 4 with operational investment.

## Why invest in A rather than the others?

A combines direct product adjacency, accessible licensed labels, measurable errors and a short path to a supervised pilot. It creates an opportunity to test reliability and operator usefulness before paying for broad integrations or generative automation. D is a strong fallback if Revio already has an equivalent triage workflow. B/C/F need private longitudinal data before credible evaluation. E lacks a useful public support corpus.

Sensitivity: lowering A's data score from 4 to 2 gives 4.20; lowering impact from 4 to 3 as well gives 3.95, narrowly above C/D at 3.90. If relevance also falls by one point after product discovery, A falls to 3.70 and D becomes preferable. The recommendation is conditional, not an assertion that Cynbit lacks the feature.
