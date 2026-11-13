# Research Materials validation

- Build base HEAD: `5de69e65dadb7028ca55d10accff91f3183b9c69`
- PASS: 2 local + 2 isolated pdfLaTeX passes, source-only standalone build.
- PASS: no TeX warnings, undefined references/citations, missing characters or overfull/underfull boxes.
- PASS: 6 pages, 16:9, unnumbered cover, content 1/5 through 5/5.
- PASS: text stays within page bounds; every page has clickable external source links.
- PASS: local/isolated text, rendered pixels and URI annotations match.
- PASS: numeric labels, source capacity labels, 16.7x and 47.8% formulas.
- PASS: all 11062 protected files retain SHA-256 hashes during build.
- Rendered: six PNGs at 3x resolution plus 2-column montage.
- PDF SHA-256: `4c8a98cb3af3966102ce7777e9cc6b694732475731ca3cb660e7334b9114fa15`
- PASS: agent visual review on 2026-11-13 of all six full-resolution pages and the final montage. Titles, bars, data labels, source footers, cards and diagram have no observed overlap or clipping. Changed pages 3/4/6 were re-inspected after the final rebuild.

## External URI targets verified in PDF

- https://reellci.com/REEL%20LCI%20Methodology%20Report%20v1.0.pdf
- https://reellci.com/d/hbf-gen1-16hi/
- https://reellci.com/explorer/?category=memory_components
- https://reellci.com/insights/hbm-footprint-inversion.html
- https://reellci.com/insights/the-hbf-inversion.html

## Final visual and preservation audit

- Cover: correct identity/date, no page number.
- Content 1: evidence and prospective-model status readable.
- Content 2: zero baseline, HBF visibly highest, all capacities and values legible.
- Content 3: nominal unit label and GB/GiB qualification visible beside 47.8%.
- Content 4: assumptions separated from limitations; PDF/printed methodology pages identified.
- Content 5: full research title, conceptual architecture, carbon equation, metrics and question visible.
- Reference match: Madrid/Latin Modern/palette/margins retained from November 11.
- Source links: annotations preserve all five official HTTPS targets; destinations were accessed during research (methodology via curl). This checks embedded links, not perpetual server availability.
- Initial snapshot: all 11,058 pre-existing repository files unchanged, including Carbon–SLO assets, PDFs, PNGs, historical decks and build scripts.
- Scope: only 13 new Research Materials files. No existing artifact modified.
- Speaking length: approximately 4 min 40 sec target, Q&A excluded; not timed in a live rehearsal.
