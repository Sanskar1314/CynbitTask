# Dataset card

Training/evaluation: Sentiment Labelled Sentences, Dimitrios Kotzias, 2015, UCI Machine Learning Repository, DOI https://doi.org/10.24432/C57604 . Source landing page: https://archive.ics.uci.edu/dataset/331/sentiment+labelled+sentences . Accessed 2026-10-16. Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Attribution retained here; raw files unmodified. Normalization and deduplication are derived transformations performed at runtime. File hashes and original download URL are in raw/manifest.json.

Original corpus: 3000 sentences, 1000 each from Amazon product, IMDb movie and Yelp restaurant reviews, balanced binary sentiment within each source. It is an old, curated English sentence dataset. It excludes a neutral label and is not representative of modern multilingual Indian business reviews. Public availability does not imply the data is free of sensitive content. Do not infer author demographics.

Splits: seed 42, stratification by source and label, 60/20/20 after normalized duplicate removal. Conflicting labels for identical normalized text are excluded. Exact duplicate leakage is controlled; original author, business and review-group IDs are unavailable, so author/business-level and near-duplicate leakage cannot be ruled out. This limits the strength of generalization claims.

Synthetic demo: data/sample/reviews.csv is manually authored illustrative feedback with fictional locations, IDs and dates. It is not Cynbit customer data, not used to train the classifier, and not a sentiment accuracy benchmark. Theme and safety examples exercise deterministic policies only.
