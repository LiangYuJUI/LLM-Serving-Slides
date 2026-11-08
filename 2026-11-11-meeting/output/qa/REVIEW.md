# Visual and scientific QA — 2026-11-11 GreenCache

## Page order and layout

- 19 Main pages + 29 Discussion/Backup pages (including the index) = 48 pages.
- PDF 9 / M09: general Eq. (7), all variable meanings, lower score means earlier eviction, compact grow/shrink operations, and task-specific implementation distinction.
- PDF 10 / M10: ShareGPT Eq. (8), conversation depth and accumulated token reuse, three-turn history-KV diagram.
- PDF 11 / M11: TriviaQA Eq. (9), document hit count and accumulated reused document length, shared-prefix KV diagram. Both alpha settings use Eq. (9).
- M10 and M11 use identical left/right column widths, formula font size, and formula position.
- PDF 12 / M12 compares FIFO, LRU, and LCS by mechanism, limitation, and one representative result: Llama-3 70B, TriviaQA α=0.7, 4 TB, token-level hit rate 23% / 26% / 35%. The +9 percentage-point finding is LCS minus LRU, not a relative improvement and not carbon reduction. FIFO/LRU limitations are inferred from the mechanism. Full Table 3 is the clickable link to B26.
- PDF 13–18 retain the prototype, settings, and four experiment pages. Conclusion is PDF 19. No experiment page was removed.
- Discussion Index is PDF 20. B13 is PDF 34; B25 is PDF 46; B27 is PDF 47; B26 is PDF 48. B13 and B25 remain hypothetical scoring examples and link to M09–M12. B26 holds the only full Table 3 and links back to M09–M12.
- B13 examples yield 200, 400, 600; B25 examples yield 1000, 2000, 3000. All use consistent GiB/hour units and evict A first. These are illustrative calculations, not paper experiments.
- PDF 8 separates two groups. Group A is the Equation (6) attainment sums. Group B is labeled as the §5.4.2 modeling assumptions and states that Equation (6) does not list that group as mathematical constraints.
- Inspected M11, M12, M14, INDEX, B02, B03, B13, B25, B27, and B26 at full rendered size. Text, bars, tables, source lines, and buttons are legible without clipping or overlap. See `navigation-review.png` and page PNGs.

## Build and navigation validation

- Local PDF: two clean pdfLaTeX passes; no Overfull, undefined-reference, or LaTeX warnings.
- Extracted Overleaf ZIP: two passes; all 48 rendered pages, text, and link targets match the local PDF.
- 273 internal links resolve to real destinations; every backup remains reachable and main-to-backup return links pass.
- All 28 backups have a standard visible Back to Main button and a separate body Discussion Index button. The validator intersects their text boxes with actual PDF link annotation rectangles and resolves destinations. Footer links alone cannot pass.
- B02 and B03 now return to M02 while keeping KV Reuse / Next. B13 returns to M10; B25 to M11; B26 and B27 to M12. Existing LCS cross-links remain.
- M12 → B27 → M12 and M12 → B26 → M12 pass. M11, M14, B25, B26, and INDEX → B27 pass, as do all B27 cross-links. `navigation-audit.md` records every backup's page, primary main, and other links.
- Frame labels are unique, all internal targets exist, and PDF destinations match frame-derived page numbers. Table 3 retains all 45 independently transcribed values. The 48-page total is a build result, not a hard-coded validator list.
- All 20 embedded paper figures retain their source pixel hashes.

## Scientific boundaries

- Eq. (7) is the general principle; ShareGPT uses Eq. (8), both TriviaQA skewness settings use Eq. (9). No independent Eq. (7)/(8)/(9) ablation is claimed.
- Age is time in storage. Scores are heuristics, not measured CO2, and do not directly multiply by current CI.
- Reuse requires matching retained KV; new input tokens still require computation.
- Solver sets capacity; LCS selects replacements. Releasing allocated SSD changes amortized accounting, not historical manufacturing emissions, and does not move all SSD KV into GPU HBM.
- TTFT/TPOT attainment sums remain separate. The unresolved 8B document TTFT threshold and HBF interpretation remain identified in their original content.


## TriviaQA source verification

- Read the local paper's PDF pages 15–16 (§5.5 and §6.1) and 19 (§6.3.2, Table 3).
- Originally near-uniform document visits are skewed with Zipf: α=0.4 gives the top 10% about 25% of prompts; α=0.7 gives about 50%. Bars show these approximate paper shares, with no invented request counts.
- Poisson arrivals, scaled Azure trace rates, 50k prompt initialization, and distinct profiling/evaluation sets follow §6.1. Zipf α is explicitly separated from arrival-rate parameters, cache capacity, and CI.
- Both distributions use Eq. (9). Fixed 4 TB Llama-3 70B LCS token hit rates are 14% and 35%. This is not a carbon-reduction calculation or a guaranteed cache hit.
- The new page is B27, between B25 and B26. B00–B26 labels remain unchanged, as does Main order.

- Pixel comparison against the pre-edit PDF: the 16 Main pages other than M11, M12, and M14 are identical above the page-count footer. All pages necessarily update the total count from 47 to 48. Other backup changes are the requested standard return-button wording, with local navigation changes on B02, B03, B13, B25, and B26.
