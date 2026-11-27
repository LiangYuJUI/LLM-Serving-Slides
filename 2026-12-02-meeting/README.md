# 2026-12-02 LLM Serving Research Meeting

## Paper Review — Kareto

The Paper Review is a 19-slide English main presentation followed by 17 backup slides. The main section reviews Kareto v1 and presents a clearly labeled, proposed energy / carbon research direction. Backup slides hold source figures, implementation detail, ablations, and proposed analysis. Main slides use semantic PDF links to the relevant appendix pages; every backup page has return navigation.

### Main slides

1. Adaptive Multi-Objective Tiered Storage Configuration for KV Cache in LLM Service
2. Workload-Dependent KV Cache Reuse
3. Cache Capacity Saturation and Diminishing Returns
4. Workload Density Changes the Value of SSD Prefetching
5. Density Changes Reuse, Throughput, and TTFT
6. Kareto Optimizes Throughput, Latency, and Economic Cost
7. Kareto Uses an End-to-End Discrete-Event Simulator
8. Empirical GPU Profiling Feeds Execution-Time Models
9. Adaptive Pareto Search Refines High-Impact Regions
10. Group TTL Allocates Disk Retention by Reuse Pattern
11. Evaluation Uses Three Trace Types and Two Cluster Scales
12. Simulator Fidelity Is Validated on Three Storage Configurations
13. Adaptive Provisioning Improves Distinct Objectives
14. Kareto and GreenCache Address Complementary Decisions
15. Energy-Aware Multi-Tier Cache Management Is a Gap to Validate
16. Energy-Aware Cache Decisions Must Respect Data Availability
17. GPU Models Should Separate Prefill and Decode Operations
18. System Energy Requires Consistent Component Accounting
19. A Validated Energy Model Can Guide SLO-Constrained Optimization

### Backup slides

1. KV Cache Lifetime and Storage Requirements
2. DRAM Bandwidth Sensitivity
3. Disk Bandwidth and Capacity Are Coupled
4. Workload Density and Storage Capacity
5. Full Tier Reuse Results
6. Planner, Simulator, and Selector
7. Kareto Simulator Architecture
8. Adaptive Pareto Search Ablation
9. Prefix-Tree Reuse Concentration
10. Group Reuse-Interval Distributions
11. ROI-Aware Group TTL Allocation
12. Group TTL Reuse Ablation
13. Group TTL Reuse-Interval Ablation
14. Group TTL Performance and Cost
15. Real-System Simulator Validation
16. KV Reuse Energy Break-Even Model (proposed)
17. Energy and Carbon Accounting Boundaries (proposed)

### Outputs

- [Final PDF](output/pdf/2026-12-02-Paper-Review.pdf)
- [Standalone Overleaf ZIP](output/overleaf/Paper-Review.zip), with `main.tex` entry point and only required figure assets
- [Evidence Register](2026-12-02-Paper-Review-Evidence.md)
- [Research specification](2026-12-02-Research-Discussion-SPEC.md)
- [QA validation report](output/qa/validation.md)
- [QA montage](output/qa/paper-review-montage.png)

### Figure inventory and source mapping

All images are user-supplied extractions from Kareto arXiv v1. Main slides use the `Without-Caption` originals with slide-authored summaries; appendix pages use `With-Caption` versions where they improve source readability.

| Source item | Slide use | Notes |
|---|---|---|
| Figure 1 | B1 | Cumulative vs active block count; oracle TTL reference |
| Figures 2–3 | Main 2–3 | Reuse-hit Lorenz curves; capacity saturation |
| Figure 4 | Main 7, B7 | Simulator architecture |
| Figure 5 | Main 5, B4 | Capacity impact in compute-bound vs compute-abundant cases |
| Figure 6 | B5 | DRAM / disk reuse under Trace A and instance scales |
| Figure 7 | B3 | Disk bandwidth and reuse ratio by capacity |
| Figure 8 | Main 6 | Two-instance pure DRAM / pure disk / hybrid comparison |
| Figure 9 | B6 | Planner ↔ simulator ↔ selector overview |
| Figures 10–11 | Main 10, B9–B11 | Reuse group ranking, intervals, and group TTL method |
| Figure 12 | Main 13 | Separate throughput, TTFT, and cost operating points |
| Figure 13 | B8 | Adaptive vs grid search points and hypervolume |
| Figure 14 | B12 | Group TTL vs fixed TTL reuse comparison |
| Figure 15 | B13 | Group TTL ablation study panels |
| Figure 16 | B14 | Group TTL performance and cost |
| Figure 17 | Main 12, B15 | Real-system validation; HTML version currently labels it Figure 19 |
| Table 1 | B2 | DRAM bandwidth sensitivity and TTFT |

Conceptual TikZ diagrams: tiered HBM–DRAM–SSD hierarchy (Main 1); low-/high-density prefetch timelines (Main 4); workload/configuration → simulator → metrics flow (Main 7); adaptive Pareto sampling (Main 9); group TTL workflow (Main 10); request cache-reuse / restore / recompute decision path (Main 16); prefill/decode × Attention/FFN matrix (Main 17); proposed simulator-extension plan (Main 19); retain-vs-recompute break-even comparison (B16). Conceptual diagrams are labeled as such and are not experimental curves.

## Research Topic Discussion

The independent 10-slide Research Discussion presentation is retained without source-content changes.

- [PDF](output/pdf/2026-12-02-Research-Discussion.pdf)
- [LaTeX source](2026-12-02-Research-Discussion.tex)
- [Overleaf ZIP](output/overleaf/Research-Discussion.zip)

## Build and QA

Requires `pdflatex` plus Python packages `pymupdf` and `pillow`. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install pymupdf pillow
.venv/bin/python 2026-12-02-meeting/scripts/build.py
.venv/bin/python 2026-12-02-meeting/scripts/validate.py
```

Expected page counts are declared in `deck_manifest.json` (19 main + 17 backup for Paper Review; 10 slides for Research Discussion). The builder compiles each local and extracted ZIP deck twice, checks warnings and page bounds, verifies internal PDF links, exports only declared figure dependencies, compares local and packaged text / rendered pixels, refreshes Paper Review PNGs, and writes `output/qa/validation.json` and `validation.md`.

## QA status

Build and visual QA are recorded in [validation.md](output/qa/validation.md). Full-size page renders are in `output/qa/pages/`; montage files are for fast review, while individual renders were inspected for title fit, diagram clipping, figure readability, and footer numbering.

## Known limits and unresolved checks

- Kareto is described as an arXiv preprint; no conference venue is claimed.
- Supplied validation art is named Figure 17, while current arXiv HTML calls the corresponding validation result Figure 19; the v1 PDF page needs a final cross-check.
- Exact GPU model/count and tensor / pipeline parallel configuration for the emulated evaluation are not inferred from the cloud instance name.
- Kareto validates performance metrics on selected GPU-only, GPU+DRAM, and GPU+disk configurations; the reported maxima are not energy, power, carbon, or TPOT validation.
- GreenCache already includes carbon-aware sizing and Least Carbon Savings replacement; its paper uses typical DRAM/SSD specification power rather than activity-aware storage energy measurements.
- LLMServingSim 2.0 is a candidate foundation. A storage idle-power field does not establish SSD KV restore timing, migration, or read/write contention support.
- Phase-specific GPU energy, storage-transfer calibration, restore-vs-recompute break-even points, and the proposed research novelty all require measurement and literature validation.
- The current proposal focuses on one server and HBM–DRAM–SSD. HBF is outside scope.
