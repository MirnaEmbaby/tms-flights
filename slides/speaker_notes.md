# Speaker notes

These notes follow the 12-page deck in `tms_final.pdf`. Allow about 60-75 seconds per slide; rehearse and time the full talk before presenting.

## 1. Warn clients before a flight goes wrong
- Say: The proposal is to use two risk scores to give clients advance notice and prepare rebooking, while a person remains responsible for every action.
- Read out: 25.7% of 330,883 January-September flights were late or cancelled.
- Likely question: Why warn two hours before departure?

## 2. The problem is big and uneven
- Say: The annual average hides large differences by month, so the agency needs ongoing monitoring rather than a single yearly estimate.
- Read out: 22.9% of 435,352 flights were late or cancelled during 2023.
- Likely question: How is “late” defined, and what is the denominator?

## 3. Three useful findings
- Say: Risk builds through the day, clusters on a few bad days, and recent airport conditions are more informative than weather alone.
- Read out: The late-or-cancelled rate rose from 13.4% in the early-hour group to 39.9% in the evening-hour group.
- Likely question: Does that difference reflect the hour itself or delays accumulating through the day?

## 4. Target actions where risk is concentrated
- Say: Airport destination groups have different reliability profiles, so operational responses can be tailored instead of treating every route alike.
- Read out: The chronic-delay group contains 7 airports and 2,374 flights.
- Likely question: How were the airport groups created, and were test months used?

## 5. A human-in-the-loop process
- Say: The system scores flights at the two-hour point; staff verify airline status and prioritize clients before taking action.
- Read out: The threshold is chosen on July-September validation data, then carried unchanged into the October-December test.
- Likely question: Does the system rebook clients automatically?

## 6. The alerts beat a random shortlist
- Say: On the held-out quarter, both alerts prioritize problem flights better than selecting the same number at random, though seasonal drift matters.
- Read out: Alert 1 found 2.7 times as many problem flights as a random shortlist of the same size.
- Likely question: Why is cancellation precision still low?

## 7. Alert 1: delays or cancellations
- Say: This alert is a broad warning list; it catches a useful share of problems but requires staff to verify and manage false alarms.
- Read out: It flags about 130 flights per day on average in the test quarter.
- Likely question: What share of flagged flights were actually late or cancelled?

## 8. Alert 2: cancellation readiness
- Say: Treat the cancellation score as a way to prioritize rebooking preparation, not as certainty that a flight will be cancelled.
- Read out: It flags about 5.3 flights per day and identified 94 of the 224 test cancellations.
- Likely question: Why offer this alert if most flagged flights are not cancelled?

## 9. Limits and known failure areas
- Say: The models are weakest in some groups and on the early-morning flights; the unusual December cancellation day is unexplained by the available data.
- Read out: The test late-or-cancelled rate was 14.1%, compared with 25.7% in training.
- Likely question: How would the model be monitored for seasonal drift?

## 10. Weekly monitoring and stop rules
- Say: A named owner should review weekly performance and pause or investigate an alert when its measured recall falls below the stated rule.
- Read out: Alert 1’s weekly recall ranged from 14.3% to 51.7% in the test quarter.
- Likely question: Why use a two-week trigger for Alert 1 and four-week blocks for Alert 2?

## 11. AI use and verification
- Say: AI assisted with drafting and debugging, while the data counts, model protocol, leakage checks, and slide figures were checked against project outputs.
- Read out: Four automated leakage checks are described in the project notebooks.
- Likely question: Which check caught a bug, and what changed afterward?

## 12. The requested decision
- Say: Approve the two alerts only as human-reviewed workflows, assign weekly monitoring ownership, and improve the inputs before expanding use.
- Read out: The proposal is about 130 Alert 1 messages and about 5 Alert 2 cases per day on average.
- Likely question: What additional data would most improve the system?
