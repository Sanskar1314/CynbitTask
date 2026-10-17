# What each project file contains

## File types first

A `.py` file contains Python code. A `.csv` file contains a table. A `.json` file stores named values and lists. A `.md` file is editable written documentation. A `.pdf` file is the formatted version to read or share. A `.png` file is an image. You do not need to understand every line of code to understand how the project fits together.

## Reports: which one should I open?

| File in reports/ | What it contains and why it exists |
|---|---|
| AI_Opportunity_Report.pdf | The shop problem, intended users, relation to Cynbit, possible benefits and limits. Start here for the business idea. |
| Technical_Approach_Report.pdf | The model name and settings, data specification, error results and stock calculations. Read this to understand how it works. |
| Complete_Project_Explanation.pdf | The everyday-language walkthrough, this file guide and short interview answers. Use it while learning or demonstrating the app. |
| Matching .md files | Editable text for the three PDFs. The Complete Project Explanation is assembled from the guide files listed below. |

## Data files: the six tables

All six CSVs are in data/sample/. They are linked by product_id, so a sale for P11 can be matched to the correct product and stock. The row counts below describe the bundled demo, not a required size for uploads.

| File | What one row means |
|---|---|
| products.csv: 13 rows | One product and its price, supplier and ordering rules |
| sales.csv: 12,240 rows | One product's sales and stock movement on one date |
| batches.csv: 24 rows | One current group of stock with its own expiry information |
| purchase_orders.csv: 3 rows | One supplier order and its expected arrival date |
| reviews.csv: 14 rows | One example customer review |
| festivals.csv: 28 rows | One named festival on one date, with its source |

### products.csv columns

product_id is the code used to connect files. product_name and category describe the item. selling_price is what the customer pays; cost_price is the example purchase cost. supplier_id identifies the supplier.

lead_time_days is the delivery wait. minimum_order_quantity is the smallest supplier order. pack_size is the number of units in a pack. shelf_life_days is the assumed remaining life of a new delivery, not the official expiry date of existing stock. max_stock is the storage limit in units. backorders are orders still waiting to be supplied. aliases are other names used to match a product in reviews.

### sales.csv columns

date and product_id identify the day and product. quantity_sold is the recorded sale and unit_price is the price per unit. These four fields are required for uploaded sales.

The demo also records opening_stock, received_units, available_stock and closing_stock. They explain what was on the shelf, what arrived and what remained. stockout marks a known shortage. prior_stock_writeoff records carried stock removed before the opening balance used that day. These fields help explain why a low sale may not mean low demand.

promotion marks the example promotional days generated in the demo. It is not currently used as a future promotion plan by the selected model. simulated_demand is the generator's demand before stock limits. It is only used for a separate evaluation and must not be confused with a real observable sales field.

### batches.csv columns

batch_id identifies a batch and product_id links it to the catalog. manufacturing_date and expiry_date are recorded dates. quantity_remaining is the amount still held. cost_price and supplier_id give the cost and supplier. Blank batch dates mean unknown. The app must not invent them.

### purchase_orders.csv columns

purchase_order_id identifies the order. product_id and quantity_ordered say what is coming. order_date says when it was ordered and expected_delivery_date says when it should arrive. status is confirmed, draft, received or cancelled. Only relevant confirmed future deliveries count as incoming supply in planning.

### reviews.csv columns

review_id identifies a review. date, rating and review_text contain the feedback. product_id can identify a product if it is already known; otherwise it can be blank. The simple word rules try to find product mentions and concerns. The reviews are written examples, not a collected customer dataset.

### festivals.csv columns

festival_name, festival_date and region describe the event. calendar_source says where it came from. The bundled file also has source_title, source_url and date_status so you can inspect the original name, link and any tentative label. All-day dates are kept as listed by the calendar.

### Other data files

| File | Meaning |
|---|---|
| data/sample/metadata.json | States that the business data is synthetic; records seed 42, the snapshot date, version and table row counts. |
| data/calendar/google_india_holidays.json | Saved public Google Calendar entries and their source details. It is not a login token or private appointment file. |
| .local/snapshot.sqlite | Optional local database created when Save snapshot locally is used. It contains the saved tables; it is not the main source of bundled demo data. |

## Application code

| File | What it does |
|---|---|
| app/app.py | Builds the seven screens, responds to controls and connects the data, forecasts and stock calculations. |
| src/data.py | Reads the CSVs, checks them, prepares usable sales history and saves or loads the local database. |
| src/seasonal_model.py | Trains the selected product-by-product seasonal Poisson model and calculates its predictions. |
| src/forecasting.py | Runs all four forecasting methods, checks whether a product has enough history, compares errors and chooses a method. |
| src/calendar_data.py | Reads the saved public calendar and makes event names and dates consistent. |
| src/seasonality.py | Summarizes historical monthly sales and past festival periods. These summaries are not a second forecast. |
| src/inventory.py | Calculates draft orders, uses earlier-expiring stock first and checks storage, delivery, shelf-life and pack rules. |
| src/reviews.py | Matches product names and simple English phrases to requests or complaints. No LLM is used. |
| src/__init__.py | Marks src as a Python package so its modules can be imported. |

## Scripts you can run

| File | What running it does |
|---|---|
| scripts/generate_data.py | Recreates the synthetic demo tables. It is not a script for collecting real sales. |
| scripts/evaluate.py | Repeats the time-based model comparison and writes the current error report and prediction table. |
| scripts/build_reports.py | Converts the report text into PDFs and assembles the complete guide. It does not train a model. |

## Evaluation files: proof behind the numbers

| File | What it contains |
|---|---|
| evaluation/metrics.json | Model chosen, training/test dates, overall error scores and results by product, season and event window. |
| evaluation/backtest_predictions.csv | Individual historical predictions, their actual values, model names and periods. Use it to investigate a particular mistake. |
| evaluation/archive/v1/metrics.json | Old results from the first version. Different data or test periods make direct comparison unsafe. |
| evaluation/archive/v2/metrics.json | Old results before the latest hot-drink and festival correction. Kept as history, not the current score. |

“Backtest” means pretending to stand at an earlier date, predicting later dates, and then comparing with what happened. In the CSV, origin is that earlier date, horizon is how many days ahead the prediction is, prediction is the estimate and actual is the usable recorded sale. split says validation or test. A blank actual can mean the sale was not usable for scoring.

## Tests: checks on the program

| File | What it checks |
|---|---|
| tests/test_data.py | Invalid files, data rules and local saving/loading |
| tests/test_engines.py | Forecast and inventory examples, stockouts, expiry, delivery timing and review behavior |
| tests/test_seasonal_model.py | Calendar dates, product-specific seasons, festival effects, limited history and prevention of future-sales leakage |
| tests/test_app.py | Navigation through the seven screens and protection against incomplete uploads |

There are 26 passing tests in the latest recorded run. This means those checks pass; it is separate from model accuracy.

## Written guides and project records

| File | What it explains |
|---|---|
| README.md | Installation, launch commands, project summary and links to the reports |
| docs/Project_Walkthrough.md | The plain-English explanation of the model, data, screens and examples |
| docs/File_Guide.md | This guide to the files and their meanings |
| docs/Interview_Preparation.md | Short answers to common project questions |
| docs/Company_Research.md | Dated research sources and what was or was not verified about Cynbit |
| docs/Data_Card.md | Dataset fields, assumptions and changes made to the synthetic data |
| docs/Calendar_Integration.md | Where festival dates came from and why the app uses a saved calendar copy |
| docs/Engineering_Decision_Log.md | Historical reasons for technical choices, including old versions. It is a developer record, not the beginner reading guide. |
| docs/PROJECT_STATE.md | Current project status and where work stands |
| docs/Execution_Log.md | A dated record of work performed |
| docs/Development_Log.md | Development milestones and earlier commit references |
| docs/QA_Record.md | Tests, browser checks and document checks that were performed |

## Setup, images and working folders

| File or folder | Meaning |
|---|---|
| requirements.txt | Exact Python package versions used by the app and tests |
| requirements-reports.txt | Extra packages needed to create and inspect PDFs |
| AGENTS.md | Project workflow rules for the coding assistant |
| .gitignore | Lists local/generated files that Git should not track |
| .git/ | Git's saved change history and repository information |
| .venv/ | The local Python environment and installed libraries; not application source code |
| assets/dashboard.png | Screenshot used to show the dashboard |
| assets/forecast.png | Screenshot used to show the forecast chart |
| tmp/pdfs/ | Temporary rendered pages used to inspect PDF layout; not final reports |
| .DS_Store | A macOS folder display file; unrelated to forecasting and left untouched |

## Where to look when something is wrong

If a CSV fails, start with its column names and the error shown by data.py. If a forecast seems wrong, inspect the product's sales history and the saved predictions before changing the model. If the forecast looks reasonable but the order does not, check inventory.py and the batch, supplier and delivery records. If a chart or button fails, start with app/app.py.
