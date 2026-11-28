# Build and PDF validation

- PASS: Paper Review has 16 main slides and 17 backup slides (33 total).
- PASS: Research Discussion retains 10 slides and zero backup slides.
- PASS: each deck compiled twice with pdfLaTeX, locally and from its standalone ZIP.
- PASS: local and extracted ZIP PDFs match in text and rendered pixels.
- PASS: 16:9 page dimensions, declared page numbering, text/image bounds, and PDF readability checks.
- PASS: 46 internal links resolve to valid PDF pages; every backup page has a return link.
- PASS: no actionable overfull or missing-character LaTeX warnings in local or ZIP builds.
- PASS: Research Discussion source and pre-build PDF rendering remain unchanged.
- Visual montages and full-resolution page renders are in this directory.
- Manual visual inspection is recorded in the execution report; automated checks do not replace it.
