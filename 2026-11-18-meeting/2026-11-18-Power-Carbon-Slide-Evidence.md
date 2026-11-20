# Research Materials evidence register

Revised 2026-11-20 (Asia/Taipei). **22 pages: main 1–16, supplements 17–22.** Published evidence, modeling assumptions and our proposed work are distinct. No experiment or simulator integration was performed for this slide revision.

## Primary sources and verification scope

- **C**: [Carbon–SLO, arXiv:2610.14571v1](https://arxiv.org/abs/2610.14571v1), local `CarbonSLO-GeoDistributed-LLM-Serving-2026.pdf`, 13 pages. Secs. II-C, III-B–D, IV–V and Table I reviewed. Figure 2 copied through the existing With-Caption asset without alteration.
- **H**: [Characterizing High Bandwidth Flash for LLM Serving, arXiv:2609.39131v2](https://arxiv.org/abs/2609.39131v2), 5 October 2026, 10 pages. Original PDF downloaded, Table 1/p. 6, Table 6/p. 8, Table 7/p. 9 rendered and visually checked. Secs. 3, 5.1, 5.3–5.5 checked. **The repository's `Arxiv26_HBF_v4.pdf` is a different paper, not this source.** Existing Characterizing-HBF TeX was used as a locator, not as primary verification.
- **G**: [GreenCache accessible author preprint, arXiv:2505.23970v3](https://arxiv.org/abs/2505.23970v3), checked against the local final paper for the cited equations/sections. [Publication DOI 10.1145/3788087](https://doi.org/10.1145/3788087), local original paper, 28 pages. Sec. 2.3, Eqs. (1)–(3), PDF pp. 4–5; Sec. 3.2.1, Eqs. (4)–(5), pp. 7–8; Sec. 7 allocation discussion. GPU/CPU energy and modeled storage carbon are distinct accounting terms.
- **R**: REEL LCI v1.0. [HBF article](https://reellci.com/insights/the-hbf-inversion.html), [HBM article](https://reellci.com/insights/hbm-footprint-inversion.html), [HBF dataset](https://reellci.com/d/hbf-gen1-16hi/), [catalogue](https://reellci.com/explorer/?category=memory_components), [methodology](https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf), Sec. 4.4.4, PDF p. 68 / printed p. 66. Existing 2026-11-13 evidence register retained in Research-Materials-SPEC. HBF article and public boundary/assumptions rechecked 2026-11-17. No paid inventory retrieved or manufacturing model rerun.
- **M**: [MemExplorer author publication record](https://www.microsoft.com/en-us/research/publication/memexplorer-navigating-the-heterogeneous-memory-design-space-for-agentic-inference-npus/). Verified qualitative scope only: memory-system synthesis and heterogeneous NPU design exploration. Full-paper energy-model reproduction remains open; no numerical MemExplorer result is used. H's Table 1 attributes its assumed 2× HBF read-energy factor to MemExplorer; that attribution is not independent validation of HBF silicon.


- **L**: [Helix, ASPLOS 2025](https://doi.org/10.1145/3669940.3707215), original `2026-10-28-meeting/ASPLOS25_Helix.pdf`. Secs. 3–5 establish GPU/network profiling, max-flow abstraction, MILP placement and runtime request scheduling. Secs. 6.1–6.4 distinguish the real single-cluster prototype from simulated geo-distributed and high-heterogeneity experiments. Cross-checked against the existing Helix deck/script. New native diagram is a method summary, not a reproduced paper figure.
- **T**: [ThunderServe, MLSys 2025 original PDF](https://proceedings.mlsys.org/paper_files/paper/2025/file/c2a0e26dd9ee7d57e92bb1c24b39659a-Paper-Conference.pdf), local `2026-10-21-meeting/MLSys25_Thunderserve.pdf` (arXiv:2502.09334v2). Table 3 on PDF page 8: Coding prefill 4+1+2+1=8, decode 1+2+1=4; Conversation prefill 3+1=4, decode 1+1+1+4+1=8. Sec. 5.1 describes the 32-GPU cloud pool; these counts are replicas. The web-extracted table incorrectly reports 2 instead of 1 for Coding's mixed-GPU prefill row; the original PDF controls. No Figure 9 throughput ratios are included, avoiding mixed cloud/in-house baseline attribution. Existing October 28 materials and script corroborate the counts.
- **S**: [LLMServingSim official overview](https://llmservingsim.ai/docs/getting-started/overview), [architecture](https://llmservingsim.ai/docs/simulator/architecture), [2.0 paper](https://arxiv.org/abs/2602.23036), [ISPASS 2026 artifact](https://zenodo.org/records/18879965). Documentation reviewed 2026-11-20. Python frontend owns scheduling, batching, prefix caching, memory accounting and traces; ASTRA-Sim backend models compute/collective communication. Official documentation describes heterogeneous/disaggregated serving and profiled kernels. HBF-specific behavior, energy calibration and multi-DC CI/PUE routing are proposed extensions, not verified built-in functionality. No published accuracy percentage is transferred to RCITI.
- **RCITI**: environment selected in the user's professor-feedback brief. Repository inspection found no verified cluster inventory. Types, counts, power measurements and access are explicitly unconfirmed; no real HBF hardware is asserted.

## Current slide ledger

| PDF | Topic | Source / location | Evidence | Boundary |
|---|---|---|---|---|
| 1 | Research Overview | User scope | Research question and identity only | No experimental result |
| 2 | Research Evidence Overview | C, G, L, T, H, S | Index → 3, 7, 12, 14 | No embodied-carbon chapter |
| 3 | Carbon–SLO: Shared State, Regional Decisions | C Secs. III-A, III-C, IV-A, V-C, VI; Fig. 6(c) | Shared state, independent regional scheduling, A100 profiles | Our synthesis connects local energy/SLO costs to routing |
| 4 | GreenCache: Carbon-Aware SSD Cache Sizing | G Secs. 3.2.1, 4.1–4.2, 5.4–5.5 | SSD cache size; operational and allocated embodied carbon | No joint heterogeneous GPU/HBM/HBF placement |
| 5 | Helix: Heterogeneous GPU Placement | L Secs. 3–5, 6.1–6.4 | Profiling, max-flow/MILP and runtime scheduling | Real single-cluster prototype; geo and high-heterogeneity simulations |
| 6 | ThunderServe: Workload-Aware Serving | T Secs. 3.2–3.4, 5.1, 5.3; Table 3 | LLaMA-30B Coding 8/4; Conversation 4/8 prefill/decode replicas | Replica counts, not physical GPU counts |
| 7 | Different LLM Workload Characteristics | T Sec. 3.4, Fig. 6, Table 3; G Secs. 2–3; H Secs. 1, 3.2–3.3, 4.2 | Relative input/output demand; session state and reuse | Implications are proposed; categories overlap |
| 8 | Research Gaps and Required Models | C, G, L, T, H | Specific integration of measured local profiles and GPU/memory exploration | Novelty still requires systematic verification |
| 9 | HBM and HBF Memory Access Energy | H Table 1, Sec. 5.1 | 24/375 GB; 1000/1000 and 1000/8 GB/s; 0.1/20 and 0.1/250 µs; 3.4/6.8 and 3.4/100 pJ/bit; 100,000 P/E | Modeled parameters; provenance at page 22 |
| 10 | Workload Completion Time Comparison | H Table 6 | GLM-5.2, 16 simulated GPUs, TP16/EP16, 100k turns; 11,354 / 4,543 / 4,538 s | Published MoE simulation; 8+0 vs 8+8 is unequal memory hardware |
| 11 | Modeled Serving Energy Comparison | H Table 6 | 9.11 / 7.19 / 9.54 MJ; +32.7% = (9.54/7.19−1)×100 | Same H³ 8+8 weight-placement comparison; excludes static/background |
| 12 | Proposed Workload-Aware GPU/Memory Placement | Our proposal informed by L, T, G, H | GPU choice, memory configuration, weights, active/reusable KV, optional phases | No MoE-specific architecture or demonstrated savings |
| 13 | Proposed Serving and Scheduling Architecture | Our proposal informed by C, G, L | Global request/session routing; local hardware and memory placement | Operational carbon primary; embodied later with adequate data |
| 14 | Experimental Environment and Simulator | User-specified RCITI environment; S overview and architecture | Real Dense LLM profiling ↔ simulator calibration and validation | Inventory/access unconfirmed; no actual HBF hardware assumed |
| 15 | Research Roadmap and Evaluation Plan | Our planned evaluation; C, T, H, S | Calibration → placement → geo scheduling; fair baselines | Report errors, resources, trace, precision and SLOs |
| 16 | Thank You | Closing | Thank You | No claim |
| 17 | HBM/HBF Embodied Carbon Evidence | R catalogue, dataset, methodology Sec. 4.4.4 | Prospective HBF model, public methodology | Not verified production carbon |
| 18 | Embodied Carbon per Memory Stack | R HBF/HBM articles | 13.52 / 19.81 / ≈20.6 / 225.9 kg; 16.7× | 16/24/36 GB vs 512 GiB; not capacity matched |
| 19 | Embodied Carbon per Nominal Capacity Unit | R published values; our division | 0.845 / 0.825 / 0.572 / 0.441; 47.8% | Nominal capacity index; GB/GiB unresolved |
| 20 | HBF Carbon Estimate: Assumptions and Limitations | R dataset and methodology | 16-Hi, 512 GiB, 232-layer, 65/28 nm, 175.6 mm² proxy | No verified production data; package assembly excluded |
| 21 | REEL LCI: Database Background and Inventory Scope | R official website, verified 2026-11-17 | 520 datasets, 18 categories; inventory scope | Returns to 17; does not validate the HBF model |
| 22 | Sources of the HBM/HBF Memory Parameters | H Table 1 and cited references | Micron, Lenovo, H³, Ma/Patterson, Moon, MemExplorer, Son and SSD proxies | Returns to 9; 2× read energy is not measured device power |

## HBF controlled comparison and energy boundary

H Sec. 5.1 assumes all sessions begin at simulation time zero, subsequent turns follow completion plus recorded gaps, and no external arrival-rate constraint is imposed. Mixed batches, session-sticky routing, KV offload, 2,048-token chunked prefill per scheduling engine, index-first placement, sparse MLA lookup and ideal EP token balance apply. GLM uses 32 redundant expert copies. Host model: 16 DDR5-7200 channels (57.6 GB/s and 64 GB each), 32 SSDs (8 GB/s and 1 TB each), PCIe Gen5 x16 ~63 GB/s/direction and a modeled 900 GB/s NVLink endpoint. These are simulator assumptions, not a new hardware experiment.

Table 7's GLM 8+8 1× column uses **HBM weights**, with HBM-only same-model/same-workload energy as the denominator. Savings contributions are +19.50 percentage points weight reads, −0.63 KV/index reads, 0 avoided prefill computation, +2.21 other; published net 21.09%. Rounded contributions sum to 21.08%, intentionally not substituted for the reported net. This is a decomposition of H³/HBM versus HBM-only, **not** a decomposition of the H³/HBM versus H³/HBF placement delta. Mean TPOT for HBM-only/H³-HBM/H³-HBF is 218.72/279.15/278.01 ms. Throughput/completion improvement does not establish SLO compliance.

Sec. 3 Eq. (1) counts arithmetic and memory/link traffic, excluding static power. Thus runtime savings alone do not reduce this modeled energy. A GPU waiting-power term is needed for our total-serving-energy model. No scaling of these MJ values to carbon or J/token is presented without workload/token and electricity-boundary alignment.


## Research boundary and remaining verification

The proposed target begins with representative Dense LLM workloads. Published GLM-5.2 MoE evidence remains only to motivate memory/energy trade-offs. General GPU heterogeneity, prefill/decode separation, max-flow placement and cache reuse are not claimed as new contributions. HBF serving itself already studies placement and workload effects; the specific combination to investigate is calibrated heterogeneous GPU/memory energy under SLO constraints and its effect on cross-DC routing. This is not an exhaustive novelty claim.

Future work must inventory the RCITI cluster, obtain workload traces, measure power/latency, validate model generalization on held-out workloads and configurations, implement missing simulator interfaces, and quantify GPU idle power, memory/link traffic, write/endurance and cache migration effects. GPU telemetry and modeled memory energy must have nonoverlapping boundaries. Apply PUE once. Evaluate session affinity/migration and queue-state staleness in global routing. No actual carbon savings are established.

REEL values remain screening estimates. Reproduction of inventory totals, GB/GiB harmonization, manufacturing process assumptions, package boundaries and lifecycle allocation remain open. Primary planned accounting is operational energy/carbon; embodied carbon is supplementary context for a later extension.

GreenCache DOI retrieval previously returned HTTP 403; the PDF uses the verified author preprint link. Clickable citation annotations are validated independently of remote server availability.
