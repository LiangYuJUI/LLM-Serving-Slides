# Research Materials: Power / Carbon Slide Evidence Register

Meeting: 2026-11-18. The current deck has 17 pages. Slide number equals PDF page. Order is Previous Work (3–5), Embodied Carbon (6–9), HBM/HBF Performance and Energy (10–12), proposal (13–14), Thank you (15), backups (16–17). FREESH and the removed GPU-power slide are not current main slides; their notes below are background, not page narration. This is an evidence collection, not a system evaluation.

## Primary sources and verification scope

- **C**: [Carbon–SLO, arXiv:2610.14571v1](https://arxiv.org/abs/2610.14571v1), local `CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf`, 13 pages. Secs. II-C, III-B–D, IV–V and Table I reviewed. Figure 2 copied through the existing With-Caption asset without alteration.
- **H**: [Characterizing High Bandwidth Flash for LLM Serving, arXiv:2609.39131v2](https://arxiv.org/abs/2609.39131v2), 5 October 2026, 10 pages. Original PDF downloaded, Table 1/p. 6, Table 6/p. 8, Table 7/p. 9 rendered and visually checked. Secs. 3, 5.1, 5.3–5.5 checked. **The repository's `Arxiv26_HBF_v4.pdf` is a different paper, not this source.** Existing Characterizing-HBF TeX was used as a locator, not as primary verification.
- **F**: [FREESH, arXiv:2511.00807v1](https://arxiv.org/abs/2511.00807v1), 2 November 2025. Full original paper including appendices available as PDF (26 pages) and [HTML](https://arxiv.org/html/2511.00807v1). Reviewed model/control scope, evaluation setup and router/worker details, rather than inferring missing features from the abstract. Some PDF extraction loses glyphs; original HTML resolves mathematical notation.
- **G**: [GreenCache accessible author preprint, arXiv:2505.23970v3](https://arxiv.org/abs/2505.23970v3), checked against the local final paper for the cited equations/sections. [Publication DOI 10.1145/3788087](https://doi.org/10.1145/3788087), local original paper, 28 pages. Sec. 2.3, Eqs. (1)–(3), PDF pp. 4–5; Sec. 3.2.1, Eqs. (4)–(5), pp. 7–8; Sec. 7 allocation discussion. GPU/CPU energy and modeled storage carbon are distinct accounting terms.
- **R**: REEL LCI v1.0. [HBF article](https://reellci.com/insights/the-hbf-inversion.html), [HBM article](https://reellci.com/insights/hbm-footprint-inversion.html), [HBF dataset](https://reellci.com/d/hbf-gen1-16hi/), [catalogue](https://reellci.com/explorer/?category=memory_components), [methodology](https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf), Sec. 4.4.4, PDF p. 68 / printed p. 66. Existing 2026-11-13 evidence register retained in Research-Materials-SPEC. HBF article and public boundary/assumptions rechecked 2026-11-17. No paid inventory retrieved or manufacturing model rerun.
- **J**: [Janus, arXiv:2512.13525v2](https://arxiv.org/html/2512.13525v2), Sec. 3.1–3.4 and Sec. 4. Separate attention/expert GPU pools, activation scheduling and resource/expert management. No Janus energy-reduction percentage is used.
- **A**: [AFlex, arXiv:2608.01891v1](https://arxiv.org/abs/2608.01891v1), original PDF, 12 pages. Sec. III observations and Sec. IV design: attention/FFN disaggregation and independent frequency control. No speedup or energy percentage transferred to our MoE/HBF proposal.
- **M**: [MemExplorer author publication record](https://www.microsoft.com/en-us/research/publication/memexplorer-navigating-the-heterogeneous-memory-design-space-for-agentic-inference-npus/). Verified qualitative scope only: memory-system synthesis and heterogeneous NPU design exploration. Full-paper energy-model reproduction remains open; no numerical MemExplorer result is used. H's Table 1 attributes its assumed 2× HBF read-energy factor to MemExplorer; that attribution is not independent validation of HBF silicon.

## Slide ledger

| PDF / content | Slide topic | Source and exact location | Configuration / quantitative evidence | Interpretation | Limitations / ownership |
|---|---|---|---|---|---|
| 1 / 1 | Cover | User scope | No experiment | Carbon- and power-aware cross-DC serving with heterogeneous GPU and HBM/HBF co-design | Organization only |
| 2 / 2 | Research Evidence Overview | C, G, R, H | Four chapter cards | Previous work, embodied carbon, memory performance/energy, then the proposal | Our map; no numerical result |
| 3 / 3 | Carbon–SLO: Shared State, Regional Decisions | C Secs. III-A, III-C, IV-A, V-C, VI; Fig. 6(c) | Global snapshot of CI, batch, queue, KV and RTT; independent regional schedulers; A100-only calibration | Prior cross-DC control leaves coordination, embodied carbon and GPU heterogeneity open | Prior architecture plus our synthesis of the gap. Not our measurement |
| 4 / 4 | GreenCache: Carbon-Aware SSD Cache Sizing | G v3 Secs. 3.2.1, 4.1–4.2, 5.4–5.5 | Hourly ILP over predicted CI, request rate and power/SLO profiles | Operational plus allocated embodied carbon for local SSD KV capacity | No cross-DC routing, heterogeneous GPU, or HBM/HBF placement |
| 5 / 5 | Previous Work: Reusable Methods and Research Inputs | C; G; H; R | Methods and inputs only; no new total | Borrow geo scheduling, KV reuse and carbon accounting; still need HBM/HBF models | Integration is our proposal |
| 6 / 6 | HBM/HBF Embodied Carbon Evidence | R catalogue, dataset, methodology Sec. 4.4.4 | REEL v1.0 prospective HBF model | Traceable starting framework | No verified HBF production carbon |
| 7 / 7 | Embodied Carbon per Memory Stack | R HBF and HBM articles | 13.52, 19.81, ≈20.6, 225.9 kg; 225.9/13.52 = 16.7×; 16/24/36 GB and 512 GiB | Higher carbon per HBF stack, with much larger labeled capacity | Model estimates, not a capacity-matched serving result |
| 8 / 8 | Embodied Carbon per Nominal Capacity Unit | Same published numerals | 0.845, 0.825, 0.572, 0.441; 47.8% lower nominal index | Capacity normalization changes the ranking | GB/GiB unresolved; not a verified per-GiB result |
| 9 / 9 | HBF Carbon Estimate: Assumptions and Limitations | R dataset and methodology Sec. 4.4.4 | 16-Hi 512 GiB; 232-layer NAND; 65/28 nm proxies; 175.6 mm² outline | Preliminary scenario input | No production validation; package assembly excluded |
| 10 / 10 | HBM and HBF Memory Access Energy | H Table 1, Sec. 5.1 | 24/375 GB; 1000/1000 and 1000/8 GB/s; 0.1/20 and 0.1/250 µs; 3.4/6.8 and 3.4/100 pJ/bit; 100,000 P/E | Capacity, bandwidth, latency and energy must be modeled together | Not measured HBF silicon. Parameter provenance is slide 17 |
| 11 / 11 | Workload Completion Time Comparison | H Table 6 | GLM-5.2; 16 simulated GPUs; 100k turns. 11,354 / 4,543 / 4,538 s | Added HBF capacity shortens completion by about 60% in this simulation | HBM-only 8+0 is not equal hardware to H³ 8+8 |
| 12 / 12 | Modeled Serving Energy Comparison | H Table 6 | 9.11 / 7.19 / 9.54 MJ. Same 8+8 hardware: (9.54−7.19)/7.19 = 32.7% | Similar completion time can still raise modeled energy | Excludes static/background power. Not a whole-machine increase |
| 13 / 13 | Proposed HBM/HBF-Aware Attention–Expert Placement | J; A; M; H energy assumptions | No result. Local HBM attention worker and HBF expert worker; hot HBM / cold HBF weights | Benefit only if placement gains exceed transfer, waiting and HBF-read costs | **Proposal, not evaluated.** A/FFN is not MoE A/E. HBF stores data |
| 14 / 14 | Research Plan | C; G; H; R as inputs | Calibrate, then local placement, then geo routing and operational plus allocated embodied carbon | Request/session routing across DCs; placement stays inside the selected DC | **Proposal.** No demonstrated energy or carbon reduction |
| 15 / 15 | Thank you | Closing slide | No quantitative evidence | Discussion | No scientific claim |
| 16 / 16 | REEL LCI backup | REEL website, checked 2026-11-17 | 520 datasets, 18 categories | Inventory context for slides 6–9 | Returns to slide 6. Not an independent validation |
| 17 / 17 | HBM/HBF parameter sources | H Table 1 and its cited specifications | S/R/A tags for each parameter | Separates specifications, prior models and SSD proxies | Returns to slide 10. 2× read energy is not measured device power |

## HBF controlled comparison and energy boundary

H Sec. 5.1 assumes all sessions begin at simulation time zero, subsequent turns follow completion plus recorded gaps, and no external arrival-rate constraint is imposed. Mixed batches, session-sticky routing, KV offload, 2,048-token chunked prefill per scheduling engine, index-first placement, sparse MLA lookup and ideal EP token balance apply. GLM uses 32 redundant expert copies. Host model: 16 DDR5-7200 channels (57.6 GB/s and 64 GB each), 32 SSDs (8 GB/s and 1 TB each), PCIe Gen5 x16 ~63 GB/s/direction and a modeled 900 GB/s NVLink endpoint. These are simulator assumptions, not a new hardware experiment.

Table 7's GLM 8+8 1× column uses **HBM weights**, with HBM-only same-model/same-workload energy as the denominator. Savings contributions are +19.50 percentage points weight reads, −0.63 KV/index reads, 0 avoided prefill computation, +2.21 other; published net 21.09%. Rounded contributions sum to 21.08%, intentionally not substituted for the reported net. This is a decomposition of H³/HBM versus HBM-only, **not** a decomposition of the H³/HBM versus H³/HBF placement delta. Mean TPOT for HBM-only/H³-HBM/H³-HBF is 218.72/279.15/278.01 ms. Throughput/completion improvement does not establish SLO compliance.

Sec. 3 Eq. (1) counts arithmetic and memory/link traffic, excluding static power. Thus runtime savings alone do not reduce this modeled energy. A GPU waiting-power term is needed for our total-serving-energy model. No scaling of these MJ values to carbon or J/token is presented without workload/token and electricity-boundary alignment.

## Related-work matrix rationale

- F Eq. (1) / Sec. 3.1 chooses instance counts by location, partition, request type and mode, with power profiles and locational marginal emission rate (which can be negative). This is not interchangeable with average grid CI in attributional accounting. Establish a consistent accounting objective before comparing numerical carbon results.
- F Sec. 3.2 uses MIAD GPU frequency control; Sec. 3.3 uses least-laxity-first queues. App. D.6 describes the actual router's LLF dispatch and weighted round-robin workers. App. D.2 gives TBT, TTFT and E2E congestion thresholds. Therefore “no queue” would misrepresent its implementation.
- F's pool plan uses profiled average latency/service capacity rather than C's explicit per-step queue/batch projection. F's geographically separated testbed is assumed in Sec. 4.1: 4 A100+4 H100, 12 A100+2 H100, and 8 A100 at three locations, with GPU profiling and trace-driven planning. It is not evidence of a fully measured physical three-region WAN deployment.
- C evaluates A100 configurations with distinct models/TP degrees. That does not establish joint heterogeneous GPU-type allocation or DVFS optimization. Its operational accounting does not model manufacturing or HBF placement. F likewise omits manufacturing and HBM/HBF placement from its objective/controls.
- “Not modeled” describes the reviewed paper's formulation, not a universal claim about what its software could support. This FREESH comparison is background and is not a current main slide. AFlex/Janus/MemExplorer remain qualitative context for slide 13.

## Observations / inferences / hypotheses / unknowns

| Area | Observation | Inference | Hypothesis | Unknown |
|---|---|---|---|---|
| Geo/power | C profiles phase-dependent power; F uses heterogeneous profiles and DVFS | Energy-aware location choice depends on workload | Memory profiles can alter the feasible carbon-optimal destination | Common calibrated baseline and marginal vs average CI |
| HBF | H's matched H³ placement changes modeled energy by 32.7% | Placement matters beyond added capacity | Hot/cold expert placement may improve net energy | Waiting/static power, write amplification, thermal/power limits and real HBF measurements |
| Carbon | R's nominal capacity ratio is lower but per-stack footprint higher | Capacity index alone cannot rank serving carbon | Lifetime-aware co-design may change hardware choice | GB/GiB harmonization, inventory reproduction and package attribution |
| Disaggregation | J/A already partition operators; M explores memory/NPU design | A/E plus DVFS alone is not a new contribution | Local memory-aware partitioning plus request routing may help | Transfer energy, SLO and cold-expert behavior |

## Remaining scientific work

No simulator integration, empirical calibration, hardware manufacturing validation or exhaustive novelty review was completed here. Slides 11–12 are one simulated placement study, not a new hardware experiment. Full MemExplorer review, AFlex/Janus quantitative comparison, lifetime allocation and package-level carbon remain open. These are scientific limitations, not build defects.

Source access note: the GreenCache DOI resolves to ACM but automated retrieval returned HTTP 403. Deck hyperlinks use the verified author arXiv v3 (28 pages; accounting sections and equations agree with the local published paper). The DOI remains here for bibliographic traceability.
