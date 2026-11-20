# Research Materials specification

Meeting: 2026-11-18. Revised: **2026-11-20, Asia/Taipei**. Yu-Jui Liang; advisor Hsiang-Yun Cheng; National Taiwan University / Academia Sinica.

Repository: https://github.com/LiangYuJUI/LLM-Serving-Slides.git. Actual starting HEAD was clean `51548444d0d896c8302ad94a9c81cae3f2ed571d`. This revision supersedes the earlier 17-page contract and the earlier preference not to update speaker notes.

## Current contract

**19 pages, 13 main and 6 supplementary.** Thank You is page 13. Footer equals physical PDF page, 1/19–19/19. The [page map](2026-11-18-Research-Materials-Page-Map.md) defines exact titles, stable labels and index destinations. English slides and Traditional Chinese speaker script.

Research direction (simplified 2026-11-20): **coordinated, workload-aware, power- and carbon-aware LLM serving on heterogeneous GPUs**. Investigate whether workload-aware, coordinated heterogeneous GPU scheduling reduces serving energy and operational carbon under latency SLOs, using local heterogeneous GPU costs for cross-DC routing. This is a proposal, not an experimental result. GPU heterogeneity, prefill/decode splitting and prior placement algorithms are established work, and related carbon-aware work (e.g. GreenLLM) exists, so novelty remains to be established. HBM/HBF is kept only as published evidence (pages 8–10 and supplements) and is not a research commitment. Attention/expert disaggregation and the HBM/HBF co-design slide were removed from the proposed architecture.

## Design and preservation

Madrid Beamer, 16:9, Latin Modern, 0.48 cm margins and original title/footer geometry. Ink #243748, Muted #667B8B, Accent #347E74, AccentBlue #507DAD, SoftMint #E6F4EE, SoftLilac #F1EEF8, Paper #FBFCFE. Preserve the existing source-footer style, cards, tables and TikZ charts. New conceptual diagrams use native TikZ and cite the source of prior methods.

Four index cards link to pages 3, 7, 11 and 12. No embodied-carbon chapter is exposed in the main index. REEL pages 14–17 and original supplements 18–19 preserve scientific content, units and charts. REEL original hashes remain enforced. GreenCache, Table 1 and both source supplements remain unchanged. Table 6 frames only add the MoE scope clarification to the source area. The GLM-5.2 comparison remains a published MoE simulation, not a Dense LLM measurement. Thank You remains unchanged.

## New evidence and proposed evaluation

- Helix: ASPLOS 2025 max-flow/MILP placement and runtime scheduling. Single-cluster prototype versus simulated cross-region/high-heterogeneity settings are distinguished.
- ThunderServe: MLSys 2025 Table 3, LLaMA-30B. Coding has 8 prefill / 4 decode replicas; Conversation has 4 / 8. These are replicas, not GPU counts. No throughput comparison between different hardware baselines is imported.
- Workloads: Coding and Conversation are relative characteristics of the cited workloads. Multi-turn/agentic reuse uses GreenCache and Characterizing HBF evidence. Proposed implications are marked separately, and categories can overlap.
- CITI: proposed Dense LLM profiling environment. GPU inventory, counts and access must be established before experiments. No available HBF hardware is claimed.
- LLMServingSim 2.0: official overview and architecture reviewed on 2026-11-20. Documented heterogeneous/disaggregated serving, batching/scheduling, KV models, compute profiles and ASTRA-Sim communication. HBF access/placement, calibrated energy integration and geo carbon scheduling are proposed work requiring implementation and validation. Do not generalize published simulator accuracy to this new setup.
- Roadmap and scheduling architecture: removed from the deck on 2026-11-20 at the professor's request. The final main slide (page 12) only introduces the available environments, LLMServingSim 2.0 and planned real GPU profiling on the CITI cluster, with no research phases or architecture commitment.

## Accounting and fair comparison

Report hardware count, memory capacity, precision, model, workload trace and SLO constraints. Separate capacity expansion from policy gains. Measure power over time to obtain energy; GPU telemetry alone does not measure whole-server energy. Model memory/link energy without double counting telemetry-covered components. Include idle/background terms for the planned serving-energy model, and apply PUE once at the appropriate IT-energy boundary. Global routing should account for WAN delay and session/cache locality or migration costs.

Operational energy/carbon is primary. Allocated embodied carbon is a later extension conditional on defensible lifecycle data, lifetime/utilization allocation and component boundaries. Never add memory-stack footprints to a GPU footprint that already includes them.

## Build and validation

```sh
python3 -m venv /tmp/research-materials-qa
/tmp/research-materials-qa/bin/pip install pymupdf pillow
/tmp/research-materials-qa/bin/python 2026-11-18-meeting/scripts/build_research_materials.py
/tmp/research-materials-qa/bin/python 2026-11-18-meeting/scripts/test_research_materials.py
```

Requires pdfLaTeX, Beamer, TikZ and Latin Modern. The builder compiles twice locally and twice from the extracted self-contained Overleaf ZIP. It enforces 19 pages, all frame positions, full-width index links, supplement round trips, source citations, footer numbers, bounds, scientific values and evidence preservation. Local and ZIP text, rendered pixels and link annotations must match. Final-pass LaTeX warnings cause failure. Negative tests verify that broken navigation and missing evidence are rejected.

Artifacts: `output/pdf/2026-11-18-Research-Materials.pdf`, `output/overleaf/Research-Materials.zip`, `output/qa/pages/research-materials-01.png` through `-19.png`, and `output/qa/research-materials-montage.png`. QA records are in `output/qa/validation.md` and the research-materials JSON reports. Every rendered page must also be visually inspected. Unrelated decks and source papers are protected.

## Preserved REEL provenance

The following scientific source register was established on 2026-11-13 and rechecked in the earlier revision on 2026-11-17. Moving it into supplements does not provide independent validation or new inventory access. Current pages are 17–20.

## Source register and access results

| ID | Exact URL | Version / evidence used |
|---|---|---|
| A | https://reellci.com/insights/the-hbf-inversion.html | Updated 2026-09-10, explicitly REEL LCI v1.0 (released 2026-08-21). Published screening carbon values and comparison chart. |
| B | https://reellci.com/insights/hbm-footprint-inversion.html | Updated 2026-09-10, explicitly v1.0. HBM3E 12-Hi 36 GB: approximately 20.6 kg CO2e, IPCC 2021 GWP100. |
| C | https://reellci.com/d/hbf-gen1-16hi/ | Current page says release v1.0, UUID 95408b13-60a3-4a44-a48b-9e104a8ccd2b. Architecture, process proxies, data quality, scope, uncertainties. |
| D | https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf | Downloaded successfully with curl after web-tool retrieval failed. Section 4.4.4, PDF page 68 / printed page 66, rendered and inspected. |
| E | https://reellci.com/explorer/?category=memory_components | v1.0 catalogue; public documentation, not full inventory quantities. |
| F | https://reellci.com/d/hbm3-8hi/ | Current v1.0, HBM3 16GB, 8-Hi; component boundary. |
| G | https://reellci.com/d/hbm3-12hi/ | Current v1.0, HBM3 24GB, 12-Hi. |
| H | https://reellci.com/d/hbm3e-12hi/ | Current v1.0, HBM3E 36GB, 12-Hi. |

Methodology downloaded bytes SHA-256: `9ec048a91696086cb2087889dece3abf5fbe8af67c00261c24a0f1cb54f63042`. PDF p. 68 is a physical page index starting at 1; printed p. 66 is the page number displayed in the document. They are not interchangeable.

E lists HBM3 8/12-Hi, HBM3E 8/12-Hi, HBM4 8/12/16-Hi with mature/ramp variants, and HBF Gen 1 16-Hi. Availability here means a catalogue/documentation entry exists; no paid inventory was purchased or claimed as retrieved. No HBM4 carbon number is plotted.

## Exact data and derived values

All carbon inputs below are **REEL LCI model estimates reported in v1.0 insights**, not manufacturer-verified product footprints. Values are reproduced as published, not recomputed from the detailed life cycle inventory. This is neither an independently validated LCA nor a peer-reviewed HBF study.

| Configuration | Source capacity label | kg CO2e / stack | Carbon source | Our division by capacity numeral | Chart label |
|---|---|---:|---|---:|---:|
| HBM3 8-Hi | 16 GB (F and A prose); A chart says GiB | 13.52 | A chart | 13.52 / 16 = 0.845 | 0.845 |
| HBM3 12-Hi | 24 GB (G and B); A chart says GiB | 19.81 | A chart | 19.81 / 24 = 0.8254166667 | 0.825 |
| HBM3E 12-Hi | 36 GB (H and B) | approximately 20.6 | B | 20.6 / 36 = 0.5722222222 | approximately 0.572 |
| HBF Gen 1 16-Hi | 512 GiB (C and A) | 225.9 | A chart | 225.9 / 512 = 0.4412109375 | 0.441 |

No v0.1 results were used. B rounds HBM3 values to 13.5 and 19.8; A gives 13.52 and 19.81. This is consistent with rounding, so the chart retains A's precision without manufacturing extra digits for HBM3E.

The y-axis on current PDF page 19 (REEL3) is **kg CO2e / nominal capacity unit**. This is an arithmetic index based on the label numerals, not a physical-unit-harmonized carbon intensity. No assumption that GB equals GiB is made. The explicit units remain beside each bar.

Derived comparisons, always using unrounded inputs:

- Per-stack ratio: `225.9 / 13.52 = 16.7085798817`, displayed 16.7x.
- Nominal capacity numeral ratio: `512 / 16 = 32`. This is not a verified physical capacity ratio.
- Normalized ratio: `(225.9 / 512) / (13.52 / 16) = 0.5221431213`.
- Nominal reduction: `100 * (1 - (225.9 / 512) / (13.52 / 16)) = 47.78568787%`, displayed 47.8%.
- If HBM GB were confirmed decimal, convert to GiB with `GB * 10^9 / 2^30` before division. If it were confirmed a shorthand for binary capacity, the numeric capacities could be used directly. Neither interpretation has been established here, so no converted claim is on the slides.

## Model assumptions, boundaries and conflicts

C uses 232-layer NAND, 65 nm CMOS-peripheral and 28 nm base-logic proxies. A 10.975 x 16 mm device envelope yields 175.6 mm²; the central die-yield proxy is `exp(-0.005 * 175.6) ≈ 0.416`, with 0.670 described as a favorable bound. These are current public dataset assumptions, **not verified reconstruction parameters for A's 225.9**.

C explicitly discloses a die-capacity/area inconsistency, a package outline substituted for measured die geometry, and packaging/material gaps. Package-level interposer, redistribution, organic substrate and assembly are excluded from the stack; they require additional accounting without double counting. Operational electricity is outside this manufacturing boundary. Semiconductor-fab electricity is part of manufacturing, not serving operational energy.

D describes a prospective dataset and an approximate −24%/+32% band, alongside about 243 kWh per component. That energy number is not a carbon value, and no grid factor is inferred to turn it into one. The range's exact application to the article's GWP result cannot be independently established from the public quantities. The optional low/base/high chart is therefore omitted. For transparency, mechanically applying it to 225.9 would give `225.9 * 0.76 = 171.684` and `225.9 * 1.32 = 298.188` kg CO2e. These would be illustrative scenarios, not measured bounds or a confidence interval, and are not used as chart data.

Both A and C display v1.0, but public detailed pages disclose assumptions not reconciled with the article's carbon characterization. The deck distinguishes **published article estimates** from **current dataset assumptions**. Reproducibility of the article from today's inventory remains an open verification item; it is not valid to silently claim they are a single frozen model snapshot.

The source's TRL/sample timing is an authored model status, not an independent assessment of the actual HBF market as of this meeting. The deck does not claim a current commercial-shipment status.

## Claim-to-source mapping

| Slide / claim | Source / location | Evidence type and limitation |
|---|---|---|
| Cover / topic and identity | User's requested identity; A/D | Meeting metadata, not external scientific claim |
| 17 / common framework and available memory families | D Sec. 4.4; E catalogue | Public methodology and listed dataset coverage |
| 17 / HBF lacks production data | C, Sampling procedure; D Sec. 4.4.4 | Source-declared prospective model |
| 17 / preliminary sensitivity use | A screening-level framing plus our judgment | Intended use, not validation guarantee |
| 18 / stack values and capacity labels | A chart; B listed results; E/F/G/H names | Published model outputs, units retained |
| 18 / 16.7x | Formula above | Our calculation |
| 19 / four normalized bars and 47.8% | A/B inputs plus explicit formula above | Our nominal index, not verified per-GiB comparison |
| 19 / capacity cannot establish serving performance | Methodological limitation of capacity-only index | Does not claim measured bandwidth/latency equivalence |
| 20 / current process, geometry, yield assumptions | C Overview | Model proxies, not vendor manufacturing recipe |
| 20 / die-area/bit-density conflict; package gaps | C Limitations and unquantified flows | Model's own disclosure |
| 20 / omitted package burdens | C Production covered; F boundary | Include in system accounting separately |
| 20 / uncertainty band and caution | D PDF p. 68 / printed p. 66; C | Published band; not validated around A's GWP center |

## Slide 5 figure redesign

Only the `HELIX` frame and its speaker-script section are redesigned from commit `3f90a20`. Original Helix Figure 3 is included at full content width with its aspect ratio and all labels preserved. The local TeX references `../2026-11-04-meeting/Helix/Without-Caption/Helix_Figure_03_System_Overview.png`. Packaging rewrites only this path to `figures/Helix_Figure_03_System_Overview.png` and includes the exact image bytes in the self-contained ZIP. The builder verifies identical text, 3× pixels and link annotations for every other page against that commit. Figure 3 depicts the system overview, while the method line separately describes max-flow/MILP placement and subsequent runtime scheduling.
