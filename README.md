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
slides/          # tms_final.pdf and tms_final.pptx (13-slide decision pitch for the agency owner, speaker notes inside the PPTX), build_deck.py
```

## Data
Source: nycflights23 (C. Ismay, S. P. Couch, H. Wickham, "nycflights23", 2025), licence CC0. Original: https://github.com/moderndive/nycflights23 . The data files are not in this repo (`data/` is ignored).

## How to run
1. Put `flights.csv`, `weather.csv`, `planes.csv`, `airports.csv`, `airlines.csv` in `data/raw/`.
2. `pip install -r requirements.txt` (Python 3.10 or newer; CPU only).
3. Run the notebooks in `notebooks/` in order, `01_clean` to `07_decision`. Each one saves files in `data/processed/` that the next one reads, and each runs top to bottom with Kernel > Restart and Run All, e.g. `jupyter nbconvert --to notebook --execute --inplace notebooks/01_clean.ipynb`. Run time on 2 CPUs and 8 GB: 01 to 05 about 3 minutes in total, 06 about 65 minutes, 07 about 15 seconds.
4. Slides (optional): `python slides/build_deck.py` rebuilds `slides/tms_final.pptx` and `slides/tms_final.pdf`. It needs `python-pptx` and `pillow` (`pip install python-pptx pillow`, not in requirements.txt) and LibreOffice for the PDF. The numbers on the slides are written in the script from the printed outputs of notebooks 01 to 07; the ledger below maps each one to its notebook.

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
Claude (Anthropic) and Gemini (Google) were used as an assistant, working with me on some tasks. It was used for:
* debugging (an out-of-memory crash in notebook 06, a tie bug in the previous-flight feature, a divide-by-zero in the bootstrap of PR-AUC);
* proposing the plan and the decisions listed above, suggesting the slide structure and text, and reviewing the slides against the plan.
* writing the README.md file for this project.

What was checked (by re-running and reading the outputs, not taken on trust):
* every count of the data report against the plan and the data files (435,352 flights, 10,738 cancelled, 1,913 missing tails, ...), and the 15 metric check values, which are asserted in code in `04_metrics.ipynb`;
* each feature against the "known at T" rule: four automated leak tests (no forbidden column; 1,000 flights recomputed by a slow loop; deleting all later flights changes nothing; strict weather never later than T). One of them caught a bug that was then fixed;
* the protocol: tuning only on validation, the test part scored once in cells titled "TEST: run once", the wording of every finding (for example the early "storm week" claim was found wrong and replaced by "one day, cause not explained by the available data");
* every notebook runs top to bottom with no error, at most 5 data rows are shown, and notebook 06 gives identical numbers on a second run;
* every number on the slides was compared with the notebook outputs and has a line in the ledger below.

## Ledger: slide number, notebook, cell title
The deck is written for the agency owner (a decision pitch), so technical details stay in the notebooks. Cell titles marked (?) were not re-checked against the notebook after the deck was rebuilt: open the notebook and confirm the title.

| Slide | Number | Notebook | Cell title |
| --- | --- | --- | --- |
| 1 | 25.7% late or cancelled, 330,883 training flights; 435,352 flights | 01 | 6. Data report (drift row) |
| 1, 13 | two alerts tested on Oct-Dec; about 130 messages and 5 flights a day | 07 | 7. The two cards |
| 2 | 435,352 flights, 1,913 flights without a tail, all cancelled | 01 | 6. Data report |
| 2 | UTC join: -0.0039; plane fill +0.012 vs +0.206 | 06; 05 | weather rows (?); ablation (?) |
| 3 | monthly late-or-cancelled bars; 79.03%, 13.84 min, 2.47%, 8.41%, 22.91% | 04 | 1. The five metrics; 2. The monthly table |
| 3 | June and July not wetter or foggier; cause not explained | 04 | unusual months (?) |
| 4 | 13.4%, 39.9%, 26.5 points [24.2, 28.9]; 11.5 to 36.3; 11.4 to 43.4 | 02 | Finding 1 |
| 4 | 27 of 273 days; 9.8%, 21.9%, 57.5%; 10.0% (max 27.1%); 21% of rainy days | 02 | Finding 2 |
| 4 | 0.228, 0.059, 0.032, 0.027, 0.023 | 06 | D1. Which columns matter? |
| 4 | rain +14.5 points [11.1, 18.1] | 02 | Finding 3 |
| 5 | B6 1.26, F9 1.25, WN 1.21, YX 0.76, G4 0.54; YX 29%, 9E 27%, Delta 9%; 1.0% to 1.7% | 02 | Finding 4 |
| 5 | Thursday 1.5%, Sunday 4.7%; 0.057 to 0.023; 8.7% | 02 | Finding 5 |
| 6 | 57 / 45 / 7 airports; 101,287 / 226,896 / 2,374 flights; 21.2%, 27.8%, 53.1%; 4.3%; 15% to 42%; 41.5 min; silhouette 0.322 | 03 | 7. One row per group; 3. Choose k |
| 7 | four leak tests | 05 | 11. Leak tests |
| 7 | 222,402 / 108,481 / 104,469 / 330,883 flights; 85.9%; 0.1406; 0.0021 | 06 | A1; A3 (?) |
| 8 | PR-AUC with intervals of every model, both predictions | 06 | E2 and E3. Final results tables |
| 8 | strict -0.0016; literal -0.0039; without airport state -0.058 | 06 | weather rows and ablation rows (?) |
| 8 | 224 cancellations, 115 on one day | 07 | 6. The finding for each card |
| 9 | cut-off 0.597; 130 a day; 11,974; 37.4% [34.2, 40.6]; 30.5% [25.4, 35.1]; 2.7x; 14.1%; 0.339 [0.301, 0.376] | 07; 06 | 7. The two cards (card 1); E2 |
| 9 | 14.3% to 51.7% (weeks with 100+ cases); stop rule 14% | 07 | 3. The same cut-offs by week; 7. The two cards (line 9) |
| 9 | mornings 5.8%; Newark 20.5% | 06 | D2. Where is the model wrong? |
| 10 | cut-off 0.137; 5.3 a day; 484; 94 of 224; 19.4% [0.6, 25.9]; 42% [1.0, 60.5]; 91x; 0.120 [0.002, 0.233]; top 1%: 47.8% | 07; 06 | 7. The two cards (card 2); E3 |
| 10 | 39 Newark cancellations missed; 115 of 224 on 18 December; 23% stop rule, 46.7% | 06; 07 | D2. Where is the model wrong?; 6. The finding for each card; 3. The same cut-offs by week |
| 11 | Alaska, American, Endeavor under-flagged; JetBlue most | 06 | D3. Fairness check |
| 11 | 25.7% to 14.1%; strict weather -0.0016 | 01; 06 | 6. Data report; weather rows (?) |
| 12 | 15 metric check values; four leak tests | 04, 05 | 1. The five metrics; 11. Leak tests |
