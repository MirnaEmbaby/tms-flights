# TMS: NYC flights 2023, a travel agency's data science project

**Status:** all 8 tasks are done (notebooks 01 to 07, slides, this README).

## What this project is
We are the data scientist of a travel agency that books flights from New York for its clients. Data: every flight that left JFK, LGA or EWR in 2023 (435,352 flights) with hourly weather, planes, airports and airlines. Three business questions (top of `01_clean.ipynb`) lead to two predictions that are turned into decision cards:

1. Will a flight leave more than 15 minutes late, or be cancelled?
2. Will a flight be cancelled?

Both are predicted two hours before the scheduled departure. Training: January to September 2023. Validation: July to September (models fitted on January to June). Test: October to December 2023, scored once.

## Repository layout
```
README.md
requirements.txt
data/            # never committed (see .gitignore); raw/ and processed/
notebooks/       # 01_clean ... 07_decision, utils.py (shared helpers)
slides/          # tms_final.pdf, speaker_notes.md, build_slides.py
```

## Data
Source: nycflights23 (C. Ismay, S. P. Couch, H. Wickham, "nycflights23", 2025), licence CC0. Original: https://github.com/moderndive/nycflights23 . The data files are not in this repo (`data/` is ignored).

## How to run
1. Put `flights.csv`, `weather.csv`, `planes.csv`, `airports.csv`, `airlines.csv` in `data/raw/`.
2. `pip install -r requirements.txt` (Python 3.10 or newer; CPU only).
3. Run the notebooks in `notebooks/` in order, `01_clean` to `07_decision`. Each one saves files in `data/processed/` that the next one reads, and each runs top to bottom with Kernel > Restart and Run All, e.g. `jupyter nbconvert --to notebook --execute --inplace notebooks/01_clean.ipynb`. Run time on 2 CPUs and 8 GB: 01 to 05 about 3 minutes in total, 06 about 65 minutes, 07 about 15 seconds.
4. Slides (optional): `python slides/build_slides.py` rebuilds `slides/tms_final.pdf` from `data/processed/` (needs `playwright` with chromium, not in requirements.txt).

All seeds are 42; two runs of 06 gave identical numbers.

## Decisions (what the plan fixed, and why)
* **D1** `late` = departure delay above 15 minutes, or cancelled (no departure time). Exactly 15 minutes is not late.
* **D2** Prediction moment = scheduled departure minus 2 hours. Only information known then is used as a feature (automated leak tests in `05_features.ipynb`).
* **D3** Second prediction = will the flight be cancelled. The fallback (delay regression) was not needed: best validation PR-AUC 0.353 against the gate 0.0768.
* **D4 (deviation from the Excel instruction)** The sheet says to join weather on `origin` + `time_hour`. `weather.csv` is in UTC and `flights.csv` in New York time, so a literal join pairs flights with weather 4 to 5 hours off. Flights are converted to UTC first (primary). The literal join is run once as a comparison row; the score changes by -0.0039 PR-AUC, inside the confidence interval.
* **D5** Two weather sets: weather of the scheduled hour (a stand-in for a forecast) and a strict set (only observations at least 2 hours before departure). Main results use the first; the strict set is an extra row (-0.0016, inside the interval).
* **D6** Validation = July to September (fit on January to June); final models refit on January to September.
* **D7** Dumb answers: nobody is late / nobody is cancelled (PR-AUC = prevalence). A hour-only baseline is also shown.
* **D8** Main metric PR-AUC; precision, recall, F1, lift at a cut-off; accuracy is never a headline (the dumb answer is 85.9% accurate).
* **D9** Prediction 1: logistic regression, histogram gradient boosting, random forest, PyTorch MLP. Prediction 2: logistic regression, gradient boosting, random forest.
* **D10** A missing tail number always means a cancelled flight (1,913 of 1,913), so plane features of flights with a missing or unknown tail are filled with a random real aircraft of the same airline (seed 42), with no missing flag. The ablation shows no jump (+0.012 against +0.206 for the naive fill).
* **D11** No row is removed in cleaning; problems are fixed or flagged.
* **D12** `planes.speed` (all 0) is dropped.
* **D13** One person works alone with AI agents (confirmed by the instructor).
* **D15** One shared helper file `notebooks/utils.py`.
* **D16** Airport groups are fitted on January to September only.
* **D17** No cancellation-based feature of earlier flights (the time at which a cancellation became known is not in the data).
* Intervals are bootstrap intervals that resample whole days, because flights of one day are not independent.

## Known limits
One year of data from three airports. Weather is observed, not forecast. Train and test differ strongly (late 25.7% against 14.1%; cancelled 3.18% against 0.21%). Cancellation precision is low in absolute terms and 115 of the 224 test cancellations fall on one day (18 December, cause not explained by the available data). The group structure of destination airports is weak (silhouette 0.322). Models of the same family cannot be told apart on the test part. Arrival delays are not modelled.

## How AI tools were used
Claude (Anthropic) was used as a coding and writing assistant, working with me on all eight tasks. It was used for:
* drafting the notebook code and the shared helper file `utils.py`, and the script that builds the slides;
* debugging (an out-of-memory crash in notebook 06, a tie bug in the previous-flight feature, a divide-by-zero in the bootstrap of PR-AUC);
* proposing the plan and the decisions listed above, and writing the explanations and the slide text.

What was checked (by re-running and reading the outputs, not taken on trust):
* every count of the data report against the plan and the data files (435,352 flights, 10,738 cancelled, 1,913 missing tails, ...), and the 15 metric check values, which are asserted in code in `04_metrics.ipynb`;
* each feature against the "known at T" rule: four automated leak tests (no forbidden column; 1,000 flights recomputed by a slow loop; deleting all later flights changes nothing; strict weather never later than T). One of them caught a bug that was then fixed;
* the protocol: tuning only on validation, the test part scored once in cells titled "TEST: run once", the wording of every finding (for example the early "storm week" claim was found wrong and replaced by "one day, cause not explained by the available data");
* every notebook runs top to bottom with no error, at most 5 data rows are shown, and notebook 06 gives identical numbers on a second run;
* every number on the slides has a line in the ledger below.

## Ledger: slide number, notebook, cell title
Numbers drawn directly from `data/processed/` files by `slides/build_slides.py` are marked (code).

| Slide | Number | Notebook | Cell title |
| --- | --- | --- | --- |
| 1 | 435,352 flights; Q1 to Q3 | 01 | The three business questions |
| 2 | 10,738 cancelled; 1,913 no tail; 9,371 tail not in planes; 715; 365; 73; 0 duplicates | 01 | 6. Data report |
| 2 | weather in UTC, 4 to 5 hours off | 01 | 5.3 Check that the tables join as expected |
| 3 | 13.4%, 39.9%, gap 26.5 [24.2, 28.9] | 02 | Finding 1 (and hour chart, code) |
| 3 | 27 of 273 days; 57.5% of cancellations; 21.9%; 9.8% (code) | 02 | Finding 2 |
| 3 | +14.5 points [11.1, 18.1]; 38.3% vs 23.8% (code); 1.48 | 02 | Finding 3 |
| 4 | YX 29%, 9E 27%, DL 9%; 1.0 to 1.7% (code) | 02 | Finding 4 |
| 4 | Thursday 1.5%, Sunday 4.7% (code); V 0.057 to 0.023; 8.7% | 02 | Finding 5 |
| 5 | 57 / 45 / 7 airports; 101,287 / 226,896 / 2,374 flights; 21.2%, 27.8%, 53.1%; 4.3% | 03 | 7. One row per group |
| 5 | silhouette 0.322; ARI at least 0.965 | 03 | 3. Choose the number of groups k |
| 6 | M1 79.03%, M2 13.84, M3 2.47%, M4 8.41%, M5 22.91%; monthly chart (code) | 04 | 1. The five metrics; 2. The monthly table |
| 6 | July M3 8.68%, z = 4.1; 76% and 69% | 04 | 4. Unusual months |
| 7 | 51 columns; leak tests | 05 | 9. The table of new columns; 11. Leak tests |
| 7 | 0.621, 0.618, 0.606, 0.518; 0.263, 0.251, 0.159, 0.458 | 05 | 12. Ablation |
| 8 | 330,883 / 104,469 flights; 0.1406; 0.0021; 85.9%; 0.1836 | 06 | A1; A5. The dumb answers |
| 8 | leakage list | 06 | A2. Columns that are removed |
| 8 | 14.1% vs 25.7% | 01 | 6. Data report (drift row) |
| 9 | PR-AUC and intervals, both predictions | 06 | E2 and E3. Final results tables |
| 9 | -0.0039 literal weather join | 06 | B3. Weather decisions and ablations |
| 9 | 0.0071 vs 0.0011 without week 51; 115 of 224 | 06, 07 | Results for prediction 2; 6. The finding for each card |
| 9 | morning recall 5.8%, Newark 20.5%; 39 Newark cancellations missed | 06 | D2. Where is the model wrong? |
| 9 | Alaska, American, Endeavor under-flagged | 06 | D3. Fairness check |
| 10 | 0.597; 37.4% [34.2, 40.6]; 30.5% [25.4, 35.1]; 2.7x; 11,974; 4,481; 14,685; 130 a day; 0.339 [0.301, 0.376] | 07 | 7. The two cards (card 1) |
| 10 | 14.3% to 51.7%; 51.0% evening recall; JFK 40.2% | 07 | 3. By week; 4. Where the cut-offs work |
| 10 | 0.228 vs 0.023 | 06 | D1. Which columns matter? |
| 11 | 0.137; 19.4% [0.6, 25.9]; 42.0% [1.0, 60.5]; 91x; 94 of 484; 5.3 a day; 0.120 [0.002, 0.233] | 07 | 7. The two cards (card 2) |
| 11 | top 1%: 10.2% and 47.8%; G1 25.1%, 81 cases; Oct 0%, Nov 5%, Dec 60%; 23% | 07 | 7. The two cards; 3. By week; 4 |
| 11 | 18 December: 115 of 224; 9.8% of 1,174 flights | 07 | 6. The finding for each card |
| 12 | limits: 25.7% vs 14.1%, 3.18% vs 0.21%, silhouette 0.322 | 01, 03 | Data report; 3. Choose k |
