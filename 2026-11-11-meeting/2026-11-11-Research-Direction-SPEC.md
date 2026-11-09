# Research Direction specification and claim register

Meeting: 11 November 2026. Standalone seven-page Beamer presentation (one unnumbered cover plus six content slides), pdfLaTeX, 16:9, approximately 7 minutes 20 seconds. Repository HEAD used: `96881bc80eff943d05056844550029e6451c9f5e`. No November 18 deck is created. No PDF concatenation, appendix, Main/Backup division or discussion index.

## Design and structure

The GreenCache source supplies the Madrid theme, Latin Modern typography, margins (0.48 cm), title geometry, rounded color boxes and palette: Ink `243748`, Muted `667B8B`, Accent `347E74`, AccentBlue `507DAD`, SoftMint `E6F4EE`, SoftLilac `F1EEF8`, Paper `FBFCFE`. The reference PDF's slide 4 was rendered and inspected. The new footer is `Research Direction | n / 6`, without inherited navigation. Diagrams and tables are editable native LaTeX/TikZ. No external images or dependencies on the GreenCache document.

| Slide | Layout and required conclusion | Evidence class | Time |
|---|---|---|---|
| 1 | Three research dimensions, primary metrics, explicit proposal status | C/D: design hypothesis and intended objective | 45 s |
| 2 | Four-row data/access/placement table; capacity does not establish energy savings | B/C: prior findings and candidate placement | 65 s |
| 3 | Two worker groups, two labeled activation arrows, resident KV/weights, costs and comparison architectures | B: A/E precedent; C/D: proposed HBM/HBF roles | 100 s |
| 4 | Three simulator roles, completed/future distinction, qualified TPOT example, integration warning | A: documented Oak simulations; D: integration | 90 s |
| 5 | Three RQs, six baselines, metrics, separate November 18 MemExplorer announcement | B: existing coverage; D: proposed experiments | 75 s |
| 6 | Final five-column comparison, 13 entries, uncertainty legend, complete matrix link | B: curated literature summary; unverified fields marked | 65 s |

A = documented experiments already performed; B = prior-work findings; C = inference/hypothesis; D = future work. These distinctions appear in the slides and speaking script. No energy, carbon, or hardware-prototype achievement is claimed.

## Source register

**N**: [2026-11-09 research record](https://app.notion.com/p/412c9399c91881fa90a4c56a96ce42d6), fetched via connected Notion. Source edit time: `2026-11-09T04:38:25.489Z`. Workspace verification state is unverified. The full requested §5.3 matrix was accessible. It is the source of truth for the condensed comparison, not evidence that every underlying paper was independently re-audited here.

**M**: [MemExplorer v2 full text](https://arxiv.org/html/2604.16007v2), 29 September 2026. Table I confirms heterogeneous compute/memory and P/D plus A/FFN coverage. §V-E and Fig. 8 discuss layer specialization. This deck does not quote improvement factors or claim an uncovered research gap. Exact limits and contribution overlap remain next week's reading task.

**J**: [Janus, arXiv:2512.13525](https://arxiv.org/abs/2512.13525), current abstract independently checked. Confirms attention/expert pools, activation scheduling and SLO-aware provisioning. [MegaScale-Infer](https://arxiv.org/abs/2504.02263) is linked as established precedent from N §6; not independently re-read in full here.

**H/S**: [HBFSim](https://github.com/FlashLabAE/HBFSim) and [ServeLoop](https://github.com/FlashLabAE/ServeLoop). HBFSim repository accessible; ServeLoop web fetch timed out. Capabilities and deployed versions on slide 4 follow N §§3–4. Oak versions documented there: HBFSim `3df0f3d6cf756535535e78c85764cf0728134be7`; ServeLoop `7d5d7a4b767d131225cd93bb6f8056f4ef67b278`. These were not checked against a live Oak checkout during this task.

## Claim-to-source mapping

| Claim / slide | Source and boundary |
|---|---|
| Role-specific HBM/HBF may improve energy under SLO (1–3) | N §§1–2, 5.3.4; explicitly a hypothesis, not a proven design |
| Active KV differs from read-mostly experts; activations cross workers (2–3) | N §§2.1–2.4; candidate placements are not universal |
| A/E already exists (3, script) | J abstract; MegaScale-Infer entry in N §6 |
| HBFSim transaction/FTL/thermal/endurance role and ServeLoop single-device scope (4) | N §3.2; H/S repositories linked for identification |
| Deployment, synthetic experiments, ratio/placement sweeps completed (4) | N §§3, 4.1–4.3, 13; reported completed work, not rerun here |
| Llama-3.1-8B, 8 requests, 256/32, 4 HBM/4 HBF; 1.261 vs 7.342 ms mean TPOT (4) | N §4.2 provides workload and rounded values; §4.3 provides three-decimal values. Both placements use the same 4/4 system. The All-HBM label is data placement, not an 8-HBM hardware configuration. This is a modeled synthetic dense-model result, not MoE or physical GPU evidence. Raw receipts were not retrieved. |
| Multi-GPU integration, calibrated full power model and large MoE energy comparison incomplete (4) | N §§3.2, 8, 13, 15 |
| Kernel profiles may contain HBM stalls; naive addition double counts (4) | N §§3.2, 8. Integration must define component boundaries and overlap semantics. Memory makespan is not an independent additive wall-clock term. |
| RQs, six baselines and fairness constraints (5) | N §§5.3.4, 9–10, 13. Explicit future experimental design. |
| MemExplorer includes HBM/HBF co-design and A/FFN (5–6) | M Table I, §V-E. No novelty claim is finalized. |
| Matrix classifications (6) | N §5.3.1–5.3.2, condensed below; no new categorical negatives inferred |

## Slide 6 condensation ledger

Five requested columns retained exactly. Thirteen representative entries fit at 7.5 pt native Beamer font, rendered approximately 23 px at 1400 px slide width. This is larger than the 6.8 pt source lines, without whole-table scaling. Mooncake and HBF Sucks? omitted to preserve readability; their full rows remain in Notion.

| Entry | Source | Condensation / uncertainty |
|---|---|---|
| Helix | N §5.3.1 | Own simulator and GPU cluster; geo-distributed simulation explicitly distinguished from hardware evaluation |
| ThunderServe | N §5.3.1 | Estimator + GPU experiments; P/D, TP/PP and KV; selected objectives shown, latency also in full matrix |
| Hetis | N §5.3.1 | vLLM prototype; independent simulator form **Needs verification**; attention-head and KV placement |
| Tessera | N §5.3.1 | GPU runtime; independent simulator form **Needs verification**; kernel placement; full matrix also lists profiling and MILP |
| GreenCache | N §5.3.1 and unchanged local GreenCache documentation | No geo-serving claim; SSD KV placement; carbon under SLO |
| Janus | N §5.3.1 plus J abstract | Runtime; independent simulator form **Needs verification**; A/E; per-GPU throughput is the compact reported objective/benefit |
| How Far Can Disaggregation Go? | N §5.3.1 | Profiles + ASTRA-Sim are use of an existing simulator; A/FFN and GPU placement |
| Carbon–SLO | N §5.3.1 | Geo queue/network simulation and request/batch routing; carbon with SLO |
| LLMServingSim 2.0 | N §5.3.2 | Simulator + profiles; TP/PP/EP. Performance/energy/fidelity marked evaluation metrics |
| HBFSim / ServeLoop | N §5.3.2 | Oak event-driven HBFSim, not the different real-GPU-profiling work with the same short name; single-device |
| MemExplorer | N §5.3.2 and M | Analytical co-design, HBM/HBF, P/D, A/FFN, Token/J/performance |
| Characterizing HBF | N §5.3.2 | Trace-driven simulator, multi-GPU KV/expert placement; time, energy, wear are evaluation metrics |
| Potential Applications of HBF | N §5.3.2 | Capacity/replication model; expert residency; TPOT and network traffic are evaluation metrics |

`Not shown` preserves the source's “not established/not seen” meaning and is not equivalent to a proven absence. `NV` expands visibly to **Needs verification**. Multiple GPUs or nodes do not establish WAN distribution. Different carbon-intensity traces do not establish geo routing. Placement is distinguished from computation partitioning; W, J and CO₂e are not interchangeable. Simulator construction and simulator use have separate wording. The table lists selected objectives, not exhaustive metrics.

## Evaluation plan detail (supporting script, not another slide)

Use the same model, input/output distribution, arrival trace and token precision. Declare the resource control for each comparison separately: equal GPU count, equal capacity, equal package, equal cost or equal power are different studies and may conflict. Count generated tokens consistently for J/token and Token/J; define goodput as completed output tokens per second from requests meeting the specified TTFT and TPOT thresholds. Report offered load, admitted fraction and violations so selective dropping cannot masquerade as an improvement. Separate compute, memory and network energy and include idle/waiting energy without re-adding components already in a board-power profile.

First establish All-HBM timing and byte invariants. Then introduce memory placement, activation traffic and network contention into a dependency graph, allowing only causally valid overlap. No fabricated hardware capacities, stack specifications or energy estimates are used in this deck.

## Build and QA

Run `python3 scripts/build_research_direction.py` from this directory (or pass its absolute path). Requires pdfLaTeX, PyMuPDF and Pillow. The script compiles twice, builds a minimal independent Overleaf ZIP, extracts it in a clean temporary directory, compiles it twice and checks text/pixel/link parity. It checks seven PDF pages with six numbered content slides, 16:9, all six footers, no inherited internal links, required final slide and next-week announcement, text bounds, and preservation of existing artifacts. It renders all pages and the montage. Visual review is recorded separately in `output/qa/research-direction-validation.md`.

## Cover revision

Added an independent unnumbered cover at user request. The original six content slides remain byte-identical in rendered appearance and keep 1/6–6/6 numbering. PDF pages 2–7 correspond to content slides 1–6. The final matrix remains last.

PDF page 2 now omits the presentation title, presenter and date; these appear only on the cover. Content-slide title remains Proposed Research Direction.

## Metric and layout revision

PDF page 2 uses three full-width horizontal rows stacked vertically: Hardware, Serving, Objective. The metric table now names Energy per output token (J/token), Energy efficiency (tokens/J), Time to first token (TTFT, ms), Time per output token (TPOT, ms/token), Goodput under SLO (tokens/s), and Operational carbon emissions per output token (gCO2e/token). Carbon is a planned metric, not an achieved result. It accounts for serving electricity multiplied by the corresponding grid carbon intensity, normalized by generated output tokens; embodied emissions are excluded. Goodput counts output tokens from requests meeting the specified SLOs per second. Geo routing remains a later phase.

## Research-goal wording revision

At user request, PDF page 2 now states the overall goal as reducing power consumption and carbon emissions across data centers through hardware co-design and coordinated serving under latency/SLO requirements. This is a research goal, not a reported result. The staged implementation and current integration status on other slides remain unchanged.

## Presentation cleanup

At user request, removed the architecture slide Compare line and all per-slide Sources footnotes. The final matrix retains a simple complete-matrix Notion link. This specification and the speaking script retain the claim/source record for reference.

Simulator slide revised at user request: only three full-width rows remain, ordered HBFSim, ServeLoop, LLMServingSim 2.0. Title changed to Simulation Frameworks. Removed completion status, modeled example, integration-plan text and double-counting warning from the slide; source and methodological history remain in this document.
