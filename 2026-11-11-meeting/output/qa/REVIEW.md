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
- 274 internal links resolve to real destinations; every backup remains reachable and main-to-backup return links pass.
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

## M13 / M14 simplification

- Baseline: bda7c5915442e63cf6ed145660bbf6ebd218cf6c. Only M13, M14, and B14 changed in the PDF; all other 45 pages are pixel-identical, including M09–M12, B27, and the index.
- M13 now presents real GPU serving, trace-driven evaluation, and measured power versus modeled carbon in three aligned cards, followed by a Key Takeaway. CPU/GPU measurement, specification-based SSD/DRAM power, and amortized embodied carbon remain distinct.
- M14 emphasizes the three strategies side by side. It retains the common maximum capacity and separate 90% TTFT/TPOT attainment requirements, with a Key Question below the metrics.
- Text extraction before the source line (including titles) falls from 164 to 70 words on M13 (57.3%), and from 138 to 84 on M14 (39.1%). No smaller font was introduced to fit the content.
- Existing technical detail remains in B06/B07/B11/B14/B15/B23/B24/B27. The only newly preserved setup detail is the 8k context limit and truncation in B14, verified against §6.1 on paper PDF page 15. B14 also links back to M14.
- Inspected rendered M13, M14, and B14. Cards, text, sources, and navigation fit without overlap or clipping. Before/after comparisons are `main-13-before-after.png` and `main-14-before-after.png`.
- Local PDF and independently extracted Overleaf ZIP each compile twice without Overfull, undefined references, or LaTeX warnings. All 48 pages have matching renders, text, and link targets between builds.
- Validator passes 274 PDF links, all 28 backup return/index buttons, all 45 Table 3 values, and all 20 original image pixel hashes. Explicit checks cover M13 ↔ B14, M14 ↔ B11, M14 ↔ B27, and B14 → M14. RAPL/pyNVML assertions now apply to B14, and checks reject detailed setup leaking back into M13/M14.
- No unresolved issues introduced by this edit. Previously documented paper ambiguities remain unchanged.

- M14 heading refinement: A/B/C now all use the same small bold Accent font, verified from PDF spans. Reduced top spacing by 0.04 cm to preserve page fit; build and navigation validation pass.

- M15 interpretation refinement: removed explicit reduction percentages from the main text while preserving the original Figure 12a and caption. Three concise takeaways distinguish savings versus Full Cache, prefix reuse opportunities, and No Cache carbon versus latency feasibility. Source numbers remain documented in README. Build and validator pass (48 pages, 274 links); all other 47 pages are pixel-identical to the immediately preceding PDF.

- M16 now summarizes No Cache SLO failures and GreenCache using Full Cache latency headroom to reduce capacity and carbon while meeting SLOs in the plotted experiments. Removed threshold enumeration (retained in B11), preserved separate TTFT/TPOT interpretation, Figure 13a/caption, source, and B16 navigation. Build and validation pass (48 pages, 274 links); other 47 pages are pixel-identical to the preceding PDF.

- M17 now uses qualitative interpretation: lower per-prompt carbon versus Full Cache in the shown timelines; load and CI jointly influence capacity under SLO constraints, without claiming monotonic savings. Original Figure 14a/caption and links remain. Verified §6.1–6.2: Figure 12 averages the dynamic evaluation, while Figure 14 exposes timelines; neither uses fixed CI/request-rate inputs. Build and validator pass (48 pages, 274 links); other 47 pages are pixel-identical to the preceding PDF.

- M18 states the ablation takeaway without the 10.3% / 6.6–9.9% figures: even without LCS, adaptive capacity still reduces carbon versus Full Cache, and the effect is clearer at low load because the cache needed to meet the SLO is smaller. Capacity adjustment contributes; LCS is not claimed to have no further value. Those percentages remain in the README source table. Figure 15, the ES-grid setup, and the B09 link stay.

- M19 drops the Limitations card and stacks Problem, Contribution, Evidence, and Future work full width from top to bottom. Future work is ours: capacity decisions across regional data centers, and HBM–HBF as cache tiers. GreenCache does not evaluate either. Trace length, amortized embodied carbon, sensitivity, and dense Llama-3 remain on B23.
