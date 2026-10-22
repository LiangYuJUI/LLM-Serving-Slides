# HBF sources, figure mapping, and QA

Verified on 2026-10-22. The deck is an independent nine-slide paper summary (eight main slides plus one source map after the conclusion).

## Source provenance

- Paper: [HBF Sucks? A Full-Stack Characterization of High-Bandwidth Flash for KV-Centric LLM Serving, arXiv:2608.11668v4](https://arxiv.org/abs/2608.11668v4).
- Download: https://arxiv.org/pdf/2608.11668v4
- Preserved as `../Arxiv26_HBF_v4.pdf`. No HBF PDF was present at task start.
- The supplied six PNGs do **not** match Figures 1–6 in this version. Their own embedded captions were inspected individually. Their originating paper/version remains unverified.
- Numerical narrative is restricted to the supplied task facts. New evidence images are direct crops from the retrieved paper, not redrawn charts. Original axes, legends, and panel labels are preserved. Figure captions are replaced by readable source labels in the deck.

## Supplied image mapping (all unchanged)

| Supplied PNG suffix | Number visible in caption | Actual content | Claim supported by that image | Used in deck |
|---|---|---|---|---|
| Fig01 | Figure 1 | H100 / Llama 3.1 8B simulator vs. profiled vLLM throughput | Simulator validation with host KV offload disabled | No; does not establish any C1–C3 result |
| Fig02 | Figure 2 | Shared-site Sandisk layout vs. sequential H³ HBM/HBF layout | Two possible memory organizations | No; cannot identify these as the requested HBF-1/HBF-2 roadmap pair |
| Fig03 | Figure 3 | Host, HBF, HBM hierarchy for weights, activations and KV | Hot/cold hierarchical placement | No; would add unneeded mechanism detail and a different H³ buffer context |
| Fig04 | Figure 4 | Vanilla cache-aware scheduling across two steps | Eviction can lose a future prefix hit | No; not the requested latency experiment |
| Fig05 | Figure 5 | Buffered cache-aware scheduling | A buffer can preserve a future hit | No; would misrepresent this characterization as a new runtime proposal |
| Fig06 | Figure 6 | GLM-5.2 completion time vs. modeled energy, 1× and 5× traces | Placement/parallelism energy-time tradeoff | No; not thermal/endurance or the requested SSD comparison |

## Verified evidence used

| Asset | Paper location | Slide | Notes |
|---|---|---|---|
| HBF_Figure04.png | Figure 4, PDF p. 7 | 5 | Full three-panel experiment; median matched pairs differ from the mean E2E range in the text |
| HBF_Table08.png | Table 8, PDF p. 9 | 6 | Original table, full row/column labels |
| HBF_Figure10a.png | Figure 10(a), PDF p. 11 | 7 | Only the complete temperature/bandwidth panel; (b)/(c) excluded, no axes cropped |
| HBF_Figure12.png | Figure 12, PDF p. 12 | 8 | Conceptual map, not a calibrated numerical decision boundary |

Figure 11 is summarized as text on slide 7, with its source stated. The 48–140 TB/day and 0.56× values come from the task and are verified in Section 8.2.

## Experimental-slide review

| Slide | Claim | Evidence and baseline | Takeaway |
|---|---|---|---|
| 5 / C1 | Faster HBF barely improves E2E latency | Mean E2E is 2–5.5× capacity-matched SSD; 3.75× faster media yields only 0.75% / 0.88% lower E2E relative to each slower-media setting; exposed I/O ≈ 1% | Near-tier admission and queueing dominate, not flash latency |
| 6 / C2 | Every production trace writes more than it reads | Write/read bytes = 2.14×, 4.90×, 1.14×, 2.20×; all above equal-traffic baseline 1× | Hierarchy retains hot reuse and exports cold writes |
| 7 / C3 | Write-heavy traffic makes peak bandwidth unsustainable | 16-Hi TLC model reaches 80°C at ≈202.27 GB/s; 48–140 TB/day writes; projected lifetime ≈0.56× capacity-matched SSD | Thermal throttling and long-term wear are separate costs |

## Review limitations

- The supplied PNGs' original source/version needs human identification only if those specific images must be reused. The deck now uses the verified target paper instead.
- Oral duration is a pacing estimate; rehearse the Chinese script to confirm the presenter's speed.
- The Figure 4 media-sweep panel and Section 6.1 use different summaries. The deck keeps the paper image intact and explicitly attributes the required 0.75% / 0.88% mean E2E numbers to the text; do not read them as labels from that panel.
- No commit or push was performed.


## Source-map update

Slide 9, **Sources Behind the HBF Evaluation**, groups seven sources into system/workload, HBF definition, and physical limits. Full references and all eight clickable URLs (including the HBF code branch) appear in `../HBF_scripts.md` under page 09. OCP v0.7.0 and KAIST roadmap dates remain those cited by the paper. The official OCP Storage contributions page lists v0.7.0; the KAIST lab homepage provides its HBF roadmap download. The HBF GitHub branch was confirmed through the GitHub connector. HAVEN, USENIX, 3D-ICE and KIOXIA official URLs were checked. The old OCP wiki URL was inaccessible and is not used.

The slide separates the paper's chosen 80°C policy and TLC endurance budget from external source specifications. No physical HBF measurement is claimed. Latest QA: nine PDF pages and nine script sections; two-pass pdfLaTeX build without warnings or overfull boxes; all eight page-9 hyperlink rectangles lie within the page. Page 9 was rendered and visually reviewed.
