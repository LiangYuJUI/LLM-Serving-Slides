# Visual and scientific QA — final Main–Backup alignment

## Baseline and scope

Baseline and fetched origin/main: `dfd9923a09d2b68ffb83df3f48745a8b200f6fa0`. Initial working tree was clean. Only `2026-11-11-meeting/` changed. The final deck retains 19 Main slides, 1 Discussion Index, and 28 Backup slides: 48 pages, original frame order and labels.

## Final navigation and semantic review

- 280 internal PDF links, 0 broken destinations, 0 overlapping click rectangles. Destinations match frame-derived pages. No fixed link-count acceptance condition.
- 46 clickable Main → Backup entries form 36 distinct pairs. Every entry has a visible return to its source Main. All 28 backups retain a numbered primary Back to Main and a body Discussion Index button.
- Shared Backup shortcuts now say Main N (topic). The index explicitly says Go to Conclusion (M19). Existing valid cross-links remain.
- M09 links to B13 / B25 as task-specific extensions of Eq. (7). M10 → B13 is the Eq. (8) hypothetical worked example; M11 → B25 is the Eq. (9) hypothetical worked example. These are not paper measurements or independent Eq. (7) experiments.
- M11 → B27 remains workload/Zipf background distinct from B25 scoring. M12 → B26 is full Table 3; M12 → B27 explains the workload used by its representative result. M13 → B14 covers measurement; M14 → B11 / B27 covers SLO thresholds and workloads.
- M18 → B09 says Capacity Profiling (Background). B09 names Fig. 11 as profiling background and points out that the Fig. 15 ablation is on M18. No ablation page was added.
- M12 labels the policy LCS (GreenCache). M19 → B23 says Limits / Our Future Work. The remaining “ours/our” wording correctly identifies our research direction. Original figure wording is untouched.
- M06 has both Solver Time → B18 and Resize Interval → B20. B19, B21, B22 remain accessible through Index/Backup navigation. B02–B05 also have no direct Main entry. No page is unreachable, and none of these is exclusively reachable from Index alone.
- `navigation-audit.md` lists every entry, source question, target evidence, direct/background relation and primary/other returns. `scripts/navigation-contracts.json` is a human-reviewed semantic contract checked against actual PDF annotations and visible text; it does not claim automated scientific understanding.

## Build and preservation

- Local pdfLaTeX: two passes. Independently extracted Overleaf ZIP: two passes. Both final logs have zero Overfull, Underfull, undefined-reference or LaTeX warnings.
- All 48 pages match across builds in text, rendered pixels, hyperlink destinations, annotation rectangles and annotation text. `build-validation.json` records SHA-256 of source, PDF and ZIP; `validation.json` embeds that report and rejects stale builds.
- All 20 supplied figure RGB pixel hashes equal the Git baseline and the embedded PDF images match the sources. Original figures, captions and source credits remain.
- All math expressions, including Eq. (6)–(9), are byte-identical to baseline. Full Table 3 retains all 45 independently checked values on B26 / PDF 48.
- Baseline comparison: 28 pages are pixel-identical. Changed pages are 6, 9–12, 18–20, 27–28, 30–35, 45–48, exactly the navigation/label changes. `baseline-preservation.json` records this comparison.

## Visual QA

Regenerated all 48 page PNGs, both montages, and `navigation-review.png` with the 15 required review pages. Inspected all changed pages at full rendered size: M06, M09, M10, M11, M12, M18, M19, Index, B06, B07, B09, B10, B11, B12, B13, B14, B24, B25, B27, B26. Reviewed the overall Main/Backup montage for style consistency.

- Main additions fit the original source/navigation areas. No main-body font or formula size changes; card geometry, figures and scientific content remain in their existing positions.
- M12 wraps LCS (GreenCache) within its existing policy column; it fits the existing row without changing table geometry.
- Source lines and buttons remain separate; numbered secondary returns fit on a single line. No clipping, source/navigation overlap or crowding was observed.
- Index Open A–D had pre-existing annotation overlap caused by table-cell link bounds. Local mbox wrappers constrain clickable bounds without moving the visible table or changing spacing.
- All click rectangles are on-page and mutually non-overlapping. Visible return text is verified against its actual destination, including primary Main numbers.
- Lower-page whitespace diagnostics remain informational; the established layout was preserved rather than redesigned.

## Validator regression checks

`python scripts/test_navigation.py`: 3 tests passed. The validator rejects a removed M10 → B13 entry, an Eq. (9) button misrouted to the valid B27 destination, and a removed B09 → M18 visible return. These tests run against temporary PDFs and leave deliverables untouched.

## Scientific boundaries and remaining issues

No unresolved navigation or semantic-alignment issue remains. GreenCache did not evaluate HBF or multi-region placement; cross-region optimization and HBM–HBF tiering remain explicitly our future work. Hypothetical LCS examples are heuristics, not measured carbon or workload hit rates. Higher hit rate is not automatically carbon reduction.

Existing paper ambiguities are unchanged: §6.1 states a 2.5 s 8B document TTFT threshold while Fig. 13 draws 4.0 s (B11 / PDF 32 and B16 / PDF 37); the §6.2 skewness wording does not align cleanly with its reported averages. The supplied Fig. 2 PNG has a small pre-existing top-edge crop, documented in README. None required changing the research content for this task.
