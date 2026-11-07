# TMS: NYC flights 2023, flight alerts for a travel agency

Data scientists of a travel agency that books flights from New York. Data: every flight that left JFK, LGA or EWR in 2023 (435,352 flights) with hourly weather, planes, airports and airlines. Two predictions, each made two hours before the scheduled departure:

1. Will a flight leave more than 15 minutes late, or be cancelled?
2. Will a flight be cancelled?

Training: January to September 2023. Validation: July to September (models fitted on January to June). Test: October to December 2023, scored once.

## Repository layout
```
README.md
requirements.txt
data/            # never committed (see .gitignore): raw/ and processed/
notebooks/       # 01_clean ... 07_decision, utils.py
slides/          # tms_final.pdf, tms_final.pptx (cover + 13 slides), build_deck.py
```

## Data
nycflights23 (C. Ismay, S. P. Couch, H. Wickham, 2025), licence CC0: https://github.com/moderndive/nycflights23 . The files are not in this repo.

## How to run
1. Put `flights.csv`, `weather.csv`, `planes.csv`, `airports.csv`, `airlines.csv` in `data/raw/`.
2. `pip install -r requirements.txt` (Python 3.10 or newer).
3. Run the notebooks in `notebooks/` in order, `01_clean` to `07_decision` (06 takes about an hour, the others minutes). All seeds are 42.
4. Slides (optional): `python slides/build_deck.py` rebuilds the PPTX and PDF. It needs `python-pptx` and `pillow` (not in requirements.txt) and LibreOffice for the PDF.

## Main decisions
* **Late** = departure delay above 15 minutes, or cancelled.
* **Prediction time** = scheduled departure minus 2 hours; only information known then is used (automated leak tests in `05_features.ipynb`).
* **Weather join:** `weather.csv` is in UTC and `flights.csv` in New York time, so flights are converted to UTC before joining. The literal join from the Excel sheet is run once as a comparison.
* **Missing tail numbers:** all 1,913 are cancelled flights, so plane features of flights with a missing or unknown tail are filled with a random real aircraft of the same airline (seed 42), with no missing flag.
* **Metric:** PR-AUC, compared with the dumb answer ("nobody is late / cancelled"); accuracy is never a headline. Intervals are bootstrap intervals that resample whole days.
* **Airport groups** are fitted on January to September only.

## Known limits
One year of data from three airports. Weather is observed, not forecast. Train and test differ strongly (late 25.7% against 14.1%). Cancellation precision is low, and 115 of the 224 test cancellations fall on one day (18 December, cause not explained by the data). Models of the same family cannot be told apart on the test part.

## How AI tools were used
Claude (Anthropic) and Gemini (Google) were used as an assistant, working with me on some tasks. It was used for:
* debugging (an out-of-memory crash in notebook 06, a tie bug in the previous-flight feature, a divide-by-zero in the bootstrap of PR-AUC);
* proposing the project plan, suggesting the slide structure and text, and reviewing the slides against the plan.
* writing the README.md file for this project.

## Ledger: slide number, notebook, cell title
Every number on the slides comes from a notebook output.

| Slide | Number | Notebook | Cell title |
| --- | --- | --- | --- |
| 1 | 25.7% late or cancelled, 330,883 training flights; 435,352 flights | 01 | 6. Data report (drift row) |
| 1, 13 | two alerts tested on Oct-Dec; about 120 messages and 5 flights a day | 07 | 7. The two cards |
| 2 | 435,352 flights, 1,913 flights without a tail, all cancelled | 01 | 6. Data report |
| 2 | UTC join: +0.0005; plane fill +0.012 vs +0.206 | 06; 05 | B3. Weather decisions (test rows); 12. Ablation |
| 3 | monthly late-or-cancelled bars; 79.03%, 13.84 min, 2.47%, 8.41%, 22.91% | 04 | 1. The five metrics; 2. The monthly table |
| 3 | June and July not wetter or foggier; cause not explained | 04 | 4. Unusual months |
| 4 | 13.4%, 39.9%, 26.5 points [24.2, 28.9]; 11.5 to 36.3; 11.4 to 43.4 | 02 | Finding 1 |
| 4 | 27 of 273 days; 9.8%, 21.9%, 57.5%; 10.0% (max 27.1%); 21% of rainy days | 02 | Finding 2 |
| 4 | 0.231, 0.054, 0.032, 0.026, 0.021 | 06 | D1. Which columns matter? |
| 4 | rain +14.5 points [11.1, 18.1] | 02 | Finding 3 |
| 5 | B6 1.26, F9 1.25, WN 1.21, YX 0.76, G4 0.54; YX 29%, 9E 27%, Delta 9%; 1.0% to 1.7% | 02 | Finding 4 |
| 5 | Thursday 1.5%, Sunday 4.7%; 0.057 to 0.023; 8.7% | 02 | Finding 5 |
| 6 | 57 / 45 / 7 airports; 101,287 / 226,896 / 2,374 flights; 21.2%, 27.8%, 53.1%; 4.3%; 15% to 42%; 41.5 min; silhouette 0.322 | 03 | 7. One row per group; 3. Choose k |
| 7 | four leak tests | 05 | 11. Leak tests |
| 7 | 222,402 / 108,481 / 104,469 / 330,883 flights; 85.9%; 0.1406; 0.0021 | 06 | A1; A5. The dumb answers |
| 8 | PR-AUC with intervals of every model, both predictions | 06 | E2 and E3. Final results tables |
| 8 | strict +0.0019; literal +0.0005; without airport state -0.055 | 06 | B3. Weather decisions and ablations (test rows) |
| 8 | 224 cancellations, 115 on one day | 07 | 6. The finding for each card |
| 9 | cut-off 0.603; 123 a day; 11,275; 38.0% [34.7, 41.4]; 29.2% [24.1, 33.8]; 2.7x; 14.1%; 0.339 [0.301, 0.375] | 07; 06 | 7. The two cards (card 1); E2 |
| 9 | 13.1% to 49.6% (weeks with 100+ cases); stop rule 13% | 07 | 3. The same cut-offs by week; 7. The two cards (line 9) |
| 9 | mornings 5.3%; Newark 19.1% | 06 | D2. Where is the model wrong? |
| 10 | cut-off 0.136; 5.3 a day; 484; 93 of 224; 19.2% [0.6, 25.7]; 41.5% [1.0, 59.9]; 90x; 0.119 [0.002, 0.231]; top 1%: 47.3% | 07; 06 | 7. The two cards (card 2); E3 |
| 10 | 39 Newark cancellations missed; 115 of 224 on 18 December; 23% stop rule, 46.8% | 06; 07 | D2. Where is the model wrong?; 6. The finding for each card; 3. The same cut-offs by week |
| 11 | Alaska, American, Endeavor under-flagged; JetBlue most | 06 | D3. Fairness check |
| 11 | 25.7% to 14.1%; strict weather +0.0019 | 01; 06 | 6. Data report; B3. Weather decisions |
| 12 | 15 metric check values; four leak tests | 04, 05 | 1. The five metrics; 11. Leak tests |
