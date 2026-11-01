# Helix rebuild validation — 2026-11-01

Baseline: `fe489e4fe8d13a5ccd51a802354cb730585f36e7` (37-page deck).
Result: 15 Main pages, 1 discussion index, 41 topic backup pages = 57 pages.

## Automated checks

- `scripts/build.py`: local pdfLaTeX twice, ZIP extraction in a fresh temporary directory, independent pdfLaTeX twice. No warnings, missing references, missing images, or overfull boxes in final logs.
- The 57 local and extracted-ZIP pages have identical text, rendered pixel digests, and hyperlink destinations.
- `scripts/validate.py`: 224 actual internal PDF annotations resolve to valid pages. All explicitly authored Main links, the index links, every backup return, and footer index links match their expected destinations.
- All 12 figure images match supplied `Without-Caption` PNGs by decoded RGB pixel MD5, including repeated uses and the Fig. 2 viewports. This is a pixel-identity check, not a filename check.
- Text is inside page boundaries and clear of the footer. No `caption` command or old figure path occurs in the source.
- Original and caption-free figure files are unchanged from the baseline commit.

## Visual review

All 57 pages rendered at 2x resolution. Reviewed every Main page individually and both complete montages. Additionally inspected dense constraints (29–33), the cost example (28), evaluation setup (42–43), and solver evidence (54–55) at full rendered size. Rebuilt after correcting footer clearance, a table spacing issue, and numeric multiplication glyphs. Final pages show no clipped text, equations, chart content, or footer overlap.

The wide native aspect ratios are preserved. The remaining white space on short slides is intentional and balanced; there is no added filler text. Experimental axes are necessarily smaller than body text, so the full figure backup pages remain useful for detailed discussion.

| Figure | Main PDF page | Old maximum drawn width (pt) | New drawn width (pt) | Width ratio |
|---|---:|---:|---:|---:|
| 1 | 2 | 344.1 | 428.0 | 1.24x |
| 2 | 5 | 143.5 | 265.4 | 1.85x |
| 3 | 4 | 227.4 | 426.8 | 1.88x |
| 4 | 7 | 221.0 | 317.8 | 1.44x |
| 6 | 10 | 170.7 | 367.3 | 2.15x |
| 7 | 11 | 302.0 | 428.0 | 1.42x |
| 8 | 12 | 212.5 | 284.6 | 1.34x |
| 9 | 13 | 320.7 | 428.0 | 1.33x |
| 10 | 14 | 281.4 | 428.0 | 1.52x |

Widths come from PDF image transforms. They compare the old full image against the new image or viewport; they are not a claim about uniform font-size scaling within every source PNG.

## Figure and scientific notes

Fig. 2 uses two LaTeX viewports on pages 5 and 28, omitting its embedded explanatory paragraph while retaining both diagrams and all labels. Page 24 retains the complete supplied figure. No PNG is edited or replaced. Other figures are uncropped. Original embedded subfigure descriptions remain where supplied; no external long caption is reintroduced.

The paper is the source of the experimental claims. Prototype, simulation, model, baseline, arrival mode, and metric are separated. Fig. 11's textual 43% / 8% time-reduction claim is explicitly distinguished from the plotted values' 1.43x / 1.08x speed ratios and 30% / 7.2% elapsed-time reductions. The appendix's dummy-weight artifact scope is stated.

Manual review is separate from `validation.json`; rendering and automated geometry checks alone do not establish visual correctness.
