# Research Materials page map

Simplified 2026-11-20 (Asia/Taipei) from the 20-page deck at commit `a280f04d21` (itself reorganized from the 22-page deck at `61bd0a113310`). Earlier baseline: `51548444d0d896c8302ad94a9c81cae3f2ed571d`.

Exactly **19 PDF pages: 13 main + 6 supplementary**. Physical page and footer number agree (1/19–19/19). Thank You is page 13. The REEL and memory-source pages are supplementary, not main chapters. Slides carry no source footers; citations are kept in the speaker script and the evidence register.

| PDF / footer | Label | Previous page (20-page deck) | Topic | Action |
|---|---|---|---|---|
| 1 | `COVER` | 1 | Power- and Carbon-Aware LLM Serving on Heterogeneous GPUs (title and subtitle only) | Preserved |
| 2 | `EINDEX` | 2 | Contents (four index cards, no subtitle or takeaway) | Card 4 retargeted to Experimental Environment |
| 3 | `GEO` | 3 | Carbon–SLO: Shared State, Regional Decisions | Preserved |
| 4 | `RELATED` | 4 | GreenCache: Carbon-Aware SSD Cache Sizing | Preserved |
| 5 | `HELIX` | 5 | Helix: Heterogeneous GPU Placement | Preserved |
| 6 | `THUNDER` | 6 | ThunderServe: High-performance and Cost-efficient LLM Serving in Cloud Environments | Preserved |
| 7 | `WORKLOAD` | 7 | Different Workloads, Different Resource Requirements | Preserved |
| 8 | `MEMORY` | 8 | HBM and HBF Memory Access Energy | Preserved |
| 9 | `PLACEMENT` | 9 | Workload Completion Time Comparison | Preserved |
| 10 | `PLACEMENTENERGY` | 10 | Modeled Serving Energy Comparison | Preserved |
| 11 | `ACCOUNT` | 11 | Research Gaps and Proposed Direction | Preserved |
| 12 | `ENVIRONMENT` | 13 | Experimental Environment: LLMServingSim 2.0 and Real GPU Profiling | Rewritten (replaces the plan/roadmap slide; GEOARCH removed) |
| 13 | `THANKYOU` | 14 | Thank You | Preserved |
| 14 | `REEL1` | 15 | HBM/HBF Embodied Carbon Evidence | Supplementary, preserved |
| 15 | `REEL2` | 16 | Embodied Carbon per Memory Stack | Supplementary, preserved |
| 16 | `REEL3` | 17 | Embodied Carbon per Nominal Capacity Unit | Supplementary, preserved |
| 17 | `REEL4` | 18 | HBF Carbon Estimate: Assumptions and Limitations | Supplementary, preserved |
| 18 | `REELABOUT` | 19 | REEL LCI: Database Background and Inventory Scope | Supplementary, preserved |
| 19 | `MEMORYSOURCES` | 20 | Sources of the HBM/HBF Memory Parameters | Supplementary, preserved |

Removed frames: `GEOARCH` (Proposed Coordinated Scheduling Architecture, previously page 12), together with the old plan/roadmap content of `ENVIRONMENT` (previous page 13: Phase 1–3 and GPU-inventory text). No scheduling architecture, research phases or evaluation roadmap appear anywhere in the main presentation, and none were moved to the supplements. Earlier removals: `DISAGG` and `NEXT`.

## Navigation

- Index cards: `GEO` (Previous Work and Research Background) → 3, `WORKLOAD` (Workload and Resource Characteristics) → 7, `ACCOUNT` (Research Gaps and Proposed Direction) → 11, `ENVIRONMENT` (Experimental Environment) → 12. Each card is clickable across its full width.
- Memory provenance round trip: `MEMORY` (8) ↔ `MEMORYSOURCES` (19).
- REEL background round trip: `REEL1` (14) ↔ `REELABOUT` (18).

## Experimental environment (page 12)

Upper section: LLMServingSim 2.0 as a profile-driven simulator for heterogeneous and disaggregated LLM serving (hardware and network modeling with ASTRA-Sim; multi-instance serving with configurable request routing, TP/PP parallelism, batching and KV-cache management). Power/energy modeling depends on hardware-specific profiles, configured parameters and validation. Lower section: planned real GPU profiling on the Academia Sinica CITI GPU Cluster. A Profiling and Validation separator links the two. No GPU models, counts, topology, benchmark results or completed measurements are claimed, and no coordinated multi-DC carbon-aware capability is attributed to the simulator. Details checked against the official documentation (llmservingsim.ai, the overview, power-model and CLI-flag pages, and the GitHub README).

## HBM/HBF evidence

Pages 8–10 and the supplementary pages keep the published HBM/HBF evidence with its values, assumptions and caveats unchanged. These are published simulation and model results, not our measurements, and they do not commit this research to HBF.

Existing historical Notion exports are snapshots. Use this page map and the revised speaker script for current narration.
