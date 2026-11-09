# Backup navigation audit

Generated from LaTeX frames and verified PDF link annotations.

| Backup | PDF | Primary main | Back to Main | Discussion Index | Cross-links |
|---|---|---|---|---|---|
| B00 | 21 | M02 | Yes | Yes | B02, B03 |
| B01 | 22 | M03 | Yes | Yes | B02 |
| B02 | 23 | M02 | Yes | Yes | B00, B03 |
| B03 | 24 | M02 | Yes | Yes | B00, B04 |
| B04 | 25 | M02 | Yes | Yes | B05 |
| B05 | 26 | M03 | Yes | Yes | B06 |
| B06 | 27 | M04 | Yes | Yes | B07, M02 |
| B07 | 28 | M04 | Yes | Yes | B08, M02, M07 |
| B08 | 29 | M03 | Yes | Yes | B09 |
| B09 | 30 | M05 | Yes | Yes | B10, M08, M18 |
| B10 | 31 | M07 | Yes | Yes | B11, B18, M06, M08 |
| B11 | 32 | M08 | Yes | Yes | B12, M06, M14 |
| B12 | 33 | M05 | Yes | Yes | B13, M07 |
| B13 | 34 | M10 | Yes | Yes | M09, M11, M12 |
| B14 | 35 | M13 | Yes | Yes | B15, M14 |
| B15 | 36 | M15 | Yes | Yes | B16 |
| B16 | 37 | M16 | Yes | Yes | B17 |
| B17 | 38 | M17 | Yes | Yes | B18 |
| B18 | 39 | M06 | Yes | Yes | B19 |
| B19 | 40 | M06 | Yes | Yes | B20 |
| B20 | 41 | M06 | Yes | Yes | B21 |
| B21 | 42 | M19 | Yes | Yes | B22 |
| B22 | 43 | M19 | Yes | Yes | B23 |
| B23 | 44 | M19 | Yes | Yes |  |
| B24 | 45 | M07 | Yes | Yes | M08 |
| B25 | 46 | M11 | Yes | Yes | B27, M09, M10, M12 |
| B27 | 47 | M12 | Yes | Yes | B25, B26, M11, M14 |
| B26 | 48 | M12 | Yes | Yes | B27, M09, M10, M11 |

## Main Source → Backup → Primary Return → Other Return Links

Every row is a visible PDF entry (including repeated destinations). All have a visible return to the source Main. Main question comes from the unchanged frame title. Direct means a matching supplement, not necessarily the same experiment. Background entries are explicitly scoped. No unresolved semantic mismatch.

| Main source / research question | Visible entry | Backup | Supplement / evidence | Alignment | Primary return | Other Main returns | Visible source return |
|---|---|---|---|---|---|---|---|
| M02: Why Do We Need GreenCache? | KV Reuse | B00 | KV reuse and prefill/load latency example; not end-to-end speedup. | direct | M02 | - | Yes |
| M02: Why Do We Need GreenCache? | Table 1 | B06 | Table 1 hardware embodied carbon and allocation accounting. | direct | M04 | M02 | Yes |
| M02: Why Do We Need GreenCache? | Equations | B07 | Operational and amortized embodied carbon, Equations (1)-(5). | direct | M04 | M02, M07 | Yes |
| M03: Why Is a Fixed Cache Size Suboptimal? | Grid CI | B01 | Grid carbon-intensity differences and temporal variation. | direct | M03 | - | Yes |
| M03: Why Is a Fixed Cache Size Suboptimal? | Adapt Illustration | B08 | Conceptual load/CI capacity illustration, not measured ablation. | direct | M03 | - | Yes |
| M04: What Does GreenCache Optimize? | Embodied Carbon | B06 | Table 1 hardware embodied carbon and allocation accounting. | direct | M04 | M02 | Yes |
| M04: What Does GreenCache Optimize? | Carbon Model | B07 | Operational and amortized embodied carbon, Equations (1)-(5). | direct | M04 | M02, M07 | Yes |
| M05: How Does GreenCache Work? (1/2): Monitoring \& Prediction | Profiles | B09 | Figure 11 request-rate/capacity profiling heatmaps and feasibility background. | direct | M05 | M08, M18 | Yes |
| M05: How Does GreenCache Work? (1/2): Monitoring \& Prediction | Predictors | B12 | Load and CI predictors supplying solver inputs; not all profiling/feedback details. | direct | M05 | M07 | Yes |
| M06: How Does GreenCache Work? (2/2): Optimization \& Execution | Full ILP | B10 | Full Equation (6), decision variables and carbon objective. | direct | M07 | M06, M08 | Yes |
| M06: How Does GreenCache Work? (2/2): Optimization \& Execution | SLO Numbers | B11 | Separate TTFT/TPOT attainment and numeric thresholds; paper discrepancy retained. | direct | M08 | M06, M14 | Yes |
| M06: How Does GreenCache Work? (2/2): Optimization \& Execution | Solver Time | B18 | Controller solve time per resize, not token-path latency. | direct | M06 | - | Yes |
| M06: How Does GreenCache Work? (2/2): Optimization \& Execution | Resize Interval | B20 | Resize-interval sensitivity relative to the hourly default. | direct | M06 | - | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | 1. Decision Variable — S | B10 | Full Equation (6), decision variables and carbon objective. | direct | M07 | M06, M08 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | 2. Candidate Set — S | B24 | Discrete capacity domain, configured maxima and hourly/profile assumptions. | direct | M07 | M08 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | 3. Operational Carbon | B07 | Operational and amortized embodied carbon, Equations (1)-(5). | direct | M04 | M02, M07 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | 4. Embodied Carbon | B10 | Full Equation (6), decision variables and carbon objective. | direct | M07 | M06, M08 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | 5. Model Inputs | B12 | Load and CI predictors supplying solver inputs; not all profiling/feedback details. | background | M05 | M07 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | Variables | B10 | Full Equation (6), decision variables and carbon objective. | direct | M07 | M06, M08 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | Carbon | B07 | Operational and amortized embodied carbon, Equations (1)-(5). | direct | M04 | M02, M07 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | Inputs | B12 | Load and CI predictors supplying solver inputs; not all profiling/feedback details. | background | M05 | M07 | Yes |
| M07: How Does the Solver Decide? (1/2): Variables \& Inputs | Candidates | B24 | Discrete capacity domain, configured maxima and hourly/profile assumptions. | direct | M07 | M08 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | 1. TTFT Attainment | B11 | Separate TTFT/TPOT attainment and numeric thresholds; paper discrepancy retained. | direct | M08 | M06, M14 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | 2. TPOT Attainment | B11 | Separate TTFT/TPOT attainment and numeric thresholds; paper discrepancy retained. | direct | M08 | M06, M14 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | 3. Feasible Cache Sizes | B24 | Discrete capacity domain, configured maxima and hourly/profile assumptions. | direct | M07 | M08 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | 4. Decision Interval | B24 | Discrete capacity domain, configured maxima and hourly/profile assumptions. | direct | M07 | M08 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | 5. Profile-Based Feasibility | B09 | Figure 11 request-rate/capacity profiling heatmaps and feasibility background. | background | M05 | M08, M18 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | SLO Constraints | B11 | Separate TTFT/TPOT attainment and numeric thresholds; paper discrepancy retained. | direct | M08 | M06, M14 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | Assumptions | B24 | Discrete capacity domain, configured maxima and hourly/profile assumptions. | direct | M07 | M08 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | Full ILP | B10 | Full Equation (6), decision variables and carbon objective. | direct | M07 | M06, M08 | Yes |
| M08: How Does the Solver Decide? (2/2): Constraints | Profiles | B09 | Figure 11 request-rate/capacity profiling heatmaps and feasibility background. | background | M05 | M08, M18 | Yes |
| M09: How Does LCS Rank KV Cache Entries? | Multi-turn Example | B13 | Hypothetical task-specific Eq. (8) arithmetic; not an Eq. (7) experiment. | direct | M10 | M09, M11, M12 | Yes |
| M09: How Does LCS Rank KV Cache Entries? | Document QA Example | B25 | Hypothetical task-specific Eq. (9) scoring; not workload-generation evidence. | direct | M11 | M09, M10, M12 | Yes |
| M10: How Does LCS Work for Multi-Turn Conversations? | Worked Example (Eq. 8) | B13 | Hypothetical task-specific Eq. (8) arithmetic; not an Eq. (7) experiment. | direct | M10 | M09, M11, M12 | Yes |
| M11: How Does LCS Work for Document QA? | Worked Example (Eq. 9) | B25 | Hypothetical task-specific Eq. (9) scoring; not workload-generation evidence. | direct | M11 | M09, M10, M12 | Yes |
| M11: How Does LCS Work for Document QA? | TriviaQA Workload / Zipf α | B27 | TriviaQA Zipf skew, arrivals, warm-up and distinction from LCS scoring. | direct | M12 | M11, M14 | Yes |
| M12: Why Use LCS Instead of FIFO or LRU? | TriviaQA, α = 0.7; | B27 | TriviaQA Zipf skew, arrivals, warm-up and distinction from LCS scoring. | direct | M12 | M11, M14 | Yes |
| M12: Why Use LCS Instead of FIFO or LRU? | Full Table 3 | B26 | Complete 45-value Table 3 token-hit-rate comparison; not carbon reduction. | direct | M12 | M09, M10, M11 | Yes |
| M13: Real Prototype or Simulator? | Measurement Notes | B14 | Prototype measurement and trace methodology. | direct | M13 | M14 | Yes |
| M14: How Is GreenCache Evaluated? | TriviaQA | B27 | TriviaQA Zipf skew, arrivals, warm-up and distinction from LCS scoring. | direct | M12 | M11, M14 | Yes |
| M14: How Is GreenCache Evaluated? | SLO Thresholds | B11 | Separate TTFT/TPOT attainment and numeric thresholds; paper discrepancy retained. | direct | M08 | M06, M14 | Yes |
| M15: Q1: Does GreenCache Reduce Carbon? | Llama-3 8B | B15 | Llama-3 8B carbon results, with different hardware/configuration. | direct | M15 | - | Yes |
| M16: Q2: Does GreenCache Still Meet SLOs? | 8B Timelines | B16 | Llama-3 8B TTFT/TPOT time series and threshold discrepancy. | direct | M16 | - | Yes |
| M17: Q3: Does Capacity Track Load and CI? | Document Timeline | B17 | Document-QA carbon/capacity timeline, complementing multi-turn. | direct | M17 | - | Yes |
| M18: Q4: Does Adaptive Sizing Help? | Capacity Profiling (Background) | B09 | Figure 11 request-rate/capacity profiling heatmaps and feasibility background. | background | M05 | M08, M18 | Yes |
| M19: Conclusion | Limits / Our Future Work | B23 | Paper limitations and explicitly our cross-region/HBM-HBF future work. | direct | M19 | - | Yes |

Entries: 46; distinct Main/Backup pairs: 36; internal PDF links: 280; broken links: 0.

No direct Main entry (reachable via Index and Backup navigation): B02, B03, B04, B05, B19, B21, B22.

M09 examples instantiate task-specific Eq. (8)/(9), not standalone Eq. (7) experiments. M18 → B09 is Figure 11 profiling background; Figure 15 ablation stays on M18. B25 is scoring; B27 is workload generation. B23 explicitly separates our future work from GreenCache results.

Contracts: `scripts/navigation-contracts.json`. The validator checks exact entry text inside compiled PDF annotations, destination labels/pages, target evidence, numbered visible returns, and non-overlapping click rectangles. Semantic interpretation remains a human-reviewed contract, not an automatic proof of scientific meaning.
