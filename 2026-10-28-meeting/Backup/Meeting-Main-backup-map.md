# Meeting-Main backup map

Formal slides are pages 1–13. Footer stays `Main n/13`. Page 14 is Backup Topics. Pages 15–52 are the 38 detail slides, numbered `Backup k/38` in the footer. Previous / Next stay inside one topic. Return to Main uses the page in the table. Backup Topics returns to page 14.

Compile from `2026-10-28-meeting/` with pdfLaTeX, twice. Reference-deck pages are included with `graphicx`, not redrawn:

- `output/pdf/2026-10-28-Helix.pdf`
- `output/pdf/2026-10-28-Tessera.pdf`

If those paths are missing, the deck uses `Backup/source/`. The Overleaf zip carries both PDFs there.

Do not edit `Backup/backup-index.tex` or `Backup/backup-frames.tex`. Those belong to the 10-minute review.

## Topics

| Topic | Slides | PDF | First label | Return | What it is |
|---|---|---|---|---|---|
| Max-flow graph | 2 | 15–16 | `mm_hx_maxflow_01` | p.4 | Native: graph, then why max flow is throughput |
| Compute capacity | 1 | 17 | `mm_hx_compute_01` | p.3 | Native |
| Network capacity | 1 | 18 | `mm_hx_network_01` | p.3 | Native |
| MILP placement | 3 | 19–21 | `mm_hx_milp_01` | p.4 | Native: variables, placement/memory, flow |
| Network constraints | 1 | 22 | `mm_hx_netcon_01` | p.6 | Native connectivity constraints |
| Runtime scheduling | 1 | 23 | `mm_hx_iwrr_01` | p.4 | Native IWRR |
| Pipeline scheduling | 1 | 24 | `mm_hx_pipe_01` | p.4 | Native per-request pipeline |
| High GPU heterogeneity | 1 | 25 | `mm_hx_hetero_01` | p.5 | Native Fig. 8. Not the geo-distributed run |
| MILP solver ablation | 2 | 26–27 | `mm_hx_milpabl_01` | p.7 | Native ablation, then solver quality |
| Evaluation setup | 1 | 28 | `mm_hx_eval_01` | p.5 | Helix reference p.26 |
| Workload characteristics | 1 | 29 | `mm_hx_work_01` | p.5 | Helix reference p.27 |
| Single-cluster results | 1 | 30 | `mm_hx_single_01` | p.5 | Helix reference p.28, Fig. 6 |
| Geo-distributed results | 1 | 31 | `mm_hx_geo_01` | p.6 | Helix reference p.29, Fig. 7 |
| Placement deep dive | 1 | 32 | `mm_hx_place_01` | p.7 | Helix reference p.31, Fig. 9 |
| Scheduling deep dive | 1 | 33 | `mm_hx_scheddeep_01` | p.7 | Helix reference p.32, Fig. 10 |
| Kernel GPU preference | 1 | 34 | `mm_ts_kern_01` | p.8 | Tessera reference p.6 |
| Phase labels | 1 | 35 | `mm_ts_phase_01` | p.8 | Tessera reference p.7 |
| PTX instrumentation | 1 | 36 | `mm_ts_ptx_01` | p.9 | Native. No formal-slide keyword; open from the index |
| RAW and DDG | 2 | 37–38 | `mm_ts_raw_01` | p.9 | Native RAW, then cross-iteration KV |
| Offline MILP | 2 | 39–40 | `mm_ts_plan_01` | p.9 | Native throughput MILP, then communication constraints |
| Latency-oriented policy | 1 | 41 | `mm_ts_lat_01` | p.9 | Native formulation, not the online figure |
| GPU workers | 1 | 42 | `mm_ts_worker_01` | p.9 | Native. Also the CUDA-stream link on p.12 |
| Monitor and policy switch | 2 | 43–44 | `mm_ts_mon_01` | p.9 | Native monitor, then sensitivity. p.11 opens the first page |
| Network bandwidth | 1 | 45 | `mm_ts_net_01` | p.12 | Native |
| Cost efficiency | 1 | 46 | `mm_ts_cost_01` | p.10 | Native. Index only |
| Model families | 1 | 47 | `mm_ts_gen_01` | p.10 | Native. Index only |
| Communication backends | 1 | 48 | `mm_ts_backend_01` | p.12 | Tessera reference p.25 |
| Evaluation setup | 1 | 49 | `mm_ts_eval_01` | p.10 | Tessera reference p.26. PD/AF and Poisson |
| Offline throughput | 1 | 50 | `mm_ts_off_01` | p.10 | Tessera reference p.27, Fig. 6 |
| Online latency | 1 | 51 | `mm_ts_on_01` | p.11 | Tessera reference p.28, Fig. 7 |
| Pipeline effectiveness | 1 | 52 | `mm_ts_pipe_01` | p.12 | Tessera reference p.30, Fig. 9 |

## Formal-slide keywords

| Page | Keyword | Opens |
|---|---|---|
| 2 | Layer placement, MILP placement | `mm_hx_milp_01` |
| 2 | request pipeline | `mm_hx_pipe_01` |
| 2 | GPU kernel | `mm_ts_kern_01` |
| 2 | DDG | `mm_ts_raw_01` |
| 2 | MILP (Tessera cell) | `mm_ts_plan_01` |
| 2 | Request path scheduling | `mm_hx_iwrr_01` |
| 3 | geo-distributed | `mm_hx_geo_01` |
| 3 | compute | `mm_hx_compute_01` |
| 3 | link bandwidth | `mm_hx_network_01` |
| 4 | Offline planning, MILP | `mm_hx_milp_01` |
| 4 | flow graph, Max-flow | `mm_hx_maxflow_01` |
| 4 | Online runtime | `mm_hx_iwrr_01` |
| 4 | pipeline | `mm_hx_pipe_01` |
| 5 | Prototype | `mm_hx_eval_01` |
| 5 | Offline workload, Online workload | `mm_hx_work_01` |
| 5 | throughput | `mm_hx_single_01` |
| 6 | inter-cluster network | `mm_hx_netcon_01` |
| 6 | Simulator | `mm_hx_eval_01` |
| 6 | clusters | `mm_hx_geo_01` |
| 7 | Placement ablation | `mm_hx_place_01` |
| 7 | Scheduling ablation | `mm_hx_scheddeep_01` |
| 8 | A100 | `mm_ts_kern_01` |
| 8 | phase label | `mm_ts_phase_01` |
| 9 | RAW, DDGs | `mm_ts_raw_01` |
| 9 | MILP | `mm_ts_plan_01` |
| 9 | workers | `mm_ts_worker_01` |
| 9 | monitor | `mm_ts_mon_01` |
| 10 | offline | `mm_ts_off_01` |
| 10 | PD, AF | `mm_ts_eval_01` |
| 11 | Poisson | `mm_ts_eval_01` |
| 11 | SLO | `mm_ts_on_01` |
| 11 | Stored policies | `mm_ts_mon_01` |
| 12 | transfers | `mm_ts_net_01` |
| 12 | pipelining | `mm_ts_pipe_01` |
| 12 | CUDA stream priority | `mm_ts_worker_01` |
| 13 | Layers | `mm_hx_milp_01` |
| 13 | request pipeline | `mm_hx_pipe_01` |
| 13 | GPU kernels | `mm_ts_kern_01` |
| 13 | Backup Topics (footer) | `mm_backup_index` |

The opening line of formal page 8 (`GPU-kernel granularity`) and the question line of formal page 11 sit under the title bar in the already-shipped deck, so those words are not the clickable copies. The visible links are A100 on page 8 and SLO on page 11.

## Adding a page

1. Confirm the source page in the reference PDF.
2. Add one `plain` frame next to its topic in `Meeting-Main-backup-frames.tex`, or one native frame with `\bnav` and a unique `mm_` label.
3. Keep Previous / Next inside the topic. Point Return to Main at one formal label.
4. Renumber `Backup k/38`, this table, `Meeting-Main_scripts.md`, and `scripts/verify_meeting_main_links.py`.
5. Run `python3 scripts/verify_meeting_main_links.py --baseline <old.pdf>` after two pdfLaTeX passes.
