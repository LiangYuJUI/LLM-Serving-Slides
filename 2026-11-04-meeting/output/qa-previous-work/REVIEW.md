# Previous Work Review & Research Directions — QA

## Scope and preservation

Latest `origin/main` was fetched and checked at `8d31dc3`. Nine pre-existing uncommitted Energy/Carbon files were preserved. The master imports copies of the current Motivation + Method frames rather than the older committed six-block frames. Helix and all earlier meeting files remain untouched. This describes the initial build; the contents-page revision follows below.

Visual template: 16:9, 10pt Beamer Madrid, Latin Modern, original Helix colors, .45 cm text margins and light-blue title bars. Full paper titles use the existing two-line 11pt title layout. Summary body remains 10pt, with three bullets in each of two aligned sections. No source rows, subtitles, navigation, page-number/category footers, figures or decorative takeaway boxes.

## Slide-to-paper mapping

| Page | Type / category | Content |
|---|---|---|
| 01 | cover  | Previous Work Review & Research Directions |
| 02 | contents | Five research categories with paper counts: 2, 3, 4, 3, 1 (13 total) |
| 03 | category 1 | Power-, Energy-, and Carbon-Aware GPU Serving Optimization |
| 04 | paper 1 | Cache Your Prompt When It's Green — Carbon-Aware Caching for Large Language Model Serving |
| 05 | paper 1 | Beyond Energy: When Sustainability Dimensions Reshape LLM Serving Decisions |
| 06 | category A | HBF System Characterization and KV-Centric Serving |
| 07 | paper A | HBF Sucks? A Full-Stack Characterization of  High-Bandwidth Flash for KV-Centric LLM Serving |
| 08 | paper A | Characterizing High Bandwidth Flash for LLM Serving |
| 09 | paper A | Hot--Cold Tiering of HBM and High Bandwidth Flash  for Agentic LLM Serving |
| 10 | category B | HBM/HBF Architecture and Data-Path Co-Design |
| 11 | paper B | H3: Hybrid Architecture Using High Bandwidth Memory  and High Bandwidth Flash for Cost-Efficient LLM Inference |
| 12 | paper B | FlashAccel: Leveraging High-Bandwidth Flash (HBF)  for High-Throughput LLM Inference |
| 13 | paper B | HBFlex: A Flexible Memory System for Bridging Fine-Grained  LLM States and Coarse-Grained HBF Parallel Execution |
| 14 | paper B | Beyond Capacity: Scalable MoE LLM Inference via  High-Bandwidth Flash with Direct GPU and HBM Paths |
| 15 | category C | HBF Simulation and Power/Thermal Modeling |
| 16 | paper C | HBFSim: Fast and Faithful Simulation of  High-Bandwidth Flash Under Real GPU Execution |
| 17 | paper C | HBFSim: A Simulator for Exploring HBF  in Memory Hierarchies for LLMs |
| 18 | paper C | Understanding the Power Consumption of Modern High Bandwidth Memory:  Experimental Analysis and Modeling Using Real HBM2 DRAM Chips |
| 19 | category D | HBF-Accelerated Retrieval and RAG Systems |
| 20 | paper D | HAVEN: High-Bandwidth Flash Augmented Vector Engine for  Large-Scale Approximate Nearest-Neighbor Search Acceleration |
| 21 | discussion  | What Remains Open in HBM/HBF Co-Design? |
| 22 | discussion  | Proposed Research Directions and Next Steps |

## Source verification and scientific caveats

Twelve primary paper texts were accessed: eight public arXiv PDFs downloaded for this task; GreenCache/PRISM primary PDFs already read in this conversation; Beyond Capacity/HAVEN original PDF text fetched from Drive. H3 is the sole abstract-only summary. Relevant original method/evaluation sections were inspected; no claim of exhaustive reproduction is made.

The professor-provided Drive folder `191Idq-StTW0QH4VFEcMocCDHdUa0Fi6Z` returned 404 through the connector. The original-paper and HBM/HBF research collections were accessible; the missing folder did not prevent reading the required available originals.

### Page 04: greencache

[Primary source](https://arxiv.org/pdf/2505.23970v3). GreenCache arXiv:2505.23970v3, §§5.2–5.5, §6.2, Fig.14(a).

15.1% average and 25.3% peak: Llama-3 70B, French grid, versus Full Cache; peak in multi-turn serving. >90% is reported TTFT/TPOT SLO attainment, not an invented joint success probability. SSD capacity attributes amortized embodied carbon; it does not undo manufacturing. LCS is a heuristic carbon-benefit score.

### Page 05: prism

[Primary source](https://arxiv.org/abs/2609.35569). PRISM arXiv:2609.35569v1, §2 Propositions 1/3, §3 Eq.9, §5.3, Appendix A.6 and Table 12.

50.2% is the median reduction in worst-case regret over 20 capacity seeds in the 12-region study, versus the offline WaterWise adaptation. It is not the percentage reduction of the two separately reported median regrets. Operational invariance fixes workload, location and time; embodied impacts can reverse configuration rankings.

### Page 07: sucks

[Primary source](https://arxiv.org/abs/2608.11668v4). Downloaded arXiv:2608.11668v4; §§5–8, Fig.12, Tables 2/3/8; existing HBF_Sucks TeX and original figure descriptions.

Mooncake-style drop-in substitution with package-resource trade-offs is the evaluated case. More writes than reads, near-tier loss and modeled thermal/wear constraints explain the negative result. Do not generalize to every HBF organization/runtime. The paper’s rhetorical “measured” wording does not make these HBF projections device measurements.

### Page 08: characterizing

[Primary source](https://arxiv.org/abs/2609.39131v2). Downloaded arXiv:2609.39131v2; §§3–4, §6, limitations; existing Characterizing-HBF TeX and figure interpretations.

Trace-driven architecture characterization, calibrated with H100/B200 kernels. Energy uses operation counts and memory/communication traffic and excludes static power. Larger batches can increase TPOT; completion-time gains do not establish SLO gains. Lifetime is estimated, not a physical wear-out measurement.

### Page 09: hotcold

[Primary source](https://arxiv.org/abs/2609.25782v1). Downloaded arXiv:2609.25782v1; §III architecture/data paths and write policy, trace-based evaluation.

Active decode KV stays in HBM. Cold paused KV is evicted to HBF and prefetched back on resume. Immutable blocks with a valid HBF copy need not be written twice. Append-only KV assumption excludes in-place compression/rewrite policies. Qualitative outcome only; no claim of measured HBF hardware power.

### Page 11: h3

Pending access to the original paper. Only the full paper title and “Pending” remain on the slide; all previous summary claims have been removed at the user's request.

### Page 12: flashaccel

[Primary source](https://arxiv.org/abs/2607.10186v2). Downloaded arXiv:2607.10186v2; §§IV–VI architecture, layout and management; evaluation.

Distributed SRAM prefetching, access-order weight layout, KV plane balancing, persistent storage management and programming support are confirmed. Outcome is simulated improvement under a latency constraint, not physical HBF measurement. No headline ratio was imported without its full setup.

### Page 13: hbflex

[Primary source](https://arxiv.org/abs/2609.18675v1). Downloaded arXiv:2609.18675v1; abstract, design sections on KV reads/programs/erases and evaluation.

Full-HBF exploits extra plane parallelism under a packaging budget. Compute-window writeback, lifetime-aware packing and deferred reclamation address different bottlenecks. Relative throughput is qualitative and limited to the evaluated FlashAccel/H3 comparisons.

### Page 14: beyond

[Primary source](https://drive.google.com/file/d/1IHfgK1Tj3ytcPLpDlG87RLXM27l9DEtv/view). Original PDF text fetched from the research Drive collection; arXiv:2608.14333v1 also identified; §§IV–V and evaluation.

DASH assigns whole experts to concurrent direct and HBM-base-die relay routes. Relay does not require staging every expert in HBM cells. Early determination overlaps reads with prior computation; expert and mutable KV traffic are separated. Simulation uses measured GPU compute latencies. No unqualified representative speedup included.

### Page 16: realgpu

[Primary source](https://arxiv.org/abs/2609.09800v3). Downloaded arXiv:2609.09800v3 plus https://github.com/SlugLab/HBFSim README (accessed 2026-11-04).

Paper and artifact scope are distinguished. Default waits occur at issue; dependency-point waits are experimental. Runtime prefetch described in the paper is not yet in main. Capacity eviction/write correctness limitations remain; sparse capacity validation did not exercise eviction. Optional thermal parameters are uncalibrated, and wear counters are not a lifetime/MTBF model. Timing-injection accuracy does not validate future HBF hardware predictions.

### Page 17: event

[Primary source](https://arxiv.org/abs/2610.23503v1). Downloaded arXiv:2610.23503v1 plus https://github.com/FlashLabAE/HBFSim README (accessed 2026-11-04).

Independent MBZUAI/FlashLabAE team and implementation, not SlugLab. Calibrated serving frontend drives a causal event engine with flash translation, NAND operations, resource calendars and wear accounting. Qualitative active-KV placement conclusion is limited to evaluated workloads; endurance is a model projection. Artifact README explicitly separates policies/frontends from the physical engine.

### Page 18: hbmpower

[Primary source](https://arxiv.org/abs/2610.14244v1). Downloaded arXiv:2610.14244v1; abstract, experimental characterization, power-model construction/validation sections.

36 physical HBM2 chips, command/bank/data-pattern characterization, DRAMPower-derived model; additional HBM3E GPU validation. This is direct evidence for HBM power modeling only. Extrapolation to other generations or HBF requires separate calibration. No HBF device measurement is implied.

### Page 20: haven

[Primary source](https://drive.google.com/file/d/1B2Sy8GHSAgfoiHFMcmndiJHMQ1G9KODf/view). Original PDF text fetched from the research Drive collection; arXiv:2603.01175v1 identified; §§3–5 architecture and evaluation.

IVF-PQ retrieval and full-precision reranking, not general autoregressive decode. HBF holds large vector data; near-storage search support reduces off-GPU movement. Results are modeled under power-constrained flash bandwidth. Numeric “up to” reranking gains omitted to avoid presenting them as end-to-end RAG speedups.

## Research synthesis boundaries

Pages 21–22 are explicitly candidate questions and proposed next steps. They do not claim first discovery, established novelty or a finalized thesis proposal. Compare architectures under common package/power constraints; distinguish active/paused/reusable KV; reproduce both simulators before model integration or strong hardware conclusions. Retention maintenance and power/thermal interaction are evaluation questions, not claimed contributions of every reviewed paper.

## Build and visual validation

Run `python scripts/build_previous_work.py` from this meeting directory, using Python with PyMuPDF and Pillow plus pdfLaTeX on PATH. Tested with `/tmp/helix-qa-env/bin/python` and TeX Live 2026.

- Exactly 22 pages, 12 completed paper summaries and one pending H3 placeholder and five category covers in the requested order.
- All full paper titles checked against the category index after typography normalization.
- Each completed paper summary: one bold teal Motivation heading, one Method heading and six bullets; 10pt body font; identical heading positions.
- No PDF links, subtitles, source rows, obsolete standalone section labels or page-number footers.
- Every text span is in bounds with bottom clearance; pairwise span-overlap checks pass.
- Local source and extracted ZIP each compiled twice. Final logs contain no warnings, undefined references or overfull boxes.
- ZIP contains main.tex, all six category/direction TeX modules and README.txt. It requires no external assets or repository files.
- Local versus standalone: all 22 pages have identical extracted text, rendered pixels and link annotations.
- All 22 pages rendered at 2.5x. Both montage sheets reviewed for consistent layout and density; long HBM title and final discussion pages additionally inspected at full size. No clipping or overlaps found.
- New build hashes pre-existing files outside its own artifacts before/after; final task-level baseline independently checks all pre-existing repository files, including uncommitted Energy/Carbon work.
- Build intermediates are temporary. QA retains only previews, montage, checks and documentation.

`validation.json` records automated checks. `montage-01.png` covers pages 1–12; `montage-13.png` covers pages 13–22. Each page also has its own PNG.

## Contents-page revision

Inserted Contents after the cover, listing all five categories and paper counts (2, 3, 4, 3, 1; total 13). Updated the slide index and validation to 22 pages. Removed the obsolete standalone Energy-Carbon-Summary PDF.

Validation passed for 22 pages and the standalone ZIP. Visually inspected the new contents page: category labels, counts and total fit without clipping or overlaps. All 21 original pages retain identical extracted text and rendered pixels after insertion.

## Characterization presentation order

Swapped pages 7 and 8: HBF Sucks? now precedes Characterizing HBF, presenting system characterization and design conditions before hierarchical memory management and cache-aware scheduling. Updated the category cover paper order and index.
