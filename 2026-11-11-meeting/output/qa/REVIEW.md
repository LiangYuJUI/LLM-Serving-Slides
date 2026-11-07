# Visual and scientific QA — 2026-11-11 GreenCache

## Structure and layout

- 17 main slides, 1 discussion index, and 26 backup slides, 44 pages total.
- PDF 7 and PDF 8 share one conceptual summary, \(S^*=\arg\min_{S\in\mathcal{S}}\widehat{C}_{\mathrm{total}}(S)\), in the same position and size. The line under it says this is a conceptual summary and that the full integer linear program is Equation (6).
- PDF 7 links each item title to a backup: decision variable and embodied carbon to B10, the candidate set to B24, operational carbon to B07, and model inputs to B12.
- PDF 8 separates two groups. Group A is the Equation (6) attainment sums. Group B is labeled as the §5.4.2 modeling assumptions and states that Equation (6) does not list that group as mathematical constraints.
- B10 (PDF 29) keeps the printed Equation (6), including the other-hardware numerator \(t^{j_t}_{\mathrm{TTFT},i}\) and the wedge between the two sums. It names operational carbon, SSD embodied carbon, and other-hardware embodied carbon, lists Table 2, and keeps PuLP + CBC at 7.03 s. The objective is prefill carbon; decode latency is carried by the TPOT SLO.
- B11 (PDF 30) shows the TTFT and TPOT binary indicators as separate sums. Each sum is at least 90%. The same requests need not clear both. The 8B document TTFT note still records Section 6.1 at 2.5 s and the Fig. 13 dashed line at 4.0 s.
- B24 (PDF 43) states the 1 TB grid, the 16 TB / 8 TB maxima, hourly resizing with CI held constant inside the hour, warmed-up LCS profiles, and the effect of prediction and profiling error. Those assumptions are not added to Equation (6).
- Slides 4 and 5 keep their previous body. Slide 6 adds a Solver link next to the existing ILP and SLO buttons. LCS remains PDF 9. The index is PDF 18. Backup labels B00–B23 follow it, and B24 is PDF 43; the new B25 is PDF 44.
- Inspected PDF 7, 8, 29, 30, and 43. Formulas, item links, source lines, and navigation sit inside the page. The equation on PDF 30 is clear of the attainment sentence, and the PDF 29 symbol sits above the Table 2 rule.

## Validation

- Local PDF: two clean pdfLaTeX passes, with no Overfull, undefined-reference, or LaTeX warnings.
- Extracted Overleaf ZIP: two passes; all 44 rendered pages, text, and link targets match the local PDF.
- 245 links checked, including main-to-backup return links and reachability of all backup pages.
- All 20 embedded source figures match the supplied With-Caption PNGs by pixel hash.
- Build intermediates are created in temporary directories and removed automatically.

## Scientific boundaries

- The main-slide formula is a summary of the capacity choice. Equation (6) remains the paper's ILP.
- TTFT and TPOT each require 90% attainment. The two sums do not force one shared subset of requests to pass both.
- Group B on PDF 8 is the §5.4.2 modeling assumption set: discrete sizes, an hourly interval with constant CI, and profile-based feasibility.
- 8B document TTFT remains unresolved: Section 6.1 says 2.5 s while Fig. 13 shows 4.0 s.
- The HBF discussion remains labeled as our interpretation.

## LCS refactor — 2026-11-08

- M09 / PDF 9: general Eq. (7), all four variable definitions, explicit time-in-storage Age, lowest-score-first rule, compact grow/shrink operations, and clickable links to both task scores and Table 3.
- M16 / PDF 16: all 45 original Table 3 values retained and verified against the paper (PDF 19); only the 4 TB row is bolded. FIFO/LRU/LCS definitions and token-level hit-rate denominator are explicit. The +9 percentage-point finding and equal 52% result refer to TriviaQA alpha=0.7, not measured carbon savings.
- B13 / PDF 32: Eq. (8) only; ShareGPT turn depth and accumulated reuse, with a three-turn history-KV diagram. Reuse requires matching retained KV; new tokens still require computation.
- B25 / PDF 44: Eq. (9) only; three questions reuse one cached document prefix. Both TriviaQA skewness settings use the same score. Layout matches B13.
- Inspected PDF 9, 16, 18, 32, 42, and 44. Formulas, diagrams, table values, captions, and navigation are legible and do not overlap or clip.
- The four LCS pages have 12 direct cross-links, including every main-to-backup and backup-to-main pair. All 245 destinations resolve, every backup remains reachable, and return links pass validation.
- Unmodified main pages are pixel-identical above the footer to the baseline PDF; total-page footers intentionally change from 43 to 44.
- B23 records the accounting and eviction boundaries. LCS scores do not directly use current CI and are not measured gCO2e; no independent comparison of Equations (7), (8), and (9) is claimed.
