# Research and engineering evidence: Fraud Risk Intelligence

This is a starting bibliography and evaluation checklist, **not a completed systematic literature review**.

## Research questions
1. What real stakeholder decision is improved by this system, and how can its value be measured?
2. What is the unit of observation, prediction or retrieval?
3. What information exists at decision time versus after the fact?
4. Which published baselines and error metrics fit that task?
5. What dataset shift, missingness, sampling bias and ethical risks invalidate naive results?

## Candidate source
PaySim synthetic mobile money (subject to access/license), with deterministic synthetic fallback.

## Experiments to register
- Dataset snapshot and checksum
- Split strategy, rationale and leakage review
- Baseline configuration and metrics
- Candidate configuration and fair comparison
- Error slices, failure cases, and uncertainty
- Runtime/compute cost measurements

## Decisions still awaiting evidence
Define predict-before-authorization contract; audit post-event balance leakage; baseline, validation, calibration, service.

**Do not claim paper-backed superiority until a primary source has been checked and a reproducible experiment supports it.**
