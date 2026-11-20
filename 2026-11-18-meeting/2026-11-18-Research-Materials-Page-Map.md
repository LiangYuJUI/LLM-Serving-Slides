# Research Materials page map

Reorganized 2026-11-20 (Asia/Taipei) from the 22-page deck at commit `61bd0a113310`. Earlier baseline: `51548444d0d896c8302ad94a9c81cae3f2ed571d`.

Exactly **20 PDF pages: 14 main + 6 supplementary**. Physical page and footer number agree (1/20–20/20). Thank You is page 14. The REEL and memory-source pages are supplementary, not main chapters. Slides carry no source footers; citations are kept in the speaker script and the evidence register.

| PDF / footer | Label | Previous page (22-page deck) | Topic | Action |
|---|---|---|---|---|
| 1 | `COVER` | 1 | Power- and Carbon-Aware LLM Serving on Heterogeneous GPUs (title and subtitle only) | Preserved |
| 2 | `EINDEX` | 2 | Contents (agenda with four index cards) | Navigation updated; subtitle removed |
| 3 | `GEO` | 3 | Carbon–SLO: Shared State, Regional Decisions | Preserved |
| 4 | `RELATED` | 4 | GreenCache: Carbon-Aware SSD Cache Sizing | Preserved |
| 5 | `HELIX` | 5 | Helix: Heterogeneous GPU Placement | Preserved |
| 6 | `THUNDER` | 6 | ThunderServe: High-performance and Cost-efficient LLM Serving in Cloud Environments | Preserved |
| 7 | `WORKLOAD` | 7 | Different Workloads, Different Resource Requirements | Preserved |
| 8 | `MEMORY` | 9 | HBM and HBF Memory Access Energy | Moved earlier |
| 9 | `PLACEMENT` | 10 | Workload Completion Time Comparison | Moved earlier |
| 10 | `PLACEMENTENERGY` | 11 | Modeled Serving Energy Comparison | Moved earlier |
| 11 | `ACCOUNT` | 8 | Research Gaps and Proposed Direction | Redesigned (three gap cards; no research-question box) |
| 12 | `GEOARCH` | 13 | Proposed Coordinated Scheduling Architecture | Redesigned (global scheduler over two heterogeneous data centers) |
| 13 | `ENVIRONMENT` | 14 and 15 | Experimental Plan and Research Roadmap | Merged from `ENVIRONMENT` and `NEXT` |
| 14 | `THANKYOU` | 16 | Thank You | Moved earlier |
| 15 | `REEL1` | 17 | HBM/HBF Embodied Carbon Evidence | Supplementary, preserved |
| 16 | `REEL2` | 18 | Embodied Carbon per Memory Stack | Supplementary, preserved |
| 17 | `REEL3` | 19 | Embodied Carbon per Nominal Capacity Unit | Supplementary, preserved |
| 18 | `REEL4` | 20 | HBF Carbon Estimate: Assumptions and Limitations | Supplementary, preserved |
| 19 | `REELABOUT` | 21 | REEL LCI: Database Background and Inventory Scope | Supplementary, preserved |
| 20 | `MEMORYSOURCES` | 22 | Sources of the HBM/HBF Memory Parameters | Supplementary, preserved |

Removed frames: `DISAGG` (Proposed Workload-Aware GPU/Memory Placement) and `NEXT` (Research Roadmap and Evaluation Plan). Their retained content lives on pages 11–13 and in the speaker script: the three-phase structure, the fair-comparison baselines, the Dense LLM starting point and the operational-carbon-first scope. HBM/HBF-specific placement decisions and HBM/HBF co-design were dropped from the proposal.

## Navigation

- Index cards: `GEO` (Previous Work and Research Background) → 3, `WORKLOAD` (Workload and Resource Characteristics) → 7, `ACCOUNT` (Research Gaps and Proposed Direction) → 11, `ENVIRONMENT` (Experimental Plan and Roadmap) → 13.
- Memory provenance round trip: `MEMORY` (8) ↔ `MEMORYSOURCES` (20).
- REEL background round trip: `REEL1` (15) ↔ `REELABOUT` (19).

## Research direction

Pages 11–13 propose coordinated, workload-aware heterogeneous GPU scheduling for lower serving energy and operational carbon under latency SLOs. Page 11 contrasts what Carbon–SLO, GreenCache, Helix and ThunderServe provide with the opportunity. Page 12 is a conceptual architecture. Page 13 is the experimental plan on the RCITI GPU cluster and LLMServingSim 2.0. All of it is proposed, not implemented or evaluated, and novelty relative to related work such as GreenLLM remains to be established.

## HBM/HBF evidence

Pages 8–10 and the supplementary pages keep the published HBM/HBF evidence with its values, assumptions and caveats unchanged. These are published simulation and model results, not our measurements, and they do not commit this research to HBF. HBM/HBF is not part of the agenda or the proposed architecture.

Existing historical Notion exports are snapshots. Use this page map and the revised speaker script for current narration.
