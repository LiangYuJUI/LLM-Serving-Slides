# Visual and scientific QA — 2026-11-11 GreenCache

## Page order and layout

- 19 Main pages + 27 Discussion/Backup pages (including the index) = 46 pages.
- PDF 9 / M09: general Eq. (7), all variable meanings, lower score means earlier eviction, compact grow/shrink operations, and task-specific implementation distinction.
- PDF 10 / M10: ShareGPT Eq. (8), conversation depth and accumulated token reuse, three-turn history-KV diagram.
- PDF 11 / M11: TriviaQA Eq. (9), document hit count and accumulated reused document length, shared-prefix KV diagram. Both alpha settings use Eq. (9).
- M10 and M11 use identical left/right column widths, formula font size, and formula position.
- PDF 12 / M12: the single complete Table 3, with FIFO/LRU/LCS definitions and all 45 original numbers. The 4 TB row is bolded; the +9 percentage-point finding concerns token-level hit rate, not request-level hits or carbon reduction.
- PDF 13–18 retain the prototype, settings, and four experiment pages. Conclusion is PDF 19. No experiment page was removed.
- Discussion Index is PDF 20. B13 is PDF 34; B25 is PDF 46. Each backup now gives three explicitly hypothetical scoring examples and links to M09–M12.
- B13 examples yield 200, 400, 600; B25 examples yield 1000, 2000, 3000. All use consistent GiB/hour units and evict A first. These are illustrative calculations, not paper experiments.
- PDF 1–8 and all seven moved experiment/conclusion pages are pixel-identical above the footer to the pre-task committed baseline. Footers intentionally reflect new page numbers / total 46.
- PDF 8 separates two groups. Group A is the Equation (6) attainment sums. Group B is labeled as the §5.4.2 modeling assumptions and states that Equation (6) does not list that group as mathematical constraints.
- Inspected PDF 9–12, 20, 34, and 46. Formulas, tables, reuse diagrams, and hyperlink labels are legible, with no clipping or overlaps. Main 9–12 are captured in `lcs-main-09-12.png`.

## Build and navigation validation

- Local PDF: two clean pdfLaTeX passes; no Overfull, undefined-reference, or LaTeX warnings.
- Extracted Overleaf ZIP: two passes; all 46 rendered pages, text, and link targets match the local PDF.
- 263 internal links resolve to real destinations; every backup remains reachable and main-to-backup return links pass.
- The four Main LCS slides have all 12 directed cross-links. Both detailed backups return to all four Main pages.
- Validator checks actual PDF destinations for pages 9–12, 20, 34, and 46; Main labels match page numbers. Table 3 appears once, with all 45 values independently checked against paper PDF 19.
- All 20 embedded paper figures retain their source pixel hashes.

## Scientific boundaries

- Eq. (7) is the general principle; ShareGPT uses Eq. (8), both TriviaQA skewness settings use Eq. (9). No independent Eq. (7)/(8)/(9) ablation is claimed.
- Age is time in storage. Scores are heuristics, not measured CO2, and do not directly multiply by current CI.
- Reuse requires matching retained KV; new input tokens still require computation.
- Solver sets capacity; LCS selects replacements. Releasing allocated SSD changes amortized accounting, not historical manufacturing emissions, and does not move all SSD KV into GPU HBM.
- TTFT/TPOT attainment sums remain separate. The unresolved 8B document TTFT threshold and HBF interpretation remain identified in their original content.
