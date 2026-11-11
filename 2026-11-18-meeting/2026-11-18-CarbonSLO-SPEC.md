# 2026-11-18 Carbon–SLO Paper Meeting — Production SPEC

> Status: **P0 / SPEC CREATED**. The next Codex run must perform **P1 only (paper audit + slide blueprint)** and STOP for human review. Do not build the complete deck in one run.
>
> Meeting: Wednesday, 2026-11-18. Target: **15–20 min main presentation**, professor Q&A via linked Backup. Language: English slide text; Traditional Chinese narrative speaker script.
>
> Primary paper: **Dissecting the Carbon–SLO Tension in Geo-Distributed LLM Serving** (Topcu et al., arXiv:2610.14571, 2026).
> This **replaces** the earlier tentative 11/18 MemExplorer talk. Do not silently make a MemExplorer presentation or delete the paper PDF.

## 0. Repository baseline and sources

Baseline inspected on 2026-11-11 (UTC+8): `main` commit `e1819641235c86c8c1098d3be4e916198b5ed9ef`, message “Add CarbonSLO geo-distributed LLM serving meeting deck,” committed 2026-11-11 07:20:34 UTC. The 11/18 folder already exists and contains the following PDF:

- **Authoritative local paper**: `2026-11-18-meeting/CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf`. Preserve it; read this exact local PDF before confirming page and figure references. Do not overwrite it.
- Public article/metadata: https://arxiv.org/abs/2610.14571
- **Authors' simulator, source data and figure reproduction**: https://github.com/topcuburak/carbon-slo-at-geoscale
- **This week's visual/story reference**: `2026-11-11-meeting/2026-11-11-GreenCache.tex`, `2026-11-11-meeting/README.md`, PDF `2026-11-11-meeting/output/pdf/2026-11-11-GreenCache.pdf`.
- GreenCache reference format: 19 Main + 29 Discussion/Backup; ~15–20 min main; English question-led slides, standalone Main and navigable Backup, concept-specific clickable links, Traditional Chinese script. **Reuse the design and navigation principles, not the GreenCache content/page count verbatim.**

Source priority for scientific claims: local primary PDF > original authors' figure/configuration data > arXiv metadata > secondary summaries. If PDF and code/README disagree, record the conflict instead of silently choosing. Do not assume an HTML figure's page number equals the PDF page. Any additional related work belongs in Backup and must be explicitly attributed.

## 1. Research narrative (professor-oriented)

**One-sentence takeaway:** Carbon-aware routing across geo-distributed datacenters must model **load-dependent LLM serving latency and energy** (continuous batching, engine queueing, prefill/decode, inter-region transfer), or carbon savings may come at the expense of SLO violations.

Present in this order: (1) what this paper does, (2) why the problem matters and what prior methods omit, (3) how the system and algorithms work, (4) what each experiment is designed to prove and what it actually shows, (5) conclusion / limitations / our research implications. Avoid a section-by-section retelling of the entire paper.

The simulator is a **new paper-specific geo-distributed serving simulator calibrated against real hardware/vLLM measurements**, not a proof of a real 16-DC production deployment. The authors publish code/data. The local physical reference is GPU measurement/calibration; geo routing, WAN/queues and scheduling comparison are simulation. Give this distinction a dedicated Main slide because the professor has repeatedly asked whether evaluation uses a prototype, existing simulator, or newly developed simulator.

Explain the difference from GreenCache:
- GreenCache: primarily SSD KV/prefix cache sizing, embodied plus operational carbon, with an LMCache/vLLM-based real prototype and replay/modeling.
- Carbon–SLO: **request/batch routing among datacenters**, operational carbon, SLO-aware scheduling, calibrated geo-distributed simulator; **not** SSD embodied-carbon optimization.
- Moving requests across regions is **not** migrating every model layer, activation, KV shard, or MoE expert across a WAN. Do not conflate geo request routing with cross-DC tensor/pipeline/Attention–Expert partitioning.

## 2. Verified technical anchors and required caveats

The following anchors are supported by paper abstract and/or the authors' public repository README. **P1 must attach exact PDF pages, sections, figures, and any additional qualifications before they can appear in slides.**

| Topic | Preliminary anchor | Presentation rule |
|---|---|---|
| What is optimized | Operational carbon subject to TTFT/TPOT SLO tradeoffs | Do not claim the method measures or minimizes hardware embodied carbon. |
| SLO metric | Violation fraction: requests exceeding **either** TTFT or TPOT budget | Avoid claiming an average violation of 3% means every request or every experiment has 97% attainment. |
| Algorithms | Greedy; standard ILP; iterative ILP; facility MILP | Standard ILP treats destination load as fixed during a batch; iterative ILP updates load projection; facility MILP models shared batch cost and marginal request cost. |
| Headline | Facility MILP up to **60% less carbon versus round-robin**, **average 3% SLO violation** | Qualify baseline, scope, and average vs maximum. Do not imply 60% is average, zero-violation, or versus all baselines. |
| Cautionary result | Carbon-aggressive Greedy can have **up to 55% SLO violations** at comparable carbon saving | Specify it is the aggressive setting / maximum reported case, not all Greedy settings. |
| Simulator architecture | Regional schedulers + DC/node/inference-engine simulation; queueing, continuous batching, KV admission, chunked prefill, per-step timing/energy | Clearly distinguish synthetic/trace-based requests, measured calibration, analytical model, simulated event/timeline. |
| Calibration and validation | vLLM v0.6.3 measurements on A100-40GB; fitted latency/power coefficients; within-node validation | Authors' repo does not include raw profiling logs; calibrated models and aggregated validation are available. Do not claim end-to-end geo hardware validation. |
| Geo topology | Baseline: 4 regional schedulers, 4 DCs each = **16 DCs**; 4 nodes/DC; 8 × A100-40GB GPUs/node | This is the simulated deployment, not 16 physically measured datacenters. |
| Geo input | Hourly region/zone CI, measured/cloud inter-region RTT, configurable PUE; authors' repo documents a 2021–2024 Electricity Maps data range | CI and RTT are inputs; do not claim real-time carbon telemetry or measured production WAN runs. |
| Models | Llama-3.1-8B, Qwen2.5-7B, Mixtral-8x7B; Mixtral is MoE | These share an A100-based simulator platform; do not infer heterogeneous GPU types or A/E disaggregation. |
| Workloads | Poisson arrivals; prompt/output length traces; oracle output lengths except sensitivity to predicted lengths | Carefully distinguish prompt text from request metadata; the released traces contain token lengths, not raw prompts. |
| Scheduling update | Authors' repo: provisioner polls DC load; batch window 100 ms / at most 300 requests; MILP solve-time cap 0.25 s; load-poll sensitivity | Verify conditions in paper Table II; do not present overhead as GPU inference latency. |
| Study scope | Load intensity, carbon-intensity spread, PUE, network topology, update cadence, OSL prediction, prompt lengths | Keep causal interpretation within the study; distinguish correlation/empirical result from a theoretical guarantee. |
| Limitations | Paper future work: multi-turn session KV locality; heterogeneous inference/deployments | Link to our HBM/HBF + heterogeneous serving work as a **proposed research direction**, not a contribution of this paper. |

Additional guardrails: TTFT != TPOT; p50/p90/p99 TTFT != SLO violation rate; gCO2 != gCO2e if the primary paper uses a specific unit; operational CO2 includes modeled host/idle/PUE where configured, but avoid inventing a manufacturing term. Facility MILP's shared energy cost is not synonymous with physically powering down datacenters. Report RTT direction/definition accurately (authors' README says forwarded request pays one RTT). Keep fallback routing rules accurate. Never cite a secondary page instead of the primary PDF when an exact result is available there.

## 3. Proposed Main deck: ~17 slides, ~16–18 min (subject to P1 page audit)

This is a **draft content budget**, not permission to start writing LaTeX during P1. Use short question-style titles, one takeaway per slide, one primary original figure/diagram at most when possible. The P1 outline may propose +/- one slide with a written reason.

| Main | Suggested question / content | Evidence priority | Approx. time |
|---|---|---|---|
| M01 | Cover: paper title, authors, date, affiliation as appropriate | Paper title | 10 s |
| M02 | **What does this paper actually contribute?** — problem, simulator, four scheduler types, key evidence | Abstract + conclusion | 50 s |
| M03 | **Why not just route to the greenest DC?** — CI, WAN, queueing, batching, SLO tension | Intro/motivation | 55 s |
| M04 | **What do existing geo schedulers miss?** — load-dependent TTFT/TPOT, phase-aware energy, KV admission, latency realism | Related work / gap | 55 s |
| M05 | **What is the carbon–SLO decision?** — request, DC, latency budget, operational-carbon boundary | Problem formulation | 60 s |
| M06 | **How does the geo serving simulator work?** — provisioner, scheduler, inter-region routing, engine queue / batch | Simulator overview | 80 s |
| M07 | **Real GPUs, a previous simulator, or a new simulator?** — measured A100/vLLM profiles vs analytical calibration vs simulated 16-DC evaluation; validation | Simulator + validation subsection | 75 s |
| M08 | **How do Greedy and standard ILP route requests?** — objective, per-request vs joint batch assignment and load estimate | Scheduler method | 70 s |
| M09 | **Why iterative ILP and facility MILP?** — load coupling, collective batch energy, tradeoffs / constraints | Scheduler method | 75 s |
| M10 | **What state does the scheduler know at decision time?** — DC state polling, active batch/queue, batch window, fallback | Scheduler workflow | 60 s |
| M11 | **How is the approach evaluated fairly?** — 3 models, topology, calibrated hardware, workloads, RR/LL/Green-LLM baselines, metrics | Table II / experiment setup | 75 s |
| M12 | **Q1: Does carbon-aware scheduling reduce emissions without many SLO misses?** — Figure 4 main frontier; qualify 60%, 3%, and 55% | Figure 4 | 85 s |
| M13 | **Q2: What changes as load grows, and where do TTFT tails appear?** — load regime and tail latency; no misleading average-only story | Figure 4 | 75 s |
| M14 | **Q3: How much do CI spread and facility assumptions matter?** — CI / PUE sensitivity | Figure 5 | 70 s |
| M15 | **Q4: How much does system state freshness/topology/solver overhead matter?** — pick 1–2 main panels; details in Backup | Figure 6 | 75 s |
| M16 | **What remains out of scope, and what can our research build on?** — multi-turn KV locality, heterogeneous inference; distinguish own proposal | Discussion + conclusion | 55 s |
| M17 | **Conclusion** — Problem / Contribution / Key Evidence / Limitation; no new claims | Conclusion | 65 s |

Keep the **Figure 7 output-length/prompt-length sensitivity** in Backup initially; promote selectively if P1 concludes it is essential. Figure 4 is the main result; do not bury it in Backup. A proposed total of 17 Main slides does **not** mean 17 equally dense slides. Prefer uncluttered summary, large plots and explicit caption/legend explanations.

For each Main slide, the P1 outline must record:
`ID | title | one-sentence takeaway | narration goal | exact PDF page+section+figure/table | evidence type (measured/profiled/simulated/author interpretation/our proposal) | key numbers & denominators | suggested original figure or own schematic | backup links | expected speaking time`.

## 4. Source-figure mapping (to be audited in P1)

The authors' repository README identifies:
- **Figure 4:** main comparison / carbon–SLO frontier and TTFT tail; author plots: `figures/sweep/plot_ipdps_frontier.py`.
- **Figure 5:** PUE and carbon-intensity sensitivity; `plot_ipdps_sensitivity.py`.
- **Figure 6:** scheduler overhead, load polling and topology; `plot_ipdps_system.py`.
- **Figure 7:** output sequence length (OSL) prediction and prompt-length sensitivity; `plot_ipdps_workload.py`.
- **Figures 1–3 and 8:** inspect the **original local PDF** for exact captions, panel meanings, and whether any contain compelling simulator validation/motivation. Do not guess their content.
- Main Fig. 4 result data and authors' aggregation scripts live under `data/figures/` and `figures/sweep/`. The repository README says `data/figures/within_node_tp1.csv` contains within-node validation data.

When a plot is used, preserve original axis labels, scales, legend and caption meaning. Cropping subplots is permitted only after inspecting the full original figure and documenting panel A/B correspondence. Never recreate or edit reported numeric results as though they were original measurements. If a custom schematic is drawn, label “Conceptual illustration” / “Adapted from paper” appropriately.

## 5. Discussion/Backup budget (1 index + approx. 10–14 evidence-driven pages)

Use labels `B00` for the clickable discussion index and `B01` onward for distinct deep dives. Candidate topics; finalize after the paper audit and do not produce filler pages:

- Operational-carbon accounting, PUE / host / idle boundary and units.
- Exact SLO definitions and TTFT/TPOT examples, including violation criterion.
- Analytical calibration equations and A100/vLLM profiling conditions.
- Validation: where the simulator matches / does not match real within-node inference.
- Continuous-batching mechanics, queueing, KV capacity admission, long-prefill stalls.
- Greedy objective and the role of its carbon-latency weight.
- Standard ILP variables and load assumption; iterative ILP re-projection/termination.
- Facility MILP batch-shared vs marginal cost, solution time and fallback.
- Baselines RR / LL / Green-LLM / MOER and comparison fairness.
- Figure 7: oracle vs predicted output length; long/mixed prompt sensitivity.
- Sensitivity details from Fig. 5–6 not placed in Main.
- Simulator source layout, reproducibility, missing raw calibration logs.
- Explicit boundaries: no multi-turn cache migration model; no heterogeneous hardware or A/E splitting in main experiments.
- How this work relates to our future HBM/HBF, A/E, and (later) geo-carbon research — hypothesis only.

Each Backup page must provide a **meaningful** Back to Main link and Discussion Index link; every Main-to-Backup link must target a semantically matching page. Avoid the previous error class where a link points to a valid but irrelevant Backup. Main slide page count and PDF page numbers may differ after inserting the index; generate labels, do not hardcode blind destinations.

## 6. Design and expected file layout (future phases)

Reuse theme/palette of the GreenCache Beamer deck: Madrid-based, 16:9, Latin Modern, restrained green/blue/purple accents, rounded soft-color boxes, strong readable headings, dark Ink and muted labels. Reference its specific preamble, navigation/footer, image placement and citation style. Do not import unrelated cached GreenCache content. Use **English technical terms** on slides, avoid overly small mathematical or figure text, and put detailed derivations in Backup.

Expected paths, created only in the appropriate phases:

`
2026-11-18-meeting/
  CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf    # immutable original
  2026-11-18-CarbonSLO-SPEC.md                     # P0, this file
  2026-11-18-CarbonSLO-Outline.md                  # P1
  2026-11-18-CarbonSLO-Evidence.md                 # P1
  PROGRESS.md                                      # P1 onward
  figures/                                         # P2 onward, original-figure crops + provenance
  2026-11-18-CarbonSLO.tex                         # P3 onward
  2026-11-18-CarbonSLO-Script.md                   # P6
  scripts/                                         # P5/P6 build and validation
  README.md                                        # P6
  output/pdf/2026-11-18-CarbonSLO.pdf              # P3/P4 final in P6
  output/overleaf/CarbonSLO.zip                    # P6
  output/qa/                                       # P2/P5/P6
`

The box above is a directory tree, not a shell command. Adjust exact backup count based on readable, evidence-backed content. Original figures, PDFs and finished ZIP are deliverables; ignore transient TeX auxiliaries only. The final Overleaf ZIP must compile with pdfLaTeX without reading external repo directories.

## 7. Token-budget-safe execution: one stage per Codex invocation

**Global rules for every stage:**
1. Read this SPEC and `PROGRESS.md` first (if present); record base HEAD and working-tree state. Never discard unrelated user edits.
2. Work on **exactly the assigned stage**. Do not opportunistically start the next stage. Use small atomic commits with a clear phase prefix. If the working tree has unexpected changes, report them and avoid destructive operations.
3. Leave a checkpoint in `PROGRESS.md`: stage status (NOT_STARTED / IN_PROGRESS / REVIEW_REQUIRED / BLOCKED / ACCEPTED), changed files, claims or decisions, test commands+results, unresolved questions, next recommended action and commit SHA.
4. Prefer deterministic local tools and existing assets. Do not run a full experiment sweep or large builds unless the stage explicitly requires it. Limit log output to useful tails and summaries.
5. If context/window/time is running out, **stop safely**, write an honest checkpoint, commit partial durable work if safe, and return what remains; do not claim complete.
6. After finishing assigned stage, **STOP FOR USER REVIEW**. Never say the next stage has been started; wait for the next prompt.
7. No invented numeric data. Any provisional inference must be visibly marked and traced to a source. The author PDF remains unchanged throughout.

### P0 — Spec and repository preparation (this task)
- Confirm latest commit, 11/11 reference, primary paper, folder and source code. Add this SPEC only.
- **Acceptance:** spec exists in GitHub; original PDF preserved. No LaTeX slide deck built. **Status: done.**

### P1 — Original-paper audit and slide blueprint (**next Codex run, the only stage authorized by launch prompt**)
- Read the local PDF thoroughly, inspect its figures/legends visually, read Introduction, Model/Method, Simulator, Evaluation, Conclusion.
- Validate the M01–M17 narrative and time budget; propose a necessary slide change only if supported by source evidence.
- Create `2026-11-18-CarbonSLO-Outline.md` (one line/entry for **every** Main and candidate Backup), and `2026-11-18-CarbonSLO-Evidence.md` (claims/numbers × exact **PDF page**, section, figure/table, workload, baseline, denominator and evidence class; Figure 1–8 inventory; simulator-origin boundary; ambiguity ledger).
- Spot-check author's code README/reproduction map to identify which figures are backed by scripts/data; no need to run simulator.
- Create/update `PROGRESS.md`, commit **P1 only**, report unresolved ambiguities.
- **Do not create/modify any `.tex`, figure image, PDF, output zip, slide build script, or speaker notes.** No figure extraction in P1.
- **Gate:** all nontrivial headline claims source-registered, figure/page mapping correct, one main takeaway per slide, Main≈15–20 min, paper-vs-our-proposal distinction explicit. **STOP for review.**

### P2 — Figure and source-asset extraction (only after P1 approval)
- Extract original figures/captions from the local PDF; record original PDF page, Figure/panel, bounding box/crop, resolution and SHA/visual verification.
- Inspect every used crop visually: no lost axis, legend or caption, no stretched graphs. Create a Figure-to-Slide map. Do not build the full deck.
- Commit figures + provenance + P2 checkpoint; STOP.

### P3 — Theme + Main first half (only after P2 approval)
- Build clean Beamer source using 11/11 visual conventions, but Carbon–SLO-specific content. Implement **M01–M09 only**, independent compilation where possible.
- Check figure sizes and language, create PDF preview of current slides, record warnings, checkpoint/commit; STOP. Do not silently stub M10–M17 as finished scientific content.

### P4 — Main second half (only after P3 approval)
- Implement **M10–M17**, Fig. 4–6 results, qualified numbers, limits and conclusion.
- Compile all Main slides and visually review montage + large results plots; update evidence/outline if needed, checkpoint/commit; STOP.

### P5 — Backup, navigation and semantic QA (only after P4 approval)
- Implement discussion index and evidence-backed backup pages; bidirectional Main/Backup links and clickable index. Validate targets, backlink origin, visible clickable areas, no invalid/semantically mismatched links, no clipped text.
- Keep Backup in a single post-Main section; maintain Main slide page numbering from 1. Check display/PDF page indices explicitly; checkpoint/commit; STOP.

### P6 — Script, packaging and final QA (only after P5 approval)
- Create a Traditional Chinese **narrative paragraph per Main slide** with page, suggested time, transitions, plot interpretation and sourced claims. Backup gets concise bullet-point Q&A notes. Add explicit answers to “why build a simulator,” “what is real vs simulated,” “how are CI/SLO/cost measured,” “why facility MILP helps,” and “what is missing for HBM/HBF research.”
- README with Main/Backup mapping, figure provenance, claim/source table, commands; pdfLaTeX full build and reproducible standalone Overleaf ZIP; independent ZIP compile; all slides visually reviewed (no overfull, clipping, broken glyphs, misleading crops); navigation QA including link semantics, not merely valid page numbers.
- Save final `output/pdf/2026-11-18-CarbonSLO.pdf` and `output/overleaf/CarbonSLO.zip`, QA artifacts, checkpoint/commit; STOP for final human review.

## 8. P1 pass/fail checklist

P1 is **REVIEW_REQUIRED**, not complete by assumption, until these are satisfied:

- [ ] Exact paper title, authors, year, local PDF version/pages verified.
- [ ] Figure 1–8 inventory and all Main-used figure subpanels verified visually against PDF.
- [ ] M01–M17 one takeaway per slide; no redundant slide or unmotivated detail.
- [ ] All quantitative claims include units, baseline, model/load/scenario and source page.
- [ ] 60% (up to), 3% (average), 55% (up to) properly scoped.
- [ ] Real GPU profiling / calibrated models / geo-serving simulation clearly separated.
- [ ] RR, LL, Green-LLM, and MOER baselines defined without conflation.
- [ ] Operational vs embodied carbon and SLO definitions correct.
- [ ] Paper's evaluated scope distinct from our prospective geo + HBM/HBF and A/E work.
- [ ] Only P1 documents and checkpoint changed; original PDF and 11/11 material untouched.
- [ ] P1 commit created and current status explicitly requires human review.

**Stop condition:** On completion of P1, print a compact stage report: changed file links/paths, P1 commit SHA, proposed Main/Backup count, top 3 evidence ambiguities (if any), checklist/test status, then write: “P1 complete. Awaiting review; P2 not started.” 
