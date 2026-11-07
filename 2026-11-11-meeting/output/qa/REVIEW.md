# Visual and scientific QA — 2026-11-11 GreenCache

## Page order and layout

- 19 Main pages + 28 Discussion/Backup pages (including the index) = 47 pages.
- PDF 9 / M09: general Eq. (7), all variable meanings, lower score means earlier eviction, compact grow/shrink operations, and task-specific implementation distinction.
- PDF 10 / M10: ShareGPT Eq. (8), conversation depth and accumulated token reuse, three-turn history-KV diagram.
- PDF 11 / M11: TriviaQA Eq. (9), document hit count and accumulated reused document length, shared-prefix KV diagram. Both alpha settings use Eq. (9).
- M10 and M11 use identical left/right column widths, formula font size, and formula position.
- PDF 12 / M12 compares FIFO, LRU, and LCS by mechanism, limitation, and one representative result: Llama-3 70B, TriviaQA α=0.7, 4 TB, token-level hit rate 23% / 26% / 35%. The +9 percentage-point finding is LCS minus LRU, not a relative improvement and not carbon reduction. FIFO/LRU limitations are inferred from the mechanism. Full Table 3 is the clickable link to B26.
- PDF 13–18 retain the prototype, settings, and four experiment pages. Conclusion is PDF 19. No experiment page was removed.
- Discussion Index is PDF 20. B13 is PDF 34; B25 is PDF 46; B26 is PDF 47. B13 and B25 remain hypothetical scoring examples and link to M09–M12. B26 holds the only full Table 3 and links back to M09–M12.
- B13 examples yield 200, 400, 600; B25 examples yield 1000, 2000, 3000. All use consistent GiB/hour units and evict A first. These are illustrative calculations, not paper experiments.
- PDF 8 separates two groups. Group A is the Equation (6) attainment sums. Group B is labeled as the §5.4.2 modeling assumptions and states that Equation (6) does not list that group as mathematical constraints.
- Inspected PDF 12 and 47. The comparison table, representative result, full Table 3, and hyperlink labels are legible, with no clipping or overlaps. Main 9–12 are captured in `lcs-main-09-12.png`.

## Build and navigation validation

- Local PDF: two clean pdfLaTeX passes; no Overfull, undefined-reference, or LaTeX warnings.
- Extracted Overleaf ZIP: two passes; all 47 rendered pages, text, and link targets match the local PDF.
- 270 internal links resolve to real destinations; every backup remains reachable and main-to-backup return links pass.
- The four Main LCS slides have all 12 directed cross-links. B13 and B25 return to all four Main pages. M12 links to B26, and B26 returns to M09–M12. The index also opens B26.
- Validator checks actual PDF destinations for pages 9–12, 20, 34, 46, and 47. Main labels match page numbers. All 45 Table 3 values are checked on B26. M12 is checked for the 4 TB TriviaQA α=0.7 result only: 23%, 26%, 35%.
- All 20 embedded paper figures retain their source pixel hashes.

## Scientific boundaries

- Eq. (7) is the general principle; ShareGPT uses Eq. (8), both TriviaQA skewness settings use Eq. (9). No independent Eq. (7)/(8)/(9) ablation is claimed.
- Age is time in storage. Scores are heuristics, not measured CO2, and do not directly multiply by current CI.
- Reuse requires matching retained KV; new input tokens still require computation.
- Solver sets capacity; LCS selects replacements. Releasing allocated SSD changes amortized accounting, not historical manufacturing emissions, and does not move all SSD KV into GPU HBM.
- TTFT/TPOT attainment sums remain separate. The unresolved 8B document TTFT threshold and HBF interpretation remain identified in their original content.
