# Interview preparation

Use these as explanations of this implementation, not claims of prior professional experience. Be clear about assistance used to build the project and demonstrate your understanding with the code and tests.

## 30-second pitch

StockSense is a proposed inventory intelligence module that could complement Revio. It helps a kirana owner forecast demand, review replenishment and identify expiry or excess stock. I compare simple baselines with seasonal Poisson regression and gradient boosting using chronological validation, then apply transparent inventory rules. Customer reviews suggest product investigations but never become invented sales quantities. The working demo uses synthetic data, so its results are engineering evidence, not proof of real-store savings.

## Two-minute explanation

A retailer can have both stockouts and overstock. A sales forecast alone does not solve that because inventory may expire or arrive too late. StockSense validates sales, batches, orders, product rules, reviews and a calendar as one snapshot. It masks known stockout days rather than treating constrained sales as full demand.

One product-specific model combines season, weekdays, trend and festival dates into each daily forecast. Four validation windows select seasonal Poisson regression over boosting and two simple baselines. Twelve subsequent rolling windows test360 days. Synthetic observed MAE is2.860 versus2.964 for boosting and3.374 for the average.

The rule engine then simulates earliest-expiry-first consumption and dated receipts. It uses lead time plus review period, a configurable buffer, and conservative shelf-life, capacity, pack and MOQ limits to produce draft quantities. Unsupported products and unknown expiry require investigation. Reviews highlight requested variants or availability issues without numerically inflating forecasts. A production pilot would need consented real data, verified dates, integration and measured inventory outcomes.

## Five-minute technical walkthrough

Minute1: Explain the merchant problem, Revio's advertised review-management context and why StockSense is a proposed complement, with feature overlap unverified.

Minute2: Open the six CSV templates. Explain availability-censored sales, recorded batch expiry, confirmed purchase orders and snapshot date. Show validation rejecting an incomplete upload without changing data.

Minute3: Show joint annual, weekday, trend and festival features in src/seasonal_model.py and the retained boosting comparator in src/forecasting.py. Explain why random splitting would leak future information. Display measured baseline comparisons and distinguish WAPE from accuracy.

Minute4: Work through220 demand +30 buffer -80 stock -20 incoming=150. Show FEFO and the80-unit yogurt/five-day example. Explain why pack rounding cannot exceed a safe cap and why an early shortage cannot be repaired by a late receipt.

Minute5: Show sugar-free review requests and the no-history warning. Explain uncalibrated uncertainty, synthetic data limits and the real-data shadow pilot needed before purchasing automation.

## Questions and concise answers

### 1. What does the application do in plain language?
It helps a shop owner decide what stock needs attention: buy more, pause buying, inspect expiring batches or investigate a customer request. It explains each suggestion.

### 2. Does Revio already offer this?
Its public page advertises review management and related AI. I did not establish whether inventory exists privately. StockSense is a proposal; overlap must be checked with Cynbit.

### 3. Who would use this?
Kirana owners and purchasing staff are the proposed users. Revio publicly describes brand and location roles; kirana adoption is not verified.

### 4. Why choose this problem?
It links measurable ML forecasts to an operational decision and makes it possible to test business mathematics separately from model quality.

### 5. Where did the data come from?
A reproducible seed42 generator created the business records; public Google Calendar supplied actual festival dates. None are Cynbit data. The app also accepts a validated user-supplied snapshot.

### 6. Why not train directly on every sale?
Sales can be limited by stock. A shelf with three units cannot reveal whether demand was three or fifteen. Known constrained days are masked, although this does not fully solve censored-demand bias.

### 7. How do you handle missing dates?
They remain unknown after daily reindexing. They are not silently filled with zero demand.

### 8. Why seasonal Poisson regression?
It models nonnegative daily counts with smooth annual, weekday, trend and event effects learned jointly for each product. It beat boosting and simple baselines on pooled validation. Boosting remains a useful nonlinear comparator.

### 9. Why not LSTM or a large language model?
Neither is necessary for this small structured dataset. They add complexity, data needs or costs without demonstrated benefit here.

### 10. What are the main features?
The selected model uses two annual sine/cosine harmonics, weekday, trend and a pooled festival preparation window. The boosting comparator uses lags, rolling statistics, missingness, product identity, horizon, weekday, cyclic month and event proximity. No future stock, future sales or latent demand enters the predictors.

### 11. What does direct multi-horizon mean?
In the retained boosting comparator, each future day gets its own feature row from the same known origin history. Predictions are not fed back recursively as actual lags.

### 12. How is leakage prevented?
Features stop at the origin, labels stop at the training cutoff, validation follows training chronologically, and the final test does not choose the model. A causality test changes future sales and checks that earlier features stay identical.

### 13. What are the baselines?
A28-day observed average and a repeated last week. Missing weekly observations use only the prior28-day mean.

### 14. What happens if the baseline wins?
The selection rule chooses it. Model complexity is not the objective; validation performance is.

### 15. What are the measured results?
Seasonal Poisson rolling test MAE2.860, RMSE3.921, WAPE18.520%, bias-0.040. Same-data boosting MAE2.964; average MAE3.374. There are4,200 valid product-days across360 days, not real customer outcomes.

### 16. Is WAPE19% the same as81% accuracy?
No. WAPE is aggregate absolute numerical error divided by aggregate actual units. Subtracting it from100 does not produce classification accuracy.

### 17. Why report bias?
Persistent underprediction can cause shortages even when average absolute error looks acceptable. Positive bias means overprediction; negative means underprediction.

### 18. How are festivals handled?
Festival preparation windows are learned within the same forecast using actual public Google Calendar dates imported17 October2026. No second seasonal forecast or blanket uplift is added. The app uses a snapshot; regional/tentative dates need review.

### 19. Is the event uplift causal?
No. Trend, promotions and overlapping events can confound it. The evidence table does not apply an extra forecast multiplier.

### 20. How do you calculate an order?
Sum forecast over lead time plus review period, add safety buffer, subtract usable stock and confirmed incoming adjusted for expiry, add backorders, then apply capacity, receipt-life, MOQ and pack constraints.

### 21. Why use actual cumulative forecasts?
Demand can change by weekday or event. Summing daily forecasts preserves those changes instead of assuming the same daily average everywhere.

### 22. What is safety stock here?
A configurable number of demand-days. It is a transparent policy buffer, not a calibrated95% service-level calculation.

### 23. What if supply arrives too late?
The simulation flags shortages before arrival. It does not pretend later stock prevents earlier lost sales; the owner may need to expedite supply.

### 24. Why can the order be below the calculated target?
Shelf life, storage, pack sizes and MOQ can make the target infeasible. The system explains the binding constraint rather than ordering unsafe excess.

### 25. How does FEFO work?
Each day's demand consumes eligible stock with the earliest recorded expiry first. Expired and unknown-expiry batches do not supply the forecast.

### 26. Does AI predict the official expiry date?
No. Dates come from records. Forecasts estimate how many units might remain unsold before that date.

### 27. How is an expiry beyond30 days handled?
Its final unsold-at-expiry is unknown because demand is only forecast30 days. Blank risk is not zero risk.

### 28. How do reviews affect quantities?
They do not directly. Rules show product requests, availability, variants and quality signals for human investigation. There is no validated review-to-units conversion.

### 29. How do you avoid matching cola inside sugar-free cola?
Longer aliases claim their text spans first; overlapping shorter aliases are skipped.

### 30. What happens to a new product?
Without enough observed history it receives no precise demand forecast or purchase quantity. Requests support cautious investigation, not fabricated certainty.

### 31. How does CSV validation protect the workflow?
All six tables pass schema, dates, keys, numeric and reference checks before replacing the snapshot. A bad upload leaves the old state intact.

### 32. Why SQLite?
It provides simple optional local persistence without a separate service. It is not a substitute for tenant isolation or authenticated production storage.

### 33. What testing did you perform?
Numerical business-rule tests, invalid-data and persistence checks, feature causality, no-history/expiry/receipt/event/review cases and automated navigation of all seven UI sections. Evaluation is executed separately and saved.

### 34. What is the largest limitation?
External validity: synthetic data can only show that the approach works on the simulation. Real-store data quality, demand patterns and supplier behavior may differ substantially.

### 35. What would you do next?
Confirm Cynbit fit and interfaces, collect consented real data, run shadow recommendations, evaluate SKU-level errors and inventory costs, then add monitored authenticated deployment and human approval.

### 36. How would you measure business success?
Compare stockout hours, expiry cost, inventory holding and owner review time against a defined baseline while controlling for promotions, seasons and supply changes. Forecast MAE alone is insufficient.

### 37. What would you change if real demand is intermittent?
Evaluate intermittent-demand methods and probabilistic/count models against the same chronological protocol. Do not assume the current selected model will win.

### 38. Can this application place orders or be used publicly today?
No orders are placed. It runs locally without authentication. A public production service requires additional access controls, monitoring, consent and integration work.

### 39. Why is priority separate from confidence?
Urgency and certainty are different. An expired batch is urgent even if demand prediction is weak. A clear forecast does not make every product urgent.

### 40. What should you never overclaim in the interview?
Do not call synthetic data Cynbit data, claim a live Revio integration, assert a feature is absent without evidence, present WAPE as accuracy, or claim real-world savings from this simulation.
