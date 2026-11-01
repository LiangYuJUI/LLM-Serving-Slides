# Helix visual cleanup validation — 2026-11-01

Baseline: `03622aea94186a9c1a36f4fa33624392b678c5cc`.
Result: 15 Main pages, 1 discussion index, 41 topic backup pages = 57 pages, in the same order.

## Changes and scientific claims

Removed all 44 rendered takeaway panels (15 Main, 29 Backup), their padding, and the obsolete takeaway macro. Main source/navigation uses a two-argument slidenote; backup sources and return buttons remain visible. Flexible space balances the body above compact bottom information rows, without reserving the former panel height.

- M03: throughput objective does not directly optimize request latency or percentiles.
- M05: steady max flow estimates throughput for a fixed placement.
- M06: pruning and timed solving do not always prove global optimality.
- M10: 70B vs. SP remains 1.86x offline / 1.69x online throughput with higher average latency.
- M11: simulated 30B online prompt/decode latency reductions of 66% / 24%, vs. Swarm. Simulation is now repeated in the comparison label.
- M12: 3.29x online decode throughput vs. SP, 42-node simulation, LLaMA-2 70B FP16, with slightly higher decode latency.
- M07 / M08: interleaving and KV admission are integrated into the existing body points.
- Backup B01, B05–B07, B09–B10, B12–B14, B22, B25, B27–B28, B31–B32 retain the substantive former panel text as ordinary body paragraphs. Other removed summaries repeat their page's evidence or explanation.

No experiment values or formulas were changed. All academic source strings, frame labels, image assets, and navigation targets are retained. The original Fig. 2 viewports on PDF 5 / 28 remain unchanged, and PDF 24 still supplies the full figure.

## Build and automated checks

- Local pdfLaTeX twice, extracted Overleaf ZIP pdfLaTeX twice, repeated after cleanup. Final logs contain no warnings, undefined references, missing assets, or overfull boxes.
- Local / standalone ZIP: identical text, rendered pixel digests, and hyperlink targets on all 57 pages.
- 224 actual PDF internal link annotations checked against resolved destinations. Exact multiplicities checked for every authored button, footer index, backup return and Beamer section-footer link.
- 12 / 12 supplied caption-free PNGs matched by decoded RGB pixel hashes. Original and caption-free source assets remain unchanged.
- Sources visible on all 56 source-bearing pages; the discussion index has no source in either version.
- PDF text bounds and footer clearance pass. Critical scientific claims checked on PDF 3, 6, 10, 11, 12.
- No takeaway macro remains. Actual PDF drawings contain no broad SoftBlue body panel; title bars and the small illustrative layer-range diagram remain.

## Visual review

Rendered all 57 pages at 2x resolution. Inspected both complete montages, all 15 Main pages at readable resolution, and enlarged PDF 28–33 / 54–55 for formula and solver-evidence details. No text, equations, axes, legends, or navigation are clipped or overlap the footline. Short text-only backup slides retain balanced white space rather than filler.

Figures are enlarged on PDF 7 (3.6 to 4.05 cm height cap), 10 (4.45 to 4.75 cm), 12 (4.4 to 4.85 cm), and 22 (3.0 to 3.4 cm). The key wide figures on PDF 2 / 4 / 5 / 11 / 13 / 14 already use the available width; their original aspect ratios and contents remain intact, with improved vertical balance. The Main and Backup montages reflect this cleanup, not the earlier redesign.

## Cleanup and repeatability

Removed nine confirmed job intermediates from the meeting root: `.aux`, `.log`, `.out`, `.nav`, `.snm`, `.toc`, `.fls`, `.fdb_latexmk`, `.synctex.gz`. None were tracked. No research source, figure, final deliverable, or pre-existing untracked PDF was deleted.

Build logs and recorder files now live only inside `TemporaryDirectory`, which cleans on success or exception. Failed compilation reports a bounded stdout tail. Validation renders default to an automatically cleaned temporary directory; `--render-dir` explicitly opts into retaining pages. A scoped `.gitignore` covers the additional LaTeX intermediate suffixes listed in the task.

After a fresh repeated build and validation, no LaTeX intermediates remain anywhere under the meeting directory. `output/pdf` contains only the final PDF, `output/overleaf` only the final ZIP, and `output/qa` only the ignore file, this review, validation JSON, and the two montage images. The pre-existing untracked root PDF is intentionally left untouched and excluded from the commit.

Manual review is separate from `validation.json`; automated checks alone are not visual proof.
