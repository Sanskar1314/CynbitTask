# Interview preparation in simple English

## A short explanation you can say aloud

StockSense is a demo that helps a shop owner review future demand, stock orders and expiry. It uses Seasonal Poisson Regression for the current sample data and compares it with simpler methods. Its average test error is about 2.86 units per product per day, but the data is generated, so real-shop accuracy is still unknown. The stock rules explain each suggested order, and the owner makes the decision.

## Questions and answers

### 1. What does this project do?

It helps a shop owner review demand, stock orders, expiry risks and customer requests.

### 2. Is it an existing Cynbit product?

No. It is an assessment proposal. A live Revio connection is not implemented.

### 3. Does Revio already have these features?

We have not verified whether an equivalent inventory feature exists privately. Confirm this with Cynbit.

### 4. Who would use it?

The proposed users are kirana owners and staff who buy stock. They are not verified existing Revio users.

### 5. Where did the data come from?

A Python generator created the shop records. Public Google Calendar supplied the festival dates.

### 6. How large is the dataset?

13 products, 12 with sales over 1,020 days: 12,240 sales rows, 24 batches, 3 purchase orders, 14 example reviews and 28 festival entries.

### 7. What dates do the sales cover?

1 January 2024 through 16 October 2026.

### 8. Which model is selected?

Seasonal Poisson Regression, using scikit-learn PoissonRegressor. It trains separately for each eligible product.

### 9. Why this model?

It predicts nonnegative counts, learns seasonal patterns and had the lowest model-selection error among the tested methods.

### 10. What does it learn from?

Time of year, weekday, gradual trend and festival preparation windows, fitted against usable past sales.

### 11. Are seasons a separate prediction?

No. They contribute to the same daily forecast used by stock planning.

### 12. How are festivals handled?

The week before each festival and the festival day are marked. Past event windows are combined to learn one festival effect per product.

### 13. Why combine different festivals?

There are too few examples of each named festival to fit reliable separate effects. This is simpler but cannot distinguish each festival independently.

### 14. What does MAE 2.860 mean?

The average absolute mistake was about 2.86 units per evaluated product per day in the synthetic test.

### 15. Can I say the model is 81.48% accurate?

No. WAPE is 18.520%, but subtracting that from 100 is not a valid percent-correct accuracy claim.

### 16. What are RMSE and bias?

RMSE gives more weight to big errors. Bias shows whether forecasts are generally too high or too low. Current values are 3.921 and -0.040 units.

### 17. How was the model tested?

Four earlier 30-day periods chose the method. Twelve later 30-day periods measured its errors, with training restricted to records available before each forecast.

### 18. What is a product-day?

One product on one date. The main test scores 4,200 such records.

### 19. Why not randomly mix dates for testing?

That can let future information help predict the past. Time-ordered tests are closer to how forecasting is used.

### 20. What are the comparison methods?

A 28-day average, repeating the last week, and HistGradientBoosting, which combines small decision trees.

### 21. Is the data realistic enough?

It is useful for demonstrating code, but too simplified to establish real-shop performance. We need real records and separate future tests.

### 22. Why ignore some stockout days?

If a shop sells its last three packets, true demand may be higher than three. That sale does not reveal full demand.

### 23. What if there is no history?

The app withholds an exact forecast. With some history but not enough for annual patterns, it can use the simple average.

### 24. What is review period?

The number of days between checking stock and deciding on orders.

### 25. What is safety buffer?

Extra demand-days of stock kept as a precaution. At 20 units/day, a 1.5-day buffer adds 30 units.

### 26. What is lead time?

The supplier delivery wait after placing an order.

### 27. How is an order calculated?

Expected demand during lead time plus review period, plus safety stock, minus usable stock and relevant confirmed deliveries, then adjusted for expiry and constraints.

### 28. Why might the app suggest less than the target?

Storage, expiry risk, packs or the minimum supplier order can make the full target unsuitable.

### 29. What is FEFO?

First Expiry, First Out: use the batch that expires earliest before later-expiring stock.

### 30. Does AI predict the expiry date?

No. The recorded date determines expiry. Forecasts estimate what may remain unsold before it.

### 31. What does a blank expiry-risk value mean?

The risk may be unknown, such as when expiry is beyond the 30-day forecast. Blank is not a guarantee of safety.

### 32. Do reviews change demand quantities?

No. Simple word rules highlight issues for a person to investigate.

### 33. Is an LLM being used?

No. Forecasting uses statistical/ML methods and review checks use English word rules.

### 34. Is Google Calendar live?

The dates were imported through the connected calendar. The app reads a saved snapshot and does not continuously sync.

### 35. Why upload all six tables together?

They refer to one another. Checking them together prevents an incomplete or inconsistent replacement.

### 36. Where are uploaded records saved?

They stay in the local app session unless the user chooses local saving. The saved snapshot uses SQLite.

### 37. What tests passed?

26 code checks covering data, forecasts, stock decisions, events, seasons and screen navigation. Passing code tests is not proof of real accuracy.

### 38. Can the app place an order?

No. It creates a draft recommendation for owner review.

### 39. What would you do next?

Collect permissioned real data, check stock records, compare models on later unseen periods, and measure stockout and expiry costs with owner review.

### 40. What should I avoid claiming?

Do not call generated data Cynbit data, claim an unverified integration or missing feature, present WAPE as accuracy, or claim measured real-store savings.
