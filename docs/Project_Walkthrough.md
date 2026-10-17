# StockSense in simple English

## Start here

StockSense is a working demo for a shop owner. It estimates future demand and helps the owner review stock purchases, expiry risks and customer requests. It does not place orders. Its sales data is made up by a program, so it cannot yet tell us how well it will work in a real shop.

Read the AI Opportunity Report for the business idea. Read the Technical Approach Report for how the calculations work. This guide explains the screens, files and words you will see while using or presenting the project.

## Which model does the app use?

The current demo uses **Seasonal Poisson Regression**. The Python class is called `PoissonRegressor`, from the scikit-learn library. A separate model is trained for each product that has enough sales history.

A regression model predicts a number. Here, that number is the expected units sold per day. Poisson regression is designed for counts and keeps the expected number above zero. A result such as 7.5 means an average expectation, not that the shop can sell half a packet.

The model learns four kinds of patterns together: changes over the year, differences between weekdays, slow growth or decline over time, and festival preparation days. These produce **one forecast**, which the ordering and expiry pages also use.

The annual pattern uses sine and cosine waves. These are smooth repeating curves that help the model move gradually from one season to the next. The model does not simply apply a rule such as “increase every product in winter.”

Festival preparation means the seven days before a festival plus the festival day. For each product, the current model learns one shared festival effect from all past festival windows. It does not learn a separate Diwali effect and Holi effect. We made this choice because there are only two or three past examples of each named festival. Separate effects were reacting too strongly to random variation.

### Why choose this model?

It fits the kind of number we want to predict, can learn a different seasonal pattern for each product, and runs on a normal laptop. More importantly, it had the lowest average error in the earlier periods used to choose the model. This is a reason to use it in this demo, not proof that it is the best model for a real shop.

The app also compares it with three other methods. A 28-day average repeats the recent average. A weekly repeat method copies the last week's pattern. HistGradientBoosting is a machine-learning model that combines many small decision trees to learn more complex relationships.

### When does the app avoid this model?

The seasonal model needs at least 180 usable daily observations spread across at least 365 days. Otherwise, it uses the 28-day average and labels that choice. If even recent sales history is too limited, it gives no exact forecast. A new product does not get a made-up demand number just because a review asks for it.
## How accurate is it?

**Real-shop accuracy is not known.** The following numbers come from the project's computer-generated data. We should not present them as results from Cynbit customers or real shops.

| Method | Error used to choose the model | Error in later test periods |
|---|---|---|
| Seasonal Poisson Regression | 3.088 units/day | 2.860 units/day |
| HistGradientBoosting | 3.178 units/day | 2.964 units/day |
| 28-day average | 3.507 units/day | 3.374 units/day |
| Repeat the last week | 4.230 units/day | 4.133 units/day |

Both error columns use **MAE: Mean Absolute Error**. It is the average size of a mistake, ignoring whether the forecast was too high or too low. If the actual sale is 10 and the forecast is 7, the error is 3 units. An MAE of 2.860 means the forecast was wrong by about 2.86 units per evaluated product per day on average. It does not mean every forecast is within that amount.

| Other result | Value | What it means |
|---|---|---|
| WAPE | 18.520% | Add all absolute errors, then divide by all actual units sold. Lower is better. |
| RMSE | 3.921 units | An error score that gives extra weight to large mistakes. Lower is better. |
| Bias | -0.040 units | Average forecast minus actual sales. The small negative value means slight overall underprediction. |

**Do not call this 81.48% accuracy.** Subtracting WAPE from 100 does not create a reliable “percent correct” score. Forecasting predicts quantities, so the size of each error matters.

On the same current dataset, the chosen model's MAE is about 3.5% lower than boosting and 15.2% lower than the average method. That is a comparison of forecast errors, not a percentage of money saved. A three-unit error may be small for a product selling 50 units a day but serious for one selling four.

### How were these numbers measured?

First, the models learned from older records and predicted four later 30-day periods. Those periods were used to choose the model. Next, the chosen method was kept fixed while all methods were tested over twelve more 30-day periods, covering 360 days.

At each step, training used only records from before the forecast date. As time moved forward, training could include records that had become available since the previous step. This imitates updating a model as a shop collects more sales.

The main test contains **4,200 product-days**. One product-day means one product on one date. There were 4,320 possible records for the 12 products across 360 days; 120 were left out because sales were limited by stock availability. The thirteenth product has no sales history and is not scored.

This project has been developed and adjusted using the same simulation. It is not an independent real-world test. Earlier versions also used different data, so their scores should not be used to claim a clean before-and-after improvement.
## What is in the dataset?

The shop records are **synthetic**, which means a Python program created them. They are not downloaded from a real store and are not Cynbit data. The festival dates are the exception: they were imported from the public Google Calendar called Holidays in India.

| Item | Current dataset specification |
|---|---|
| Store coverage | One fictional kirana store |
| Sales dates | 1 January 2024 to 16 October 2026 |
| History length | 1,020 days for each of 12 products |
| Products | 13 listed products; 12 have sales and one is a new product |
| Sales records | 12,240 rows: one product on one day per row |
| Stock batches | 24 rows describing stock held at the latest snapshot |
| Purchase orders | 3 examples of incoming or planned supply |
| Customer reviews | 14 written examples, not real customer messages |
| Festival dates | 28 entries: seven festival names across 2024-2027 |
| Calendar import date | 17 October 2026; saved copy, not automatic live sync |
| Dataset version | winter-calendar-v3 |
| Random seed | 42; this makes the same generator repeatable |

Products include cola, water, mango drink, milk, yogurt, chips, tea, coffee, biscuits, chocolate, packaged sweets and rice. Sugar-free cola is the new product without sales history. Prices and stock values are examples in Indian rupees.

The generator combines a starting demand level with seasonal changes, weekends, gradual trends, festival periods, example promotions and random variation. It also creates supply interruptions so some days run out of stock. It deliberately includes expiry and overstock examples so those screens can be demonstrated.

The current tea and coffee example has a winter peak. The earlier demo curve peaked near October by mistake; the generator was corrected. That change is an assumption in a fictional example, not something discovered in real shop records. The gifting example also has a festival increase built into the generated demand. A model matching these patterns does not prove that it will match a real shop.

### Why this data is a major limitation

Real demand can change with location, prices, promotions, weather, competitors, customer habits and supply problems. The small simulation does not capture all of that. A good-looking test result can therefore coexist with forecasts that feel unrealistic.

We need real sales and stock records, with permission to use them, before judging business usefulness. Those records should include dates, product quantities, price changes, promotions and stock availability. We should test future periods that were not used while adjusting the model, and inspect errors for each product, not only one average score.

## What each screen does

| Screen | What you use it for |
|---|---|
| Executive Dashboard | Start here. See the products needing attention, draft orders, sales history and upcoming festivals. |
| Product Demand Forecasting | Choose a product and view its next 7, 14 or 30 days. Seasons and festivals are part of this one forecast. |
| Smart Reorder Planner | See the suggested purchase quantity and the stock, delivery or supplier rule behind it. |
| Expiry Management | Check recorded batch dates and estimated units that may remain unsold before expiry. |
| Slow-Moving Inventory | Find products with low sales or more stock than the next 30 days appear to need. |
| Review Intelligence | Read product requests and availability or quality concerns found by simple English rules. |
| Data Management | Inspect templates, upload a complete dataset, manage calendar dates, run evaluation and save or load locally. |

The review-period control means days between stock checks. The safety-buffer control means extra demand-days of stock. For example, a 1.5-day buffer and demand of 20 units a day adds 30 units. Both are settings for the owner's policy, not values proved correct by the model.

## How to read the forecast chart

The solid grey line is recorded sales. The dashed line is the model's prediction. Shaded dates cover the week before a festival and the festival day. There is only one future forecast line. The monthly history chart inside the expandable section describes old sales; it is not another prediction.

A forecast can drop after a festival window ends. That is different from predicting a drop during the festival. Weekdays can also explain small changes from day to day. The forecast shows an expected amount, so it is usually smoother than noisy daily sales.

The current sweets example has about eight units a day during the Diwali preparation window and about four on nearby ordinary days. Tea and coffee show a winter rise in this demo. These are learned from generated examples and should not be treated as universal rules for every shop.

## A worked order example

A supplier takes four days to deliver. You check stock every seven days. The app therefore plans for eleven days. At 20 units a day, demand is 220. Add a 30-unit safety buffer. Subtract 80 usable units already held and 20 confirmed incoming units. The starting suggestion is 150 units.

Expiry, storage and supplier rules are then checked. If a rule lowers that number, read the reason beside it. A zero order might mean enough stock, unsafe extra stock, an unknown expiry date or too little history. Zero does not always mean “nothing needs attention.”

## A worked expiry example

There are 80 yogurt units that can be sold over the next five days. If expected sales are six each day, about 30 may sell and 50 may remain at risk. The earliest-expiring stock is used first. This is FEFO, short for First Expiry, First Out.

The model never decides the official expiry date. That date must come from a real batch record. Missing expiry needs checking. Stock that expires beyond the forecast period cannot be declared safe simply because a risk value is blank.

## What happens when you upload real data?

All six related tables must pass validation before the app replaces its current dataset. Validation means checking that required columns, dates, IDs and quantities make sense. Failed uploads leave the previous data active.

A new uploaded dataset starts with the simple 28-day average. It does not inherit the demo's model score. Run that dataset's evaluation to compare methods for it. Records are saved to the local database only when you choose to save them.

## Five-minute presentation

1. Say that this is a synthetic-data demo and show the dashboard.
2. Choose packaged sweets in Product Demand Forecasting. Explain the recorded line, forecast line and shaded festival dates.
3. Explain the model name and why the project chose it. Use MAE as the main error measure; do not claim an accuracy percentage.
4. Open the reorder explanation and work through the 150-unit example above.
5. Show an expiry warning and the new sugar-free product with insufficient history. End with the need for real shop data.

## Terms translated into everyday language

| Term | Simple meaning |
|---|---|
| SKU / product ID | A code for one product, such as P11 for packaged sweets |
| Forecast horizon | How many future days are predicted |
| Feature | An input the model uses, such as weekday or time of year |
| Training | Letting the model learn patterns from past records |
| Validation period | An earlier test period used to choose a method |
| Test period | A later period used to report the chosen method's errors |
| Baseline | A simple method used for comparison |
| Stockout | A product ran out, so sales may be below customer demand |
| Snapshot | The records as of one date; the demo is dated 16 October 2026 |
| Lead time | Days between ordering and receiving stock |
| Batch | A group of stock with its own manufacturing and expiry details |
| MOQ | The supplier's smallest allowed order |
| Backorders | Customer orders still waiting to be supplied |
| Bias | Whether forecasts tend to be too high or too low on average |
| Synthetic | Created by a program instead of collected from real business activity |
| API | A way for two programs to exchange information; a live Revio connection is not implemented here |
