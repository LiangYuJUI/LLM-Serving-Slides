# Research Direction validation

Reviewed 2026-11-09 for the 2026-11-11 meeting. **PASS**.

- Git HEAD: `96881bc80eff943d05056844550029e6451c9f5e`.
- Exactly **7 PDF pages: an unnumbered cover plus 6 content slides**, 16:9, independent footers **1/6 through 6/6**.
- pdfLaTeX: two passes for local source and two passes for ZIP extracted into a clean temporary directory.
- Final logs: **no overfull/underfull boxes, undefined references, missing-character/font/graphics warnings, or other warnings**.
- Extracted ZIP matches local PDF in page text, rendered pixels and external hyperlink geometry/targets.
- Text bounds checked on every page. All fonts embedded (Latin Modern Type 1). No external graphics required.
- No inherited internal frame references, Discussion Index, Main/Backup division or appendix.
- Slide 5 announces MemExplorer for **November 18, 2026**, as a separate next-week presentation.
- Slide 6 is the final comparison matrix, with **13 entries**, five requested columns and the complete Notion link.
- `git diff --check` passes. No commit or remote push performed.

## Visual review

The new cover was visually inspected; the original six content pages are pixel-identical to the previously inspected PDF. Earlier overflowing layouts were corrected before delivery. The final architecture slide was re-rendered and re-inspected after fixing a Beamer parsing issue that had consumed its initial hypothesis label as an unused subtitle. A content check now requires that label in the PDF.

| Content slide (PDF page = slide + 1) | Visual and semantic check |
|---|---|
| 1 | Three dimensions, metrics and explicit proposal status visible; duplicate cover metadata removed; footer 1/6 |
| 2 | Four data classes readable, candidate placement distinct from evidence, no automatic power-saving claim |
| 3 | Both worker groups and direction labels readable, explicit hypothesis label visible, no KV/weight shuttle implication, costs and baselines present |
| 4 | Completed and future work separated, modeled TPOT example qualified, double-counting warning fully visible |
| 5 | Three RQs, six baselines, metrics and complete next-week paper title visible |
| 6 | Thirteen entries readable at 7.5 pt native size; no table scaling; all uncertainty/metric distinctions and source link visible |

The whole-deck montage is `research-direction-montage.png`; full page renders are in `research-direction-pages/`. The dense matrix is intended as a guided comparison during a one-minute explanation, with the full matrix linked for detailed reading.

## Preservation

The pre-edit hash snapshot contained **111 existing files** under the meeting directory. All **110 files other than README.md remain byte-identical**, including GreenCache source, figures, scripts, 48-page PDF, ZIP and QA outputs. README.md begins with its exact HEAD contents and only appends the distinct Research Direction section. No GreenCache rebuild was run. Evidence: `research-direction-preservation.json`.

## Source limitations

The complete requested Notion §5.3 matrix was fetched. Classifications follow that source, not a new full-paper audit of all 13 works. Hetis, Tessera and Janus retain **Needs verification** for standalone simulator form; `Not shown` is not a definitive negative for geo-WAN capability. Some rows list evaluation metrics, explicitly marked with an asterisk, rather than claiming an optimization objective.

The 1.261 / 7.342 ms TPOT values and workload configuration were checked against Notion §§4.2–4.3. Raw Oak receipts were not re-fetched and experiments were not rerun. The slide labels this as a documented model result, not physical HBF GPU data or MoE energy evidence. Deployment status and simulator integration details follow the same research record. The ServeLoop web fetch timed out; its documented role was retained with provenance.

MemExplorer's heterogeneous memory and A/FFN coverage was independently checked in its v2 full text, Table I and §V-E / Fig. 8. Janus's A/E pool scope was checked in its abstract. Exact novelty differences and remaining model limitations are explicitly left for the separate next-week review.

## Reproduction

Dependencies: pdfLaTeX, Python 3, `pymupdf`, `Pillow`. The system Python lacked PyMuPDF, so QA used an isolated `/tmp/research-direction-venv`; no repository environment was changed. Run:

```bash
python3 2026-11-11-meeting/scripts/build_research_direction.py
```

Build outputs and hashes are in `research-direction-build.json`. The script preserves the existing GreenCache workflow and checks clean-ZIP parity on every run. Visual review must still accompany substantive content changes.

## Independent cover revision

Added at user request. Cover has no page number; original content retains 1/6–6/6. All six original pages match the pre-cover PDF pixel-for-pixel. Updated PDF, ZIP, montage, page images and documentation. Local and clean-ZIP builds pass with zero warnings; seven-page text/pixel/link parity passes. GreenCache remains unchanged.

Cover updated with Advisor: Hsiang-Yun Cheng, matching the existing GreenCache cover. Visually inspected; local and extracted-ZIP builds pass without warnings. All six content pages remain pixel-identical.

PDF page 2 revision: removed the repeated presentation title, presenter and meeting date. Rebalanced vertical spacing and visually inspected. All other pages remain pixel-identical to the preceding version. Both builds pass without warnings.

Metrics/layout revision: PDF page 2 now has three stacked horizontal rows and a six-row metric-name/unit table including operational carbon per output token. Visually inspected with no clipping. Local and clean-ZIP builds pass with zero warnings. All six other PDF pages remain pixel-identical to the preceding version.

Research-goal wording updated on PDF page 2 to cross-data-center power and carbon reductions. Visual inspection passed; local and clean-ZIP compilation passed with no warnings. Seven PDF pages retained.

Cleanup revision: removed architecture Compare line and per-slide Sources footnotes; retained final full-matrix link. Inspected the complete updated montage. Local and clean-ZIP builds pass with zero warnings and matching text, pixels and links; seven PDF pages retained. Historical source-line review notes above refer to earlier versions.

Simulator slide cleanup: all requested blocks removed. Three simulators are stacked horizontally from top to bottom. Visually inspected PDF page 5. Both builds pass without warnings; all other PDF pages are pixel-identical to the preceding version.
