# Backup map for the 10-minute review

Formal slides stay pages 1–12, with footer `n/12`. Appendix starts at page 13 and does not reset the frame counter, so hyperlink destinations stay unique. Backup frames are `plain`: the old 21 Oct footer is covered by a 0.50 cm Paper band, and the new band holds `Backup k/27`, Previous / Next (inside a topic), Return to Review, and Backup Topics.

Compile from `2026-10-28-meeting/` with pdfLaTeX, twice. Source PDFs are included by page, not redrawn:

- ThunderServe: `../2026-10-21-meeting/output/pdf/2026-10-21-ThunderServe.pdf` (44 pages)
- Hetis: `../2026-10-21-meeting/output/pdf/2026-10-21-Hetis.pdf` (39 pages)

If those paths are missing, the deck uses `Backup/source/` instead. The Overleaf zip carries the two PDFs there.

Total PDF: **40 pages** = 12 formal + 1 index + 27 included slides.

## Topics

Old page numbers were checked against the 21 Oct PDFs (1-based). A topic’s formal-slide links all open its first label. Return is one destination per topic.

| Topic ID | Name | Slides | New PDF | Label | Source page | Source title | Return |
|---|---|---|---|---|---|---|---|
| `ts_phase` | GPU phase characteristics and network heterogeneity | 2 | 14–15 | `backup_ts_phase_01` | TS 4 | Different GPUs Favor Different Inference Phases | `main_ts_why` (p.3) |
| | | | 15 | `backup_ts_phase_02` | TS 6 | Cloud Networking Is Highly Heterogeneous | same |
| `ts_tabu` | Hierarchical scheduling and Tabu Search operations | 2 | 16–17 | `backup_ts_tabu_01` | TS 10 | Scheduling as Two-Level Hierarchical Optimization | `main_ts_joint` (p.4) |
| | | | 17 | `backup_ts_tabu_02` | TS 12 | Four Neighbor Operations in Tabu Search | same |
| `ts_parallel` | TP/PP configuration | 1 | 18 | `backup_ts_parallel_01` | TS 15 | Deducing Parallel Configurations for Each Group | `main_ts_joint` (p.4) |
| `ts_kv` | Replica routing, KV transfer, network-aware placement | 4 | 19–22 | `backup_ts_kv_01` | TS 18 | Orchestrating Prefill and Decode Replicas | `main_ts_joint` (p.4) |
| | | | 20 | `backup_ts_kv_02` | TS 19 | Modeling KV Cache Communication Cost | same |
| | | | 21 | `backup_ts_kv_03` | TS 21 | Network-Aware Deployment Plans | same |
| | | | 22 | `backup_ts_kv_04` | TS 22 | Request-Time Breakdown in Table 5 | same |
| `ts_rescheduling` | Lightweight rescheduling | 1 | 23 | `backup_ts_rescheduling_01` | TS 25 | Lightweight Re-scheduling in Real Time | `main_ts_close` (p.6) |
| `ts_compression` | KV cache compression | 1 | 24 | `backup_ts_compression_01` | TS 27 | Quantize KV Cache for Communication Only | `main_ts_joint` (p.4) |
| `ts_results` | Throughput and deployment configuration | 2 | 25–26 | `backup_ts_results_01` | TS 35 | End-to-End System Throughput | `main_ts_results` (p.5) |
| | | | 26 | `backup_ts_results_02` | TS 37 | Full Deployment Plans from Table 3 | same |
| `ts_simulation` | Simulator and communication-model accuracy | 1 | 27 | `backup_ts_simulation_01` | TS 41 | Simulator and Alpha-Beta Model Accuracy | `main_ts_results` (p.5) |
| `hetis_motivation` | KV underutilization and module-dependent GPU performance | 2 | 28–29 | `backup_hetis_motivation_01` | Hetis 3 | Coarse Splitting Wastes KV Cache Capacity | `main_hetis_why` (p.7) |
| | | | 29 | `backup_hetis_motivation_02` | Hetis 5 | MLP and Attention Scale Differently | same |
| `hetis_workers` | Primary workers, attention workers, system architecture | 2 | 30–31 | `backup_hetis_workers_01` | Hetis 6 | Primary Workers and Attention Workers | `main_hetis_arch` (p.8) |
| | | | 31 | `backup_hetis_workers_02` | Hetis 7 | Hetis System Architecture | same |
| `hetis_headwise` | Head-wise attention, dynamic allocation, GQA | 3 | 32–34 | `backup_hetis_headwise_01` | Hetis 10 | Why Split Attention by Head? | `main_hetis_arch` (p.8) |
| | | | 33 | `backup_hetis_headwise_02` | Hetis 12 | Dynamic Attention Placement Across Requests | same |
| | | | 34 | `backup_hetis_headwise_03` | Hetis 13 | Head Integrity and Grouped-Query Attention | same |
| `hetis_migration` | Re-dispatching, head-level KV, migration | 3 | 35–37 | `backup_hetis_migration_01` | Hetis 20 | Re-dispatching to Balance Computation | `main_hetis_close` (p.10) |
| | | | 36 | `backup_hetis_migration_02` | Hetis 22 | Head-Level KV Management and Migration | same |
| | | | 37 | `backup_hetis_migration_03` | Hetis 31 | Dynamic Head and Cache Allocation | same |
| `hetis_results` | Llama-70B results and usable KV cache | 2 | 38–39 | `backup_hetis_results_01` | Hetis 27 | Llama-70B: GQA End-to-End Results | `main_hetis_results` (p.9) |
| | | | 39 | `backup_hetis_results_02` | Hetis 28 | Maximum Usable KV Cache Space | same |
| `hetis_hbf` | Implications for HBM/HBF co-design | 1 | 40 | `backup_hetis_hbf_01` | Hetis 38 | Implications for GPU + HBM / HBF Co-design | `main_hetis_close` (p.10) |

Page 13 is `backup_index` (Backup Topics). It links to every `*_01` label and back to `main_thanks` (page 12).

## Formal-slide keywords

Links use AccentBlue on existing words. `\smalllabel` is not used as a link target because it expands `\MakeUppercase`.

| PDF page | Frame label | Keyword | Destination |
|---|---|---|---|
| 3 | `main_ts_why` | Prefill | `backup_ts_phase_01` |
| 3 | | Decode | `backup_ts_phase_01` |
| 3 | | network bandwidth | `backup_ts_phase_01` |
| 3 | | KV cache transfer | `backup_ts_kv_01` |
| 4 | `main_ts_joint` | TABU SEARCH | `backup_ts_tabu_01` |
| 4 | | GPU group construction | `backup_ts_tabu_01` |
| 4 | | TP / PP configuration | `backup_ts_parallel_01` |
| 4 | | request routing | `backup_ts_kv_01` |
| 4 | | KV cache transfer | `backup_ts_kv_01` |
| 4 | | KV cache compression | `backup_ts_compression_01` |
| 4 | | lightweight rescheduling | `backup_ts_rescheduling_01` |
| 5 | `main_ts_results` | Workload-aware deployment | `backup_ts_results_01` |
| 5 | | FIGURE 9 | `backup_ts_results_01` |
| 5 | | throughput (takeaway) | `backup_ts_results_01` |
| 6 | `main_ts_close` | lightweight | `backup_ts_rescheduling_01` |
| 6 | | Lightweight | `backup_ts_rescheduling_01` |
| 7 | `main_hetis_why` | MLP | `backup_hetis_motivation_01` |
| 7 | | attention | `backup_hetis_motivation_01` |
| 7 | | KV-cache | `backup_hetis_motivation_01` |
| 8 | `main_hetis_arch` | PRIMARY WORKERS | `backup_hetis_workers_01` |
| 8 | | ATTENTION WORKERS | `backup_hetis_workers_01` |
| 8 | | PER-LAYER DECODE TRAFFIC | `backup_hetis_headwise_01` |
| 8 | | head granularity | `backup_hetis_headwise_01` |
| 9 | `main_hetis_results` | Llama-70B | `backup_hetis_results_01` |
| 9 | | throughput | `backup_hetis_results_01` |
| 9 | | KV cache | `backup_hetis_results_01` |
| 10 | `main_hetis_close` | Online adaptation | `backup_hetis_migration_01` |
| 10 | | Dispatcher | `backup_hetis_migration_01` |
| 10 | | Hauler | `backup_hetis_migration_01` |
| 10 | | KV cache | `backup_hetis_migration_01` |
| 11 | `main_compare` | KV cache (diagram) | `backup_ts_kv_01` |
| 11 | | memory use | `backup_hetis_results_01` |
| 11 | | phase-level | `backup_ts_phase_01` |
| 11 | | head-level | `backup_hetis_headwise_01` |
| 12 | `main_thanks` | Backup topics | `backup_index` |

`ts_simulation` and `hetis_hbf` have no formal-slide keyword. Open them from Backup Topics. The vLLM URL on page 10 stays an external link.

## Paths to rehearse

- Page 4 Tabu Search → page 16 → Next (page 17) → Return to Review (page 4).
- Page 3 or 4 KV transfer → page 19 → Next through page 22 → Return to Review (page 4).
- Page 8 head granularity, or page 11 head-level → page 32 → Next through page 34 → Return to Review (page 8).
- Page 10 Dispatcher / Hauler / KV cache → page 35 → Next through page 37 → Return to Review (page 10).
- Page 11 phase-level, KV cache, head-level, or memory use → the shared backup above → Return.
- Page 12 Backup topics → page 13 → any topic → Return, or Backup Topics back to the index.

GoTo annotations are in the PDF. A viewer that only paints pages and ignores internal links (some browser and GitHub previews) will not follow them. Preview, Acrobat, and PyMuPDF resolve them.

## Adding or swapping a backup page

1. Check the old PDF page in a viewer. Do not trust a frame count alone.
2. Add a `plain` frame with a new label in `backup-frames.tex`, next to the other frames of that topic. Keep one topic contiguous.
3. Point `\backupcanvas` at the source page. Set Previous / Next only inside the topic, Return to the frame label in the table, and Backup Topics to `backup_index`.
4. Renumber the `Backup k/27` badges and this table’s new-PDF pages.
5. Add the index line in `backup-index.tex`.
6. Run `python3 scripts/verify_backup_links.py` after two pdfLaTeX passes. Pass `--baseline` if you still have the pre-backup 12-page PDF and want the visual check.
