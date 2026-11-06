# Hybrid deck speaker notes

The deck is 12 slides and is designed for a 15-minute presentation (about 70–75 seconds per slide). Rehearse once and verify the live-status and alert-capacity answers with the agency owner before presenting.

## 1. Know before your clients do
- Say: This is an early-warning system providing two calibrated risk scores two hours before departure, with a human in the loop for every single action.
- Read out: 25.7% of 330,883 training-period flights were late or cancelled; 435,352 flights across 2023. [01]
- Ask: What does the travel agency need to know two hours before scheduled departure?

## 2. A bad flight is a client problem first
- Say: Departing from New York's three major hubs (JFK, LGA, EWR), delays build up and leave passengers stranded. Early notice gives staff time to check tight connections and prepare rebooking options.
- Read out: 10,738 cancellations across the year; every cancellation requires operational intervention. [01]
- Ask: Who on the agency team checks live airline feeds before contacting the passenger?

## 3. Risk builds, clusters—and is not just weather
- Say: Flight delay risk rises sharply through the day as delays compound across aircraft turns; cancellations cluster into extreme burst days; and live airport state at T-2h is 10 times more informative than weather alone.
- Read out: Late-or-cancelled rate climbs from 13.4% in the early wave (05–08h) to 39.9% in the evening (19–22h), a 26.5 pp jump (p < 0.001). [02]
- Ask: Should the agency enforce a specialized bad-day protocol alongside individual flight alerts?

## 4. Destinations have different reliability profiles
- Say: Destination clustering (Jan–Sep fit) reveals three distinct operational groups, though the modest silhouette (0.322) means we treat them as practical guidelines rather than absolute truth.
- Read out: Chronic delay group has 7 airports and a 53.1% late rate; short-haul has 57 airports with a 4.3% cancellation rate. [03]
- Ask: Can agency staff realistically support group-specific actions like early evening connection checks?

## 5. The year changes the operating picture
- Say: All five reliability metrics (M1 to M5) are defined with explicit denominators; dramatic seasonal drift from summer storms to calm autumn means a single annual average is misleading.
- Read out: Late-or-cancelled risk dropped from 25.7% in Jan–Sep train to 14.1% in Oct–Dec test; full-year on-time rate was 79.03%. [01, 04]
- Ask: How should the agency adjust alert thresholds when moving between high-delay summer and quiet autumn?

## 6. Score only with information available at decision time
- Say: The decision point is strictly T − 2 hours. Post-takeoff information is forbidden; missing tail numbers cannot be used as cancellation signals (D10); and 4 automated tests verify zero leakage.
- Read out: Scheduled-hour weather serves as a forecast stand-in; strict weather is tested as a robust sensitivity check. [05]
- Ask: When live forecast feeds and real-time cancellation timestamps become available, how easily can they plug in?

## 7. Tune on validation; keep the test months unseen
- Say: True out-of-sample discipline: train on Jan–Jun (222k flights), tune hyperparameters on Jul–Sep (108k flights), refit on Jan–Sep, and evaluate once on held-out Oct–Dec (104k flights).
- Read out: Accuracy is rejected because a dumb "nobody is late" rule achieves 85.9% accuracy while catching zero late flights. [06]
- Ask: Why is PR-AUC the only scientifically honest comparison metric for imbalanced flight risks?

## 8. Both alerts rank risk above the dumb baseline
- Say: Both models deliver real predictive skill, significantly outperforming their same-period prevalence dumb baselines in paired resampling tests (p < 0.001).
- Read out: Test PR-AUC is 0.339 for late-or-cancelled (2.4× dumb baseline 0.141) and 0.120 for cancellations (prevalence 0.0021). [06]
- Takeaway: The cancellation interval is wide because Oct–Dec had only 224 total cancellations, so it is used strictly for queue prioritization.

## 9. Alert 1: warn clients about a possible delay
- Say: Alert 1 creates a focused shortlist of likely delayed flights; staff verify the airline departure board and prioritize tight connections rather than promising a delay.
- Read out: Flags 11.5% of test flights (~130/day), achieving 37.4% precision and catching 30.5% of problem flights (4,481 cases; 2.7× lift over random). [07]
- Operational note: Mornings are an inherent blind spot (5.8% recall vs 51% in evening) because the airport has not yet accumulated delays.

## 10. Alert 2: prepare rebooking for cancellation risk
- Say: Alert 2 flags flights at high risk of cancellation to prepare rebooking alternatives before seats sell out; it is never used for automated rebooking.
- Read out: Flags ~5.3 flights per day (484 total), identifying 94 of the 224 test cancellations (42.0% recall, 19.4% precision, 91× lift over random). [07]
- Key nuance: 115 of the 224 test cancellations occurred on a single day (18 December; 121 in ISO Week 51); staff should scale up capacity during storm clusters.

## 11. Keep a person in the loop—and watch drift
- Say: Operational success requires active drift monitoring; we establish concrete floor rules to alert the team if model skill degrades.
- Read out: Retrain or audit Alert 1 if weekly recall drops below 14% for two consecutive weeks; check Alert 2 in 4-week blocks if recall drops below 23%. [07]
- Ask: Who on the team owns the weekly drift review?

## 12. Responsible AI, verified methods—and a careful pilot
- Say: Every rule, count, and leak guardrail was independently audited (Golden Rule #6); AI assisted with coding and layouts, while all figures and assertions were verified in code.
- Read out: We recommend approving a controlled pilot with ~130 delay alerts and ~5 cancellation preparations daily under strict human review.
- The Ask: Agree on the operational daily alert capacity and designate the review owner to launch the pilot. [01–07, README]
