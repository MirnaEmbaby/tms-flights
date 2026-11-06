# Hybrid deck speaker notes

The deck is 12 slides and is designed for a 15-minute presentation. Rehearse once and verify the live-status and alert-capacity answers with the agency owner before presenting.

## 1. Know before your clients do
- Say: This is a proposal for two early-warning scores, with a person responsible for every client-facing action.
- Read out: 25.7% of 330,883 training-period flights were late or cancelled. [01]
- Ask: What does the agency need to know two hours before departure?

## 2. A bad flight is a client problem first
- Say: The data represents departures from three New York airports; the agency needs warning time to check connections and prepare alternatives.
- Read out: The source contains 435,352 flights and 10,738 cancellations. [01]
- Ask: Who checks live airline status before contacting the client?

## 3. Risk builds, clusters—and is not just weather
- Say: Risk rises later in the day, cancellations are concentrated on a small number of days, and recent airport state is a stronger signal than weather in this comparison.
- Read out: The late-or-cancelled rate changes from 13.4% in the early-hour group to 39.9% in the evening-hour group. [02]
- Ask: Should the agency use a bad-day operating rule alongside individual flight scores?

## 4. Destinations have different reliability profiles
- Say: The cluster groups suggest different operational priorities, but their structure is modest and should not be treated as certainty.
- Read out: The chronic-delay group has 7 airports and a 53.1% late rate. [03]
- Ask: Which group-specific actions could staff realistically support?

## 5. The year changes the operating picture
- Say: Metrics need explicit denominators, and the large seasonal shift means a single average is not enough.
- Read out: Late-or-cancelled risk fell from 25.7% in training to 14.1% in test. [01]
- Ask: Which threshold or alert volume is operationally acceptable?

## 6. Score only with information available at decision time
- Say: At the two-hour point, scheduled and historical information is allowed; post-departure outcomes and cancellation flags are not.
- Read out: The scheduled-hour weather columns are a forecast stand-in; strict weather uses observations available by the prediction point. [05]
- Ask: Can the agency obtain a real weather forecast and a cancellation timestamp?

## 7. Tune on validation; keep the test months unseen
- Say: Settings are selected on earlier months, then the final model is tested once on the later quarter.
- Read out: The final training period has 330,883 flights; test has 104,469. [06]
- Ask: Why is accuracy not the primary measure?

## 8. Both alerts rank risk above the dumb baseline
- Say: Both rankings beat their same-period prevalence baseline, but the cancellation interval is wide because cancellations are rare.
- Read out: Test PR-AUC is 0.339 for late-or-cancelled and 0.120 for cancellation. [06]
- Caveat: These saved scores predate the D10 imputation update. Rerun notebooks 05–07 before using them as final results.

## 9. Alert 1: warn clients about a possible delay
- Say: This is a broad warning list; staff confirm status and prioritize connections rather than promising a delay.
- Read out: The saved test snapshot flags 11.5% of flights and catches 30.5% of problem flights. [07]
- Caveat: Refresh this card after the D10 downstream rerun.

## 10. Alert 2: prepare rebooking for cancellation risk
- Say: Treat the cancellation score as a queue for preparation, not a prediction of certainty; never auto-rebook.
- Read out: The saved snapshot identifies 94 of 224 cancellations. [07]
- Caveat: 115 of the 224 cancellations fell on one day, and the score snapshot needs refreshing after D10.

## 11. Keep a person in the loop—and watch drift
- Say: Seasonal drift and subgroup gaps require ongoing monitoring, and the proposed stop rules are tentative.
- Read out: The late-or-cancelled rate is 25.7% in training and 14.1% in test. [01]
- Ask: Who owns weekly review and what level of alert volume can they handle?

## 12. Approve a careful pilot
- Say: Start with human-reviewed actions, define capacity and ownership, and improve the model inputs before scaling.
- Read out: The pilot duration and daily alert capacity are business decisions, not model findings.
- Ask: Who will review flags, and what forecast or status data can the agency provide?
