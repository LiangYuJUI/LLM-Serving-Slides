# Visual and scientific QA — 2026-11-11 GreenCache

## Structure and layout

- 15 main slides plus 25 index/background/backup slides, 40 pages total.
- PDF 2 defines embodied and operational carbon and uses Fig. 7 to explain the request-rate trend, without detailed platform numbers. PDF 3 uses Fig. 8 and explicitly refers to Fig. 7(b) for capacity evidence. Both retain the supplied captions.
- PDF 4 states the optimization objective and separate latency attainments. PDF 6 explains profiling, forecasting, solving, and applying the chosen capacity without repeating the objective slide.
- The KV reuse explanation and Fig. 1 now occupy B00 / PDF 17. The index is PDF 16. Backup pages B01–B23 remain at PDF 18–40.
- The cover follows the Helix hierarchy. Blue title and content backgrounds remain removed. Source figures keep their original colors.
- Inspected the revised pages and updated all-page montages. Figures, captions, source lines, and navigation remain within the page with no overlapping content.

## Validation

- Local PDF: two clean pdfLaTeX passes, with no Overfull, undefined-reference, or LaTeX warnings.
- Extracted Overleaf ZIP: two passes; all 40 rendered pages, text, and link targets match the local PDF.
- 193 links checked, including main-to-backup return links and reachability of all backup pages.
- All 20 embedded source figures match the supplied With-Caption PNGs by pixel hash.
- Build intermediates are created in temporary directories and removed automatically.

## Scientific boundaries

- Low-load carbon cost is described as embodied carbon per prompt outweighing operational savings, without asserting a lower hit rate.
- 480 kgCO2e and 76.6% describe the Table 1 platform and model; allocation time determines the serving charge.
- Fig. 8 uses cache / no-cache carbon; below 1 is a reduction. FR +16.5% and MISO -7.5% apply to the stated fixed-cache setting.
- TTFT and TPOT each require 90% attainment, rather than a per-request or joint guarantee.
- 15.1% / 25.3% remain in the experiments and conclusion, labeled FR, Llama-3 70B, multi-turn, versus Full Cache.
- 8B document TTFT remains unresolved: Section 6.1 says 2.5 s while Fig. 13 shows 4.0 s.
- The HBF discussion remains labeled as our interpretation.
