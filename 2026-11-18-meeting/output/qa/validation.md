# Research Materials validation

- PASS: 22 widescreen pages; Thank You at 16, supplements at 17–22.
- PASS: two local and two extracted ZIP pdfLaTeX passes; no warnings.
- PASS: local/ZIP text, pixels and annotations match.
- PASS: four index cards target pages 3, 7, 12 and 14; embodied carbon is supplementary.
- PASS: backup round trips, bounds, evidence values and unchanged evidence frames.
- PASS: all text/image bounds fit; preserved evidence and new proposal contracts pass.
- PASS: Helix Figure 3 retains original resolution and aspect ratio; ZIP asset bytes match.
- PASS: all 21 non-Helix pages match commit 3f90a20 in text, 3x pixels and annotations.

## Helix figure redesign review

- PASS: slide 5 PNG visually inspected at 3×. Original Figure 3 is sharp and complete, with undistorted aspect ratio, readable labels and no overlap with explanatory text or footer.
- PASS: all 14 navigation and scientific-boundary regression tests.
- PASS: only speaker-script section 5 changed; all other sections match commit `3f90a20` exactly.
- PASS: the original image file is unchanged and its exact bytes are included in the Overleaf ZIP. Only its relative reference differs in packaged `main.tex`.
- Scope: slide 5 layout and narration only; all other 21 pages preserve text, 3× pixels and link annotations.
