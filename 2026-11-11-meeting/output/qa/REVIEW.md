# Visual and scientific QA — 2026-11-11 GreenCache

Checked after the clean pdfLaTeX log and the ZIP byte-level page comparison. Automatic lower-page white ratios treat chart interiors as empty, so they are not used as a failure signal. The pages below were inspected as rendered PNGs.

## With-Caption update

All 20 embedded figures match the supplied With-Caption PNGs by pixel hash. The 40-page local PDF and independently compiled Overleaf ZIP render identically; 190 internal links pass validation. Both updated montages and the split-figure pages were inspected. Captions remain visible, and content stays clear of the footer. Compilation intermediates are created in temporary directories and removed automatically.

## Figures

- Fig. 12a on PDF 11 keeps the legend, three 70B panels, axis labels, cache-size annotations, the “(a)” caption, and the original Fig. 12 caption. The 8B row is on PDF 32.
- Fig. 13a on PDF 12 keeps the legend, six 70B panels, thresholds, the “(a) Llama-3 70B” caption, and the original Fig. 13 caption. The 8B row is on PDF 33.
- Fig. 14a on PDF 13 keeps all four grids (FR, FI, ES, CISO), both rows, axis labels, cache-size labels, the “(a)” caption, and the original Fig. 14 caption. PDF 34 is the document timeline, with the original legend strip above it.
- An earlier crop used 1 px = 1 bp. These PNGs are 3780 px/m, so that crop cut through Fig. 14’s lower panels and let text overlap the image. The current trims use 0.752813 pt/px. The overlap is gone.
- Fig. 2 on PDF 18 drops about 16 px of orphan title pixels at the top of the supplied PNG. The axes and legend remain.

## Layout

- The cover follows the Helix cover hierarchy: deck label, large left-aligned paper title, subtitle, authors and venue, then unboxed meeting details.
- Blue slide-title and content-box backgrounds now match the page background throughout the deck. Source figure colors remain intact. The updated cover and all-page montages were inspected after rebuilding.

- PDF 2, 6, 7, 9, 10, and 16 use the page as cards or a figure-plus-steps row rather than one block stuck under the title.
- PDF 3 and 15 still have some open space under a short figure and a compact table. The text and source line sit with the content; the gap is the remainder of a 16:9 frame, not a clipped figure.
- Buttons sit on the source line. They do not cover axis labels on the inspected result pages.

## Science checks that stayed in the deck

- 15.1% / 25.3% is labeled FR, Llama-3 70B, multi-turn, versus Full Cache.
- 12.6% / 9.4% / 5.6% is labeled as the four-grid average and explicitly not the FR-only number.
- Fig. 8: ratio below 1 is a reduction, above 1 is an increase.
- Fig. 11 backup states the opposite ratio direction.
- LCS hit rate is token-based. 0.26 and 0.35 are the 4 TB, α=0.7 pair.
- PDF 9 says there is no standalone GPU-serving simulator.
- The HBF sentence is labeled as our interpretation.

## Still unresolved

- 8B document TTFT: Section 6.1 says 2.5 s; the Fig. 13 dashed line is at 4.0 s.
- The paper’s later sentence that high-skewness savings are higher does not match 5.6% versus 9.4%. The slides follow the numerical sentence.
