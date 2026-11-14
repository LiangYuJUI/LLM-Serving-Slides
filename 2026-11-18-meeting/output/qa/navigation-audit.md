# Navigation audit

Main is pages 1–16. Discussion index is page 17. Backup is pages 18–30.

| Backup | PDF | Primary return | Other links |
|---|---:|---|---|
| B01 | 18 | M03 | Navigation18 |
| B02 | 19 | M12 | M02, Navigation18 |
| B03 | 20 | M02 | B11, B12, M09, Navigation18 |
| B04 | 21 | M09 | Navigation18 |
| B05 | 22 | M05 | M06, Navigation18 |
| B06 | 23 | M08 | Navigation18 |
| B07 | 24 | M07 | M08, Navigation18 |
| B08 | 25 | M10 | M11, Navigation18 |
| B09 | 26 | M13 | M14, M15, Navigation18 |
| B10 | 27 | M16 | Navigation18 |
| B11 | 28 | M02 | B03, Navigation18 |
| B12 | 29 | M02 | B03, Navigation18 |
| B13 | 30 | M02 | B02, Navigation18 |

## Main keyword links

| Main | Words | Backup | Evidence checked |
|---|---|---|---|
| M02 | operational carbon | B02 | Scope 2, PUE |
| M02 | Load-dependent Latency | B11 | 1.7, 4.8, 3.4, not full geo-distributed |
| M02 | Phase-dependent Power | B12 | 95%, 72, 5.6, per-GPU |
| M02 | Lowest-CI routing | B13 | not a measured, SLO-feasible, RTT |
| M03 | Table I | B01 | SLIT, MOER, partial |
| M05 | continuous batching | B05 | not a fixed constant |
| M06 | TTFT | B05 | wait for a slot, not a fixed constant |
| M06 | TPOT | B05 | queued prefill, not a fraction |
| M07 | shared batch energy | B07 | does not power off, 0.25 |
| M08 | Greedy score | B06 | Equation (1), MOER |
| M08 | full ILP | B06 | unimodular |
| M08 | Iterative ILP | B07 | projected, successive |
| M09 | Within-node validation | B04 | 9.1, 2.5, within a node |
| M09 | formula backup | B03 | 1.7, 5.6 |
| M10 | Table II | B08 | 1200, Simulated |
| M11 | baselines | B08 | round-robin, MOER |
| M12 | SLO violation rate | B02 | either the TTFT |
| M13 | PUE and CI spread | B09 | 1.08, 0.94 |
| M14 | Polling period | B09 | 8.2, 6.5 |
| M15 | Predicted OSL | B09 | 51, GovReport |
| M16 | Limitations | B10 | Multi-turn, Our direction |
