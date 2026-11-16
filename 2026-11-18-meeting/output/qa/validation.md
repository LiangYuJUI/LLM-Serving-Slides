# Research Materials validation

- PASS: 14 widescreen PDF pages; unnumbered cover, content 1/13–13/13.
- PASS: two local and two extracted Overleaf ZIP pdfLaTeX passes; no layout/reference warnings.
- PASS: local/ZIP text, pixels, source URI and named-destination annotations match.
- PASS: five full-card index links land on PDF pages 3, 4, 6, 8, 13; 13 visible return links land on page 2.
- PASS: text/image bounds, source hyperlinks on every page, required numeric claims and calculations.
- PASS: four original REEL frame bodies match frozen SHA-256 values exactly; only frame labels and footer changed.
- PASS: protected repository files unchanged during build.
- Rendered all 14 pages at 3x resolution and a two-column montage.
- PASS: all 14 page PNGs and the complete montage visually inspected on 2026-11-17. No observed clipping, overlap, missing elements or unreadable labels. Final changed pages 6 and 8 re-inspected after typography/spacing adjustments.
- PASS: original REEL pages 2–5 versus current pages 9–12 are text- and pixel-identical at 3x above the footer (bottom 16 PDF points excluded).
- PASS: negative regression tests reject a misrouted category, a missing return link and an incorrect page count. See `research-materials-navigation-tests.json`.
- PASS: all 12 distinct external PDF source URLs returned HTTP 200. GreenCache uses the accessible arXiv author version after ACM blocked automated retrieval.
- PASS: all unrelated tracked files retain baseline SHA-256 values, including Carbon–SLO, GreenCache and Research Direction PDFs. See `research-materials-preservation.json`.
- Detailed checksums: `research-materials-build.json`.
- External URL availability: see `research-materials-url-checks.json`; HTTP availability is separate from PDF annotation validity.

## Source hyperlink targets

- https://arxiv.org/abs/2505.23970v3
- https://arxiv.org/abs/2511.00807v1
- https://arxiv.org/abs/2512.13525
- https://arxiv.org/abs/2608.01891
- https://arxiv.org/abs/2609.39131v2
- https://arxiv.org/abs/2610.14571v1
- https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf
- https://reellci.com/d/hbf-gen1-16hi/
- https://reellci.com/explorer/?category=memory_components
- https://reellci.com/insights/hbm-footprint-inversion.html
- https://reellci.com/insights/the-hbf-inversion.html
- https://www.microsoft.com/en-us/research/publication/memexplorer-navigating-the-heterogeneous-memory-design-space-for-agentic-inference-npus/
