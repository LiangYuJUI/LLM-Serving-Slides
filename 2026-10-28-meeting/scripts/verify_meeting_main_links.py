#!/usr/bin/env python3
"""Check backup navigation in the Meeting-Main PDF.

Requires PyMuPDF. Run from 2026-10-28-meeting/ or pass paths.
--baseline is the 38-page PDF from before this navigation pass.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    sys.stderr.write("PyMuPDF is required: python3 -m pip install pymupdf\n")
    sys.exit(2)

HERE = Path(__file__).resolve().parents[1]
DEFAULT_PDF = HERE / "output" / "pdf" / "2026-10-28-Meeting-Main.pdf"
HELIX = HERE / "output" / "pdf" / "2026-10-28-Helix.pdf"
TESSERA = HERE / "output" / "pdf" / "2026-10-28-Tessera.pdf"
SCRIPT = HERE / "Meeting-Main_scripts.md"

FORMAL_TARGETS = {
    1: set(),
    2: {19, 23, 24, 34, 37, 39},
    3: {17, 18, 31},
    4: {15, 19, 23, 24},
    5: {28, 29, 30},
    6: {22, 28, 31},
    7: {32, 33},
    8: {34, 35},
    9: {37, 39, 42, 43},
    10: {49, 50},
    11: {43, 49, 51},
    12: {42, 45, 52},
    13: {14, 19, 24, 34},
}

# Consecutive topic runs on the final PDF: start, end, return page.
TOPICS = [
    (15, 16, 4),
    (17, 17, 3),
    (18, 18, 3),
    (19, 21, 4),
    (22, 22, 6),
    (23, 23, 4),
    (24, 24, 4),
    (25, 25, 5),
    (26, 27, 7),
    (28, 28, 5),
    (29, 29, 5),
    (30, 30, 5),
    (31, 31, 6),
    (32, 32, 7),
    (33, 33, 7),
    (34, 34, 8),
    (35, 35, 8),
    (36, 36, 9),
    (37, 38, 9),
    (39, 40, 9),
    (41, 41, 9),
    (42, 42, 9),
    (43, 44, 9),
    (45, 45, 12),
    (46, 46, 10),
    (47, 47, 10),
    (48, 48, 12),
    (49, 49, 10),
    (50, 50, 10),
    (51, 51, 11),
    (52, 52, 12),
]
INDEX_TARGETS = {start for start, _, _ in TOPICS} | {13}

INCLUDED = {
    28: ("helix", 26, "Evaluation Methodology", "HELIX / EVALUATION"),
    29: ("helix", 27, "Workload Characteristics", "HELIX / EVALUATION"),
    30: ("helix", 28, "Single-Cluster Results", "HELIX / RESULTS"),
    31: ("helix", 29, "Geo-Distributed Results", "HELIX / RESULTS"),
    32: ("helix", 31, "Model Placement Deep Dive", "HELIX / ABLATION"),
    33: ("helix", 32, "Request Scheduling Deep Dive", "HELIX / ABLATION"),
    34: ("tessera", 6, "Different Kernels Prefer Different GPUs", "TESSERA / MOTIVATION"),
    35: ("tessera", 7, "Phase Labels Hide Kernel-Level Variation", "TESSERA / MOTIVATION"),
    48: ("tessera", 25, "Communication Backends and Interconnects", "TESSERA / IMPLEMENTATION"),
    49: ("tessera", 26, "Evaluation Methodology", "TESSERA / EVALUATION"),
    50: ("tessera", 27, "Offline Throughput", "TESSERA / RESULTS"),
    51: ("tessera", 28, "Online Latency under a Token SLO", "TESSERA / RESULTS"),
    52: ("tessera", 30, "Pipeline Effectiveness", "TESSERA / DRILL-DOWN"),
}


def goto_pages(page):
    found = []
    for link in page.get_links():
        target = link.get("page")
        if target is not None and link.get("kind") != pymupdf.LINK_URI:
            found.append(target + 1)
    return found


def check_structure(doc, errors):
    if doc.page_count != 52:
        errors.append(f"page count is {doc.page_count}, expected 52")
    for number in range(2, 14):
        text = doc[number - 1].get_text()
        if f"Main {number}/13" not in text:
            errors.append(f"page {number} footer is not Main {number}/13")
        if f"Main {number}/52" in text:
            errors.append(f"page {number} uses the full PDF page count")
    if "Backup Topics" not in doc[13].get_text():
        errors.append("page 14 is not Backup Topics")
    for number, expected in FORMAL_TARGETS.items():
        got = set(goto_pages(doc[number - 1]))
        if got != expected:
            errors.append(f"page {number} GoTo targets {sorted(got)} != {sorted(expected)}")
    index = set(goto_pages(doc[13]))
    if index != INDEX_TARGETS:
        missing = sorted(INDEX_TARGETS - index)
        extra = sorted(index - INDEX_TARGETS)
        errors.append(f"index missing {missing} extra {extra}")
    for start, end, ret in TOPICS:
        for number in range(start, end + 1):
            got = set(goto_pages(doc[number - 1]))
            need = {14, ret}
            if number > start:
                need.add(number - 1)
            if number < end:
                need.add(number + 1)
            if got != need:
                errors.append(f"backup page {number} links {sorted(got)} != {sorted(need)}")
    names = {}
    for page in doc:
        for link in page.get_links():
            name = link.get("nameddest")
            if not name or link.get("page") is None:
                continue
            names.setdefault(name, set()).add(link["page"])
    for name, pages in sorted(names.items()):
        if len(pages) != 1:
            errors.append(f"destination {name} points at {sorted(p + 1 for p in pages)}")


def check_sources(doc, errors):
    sources = {"helix": pymupdf.open(HELIX), "tessera": pymupdf.open(TESSERA)}
    try:
        for new_page, (key, old_page, title, section) in INCLUDED.items():
            included = doc[new_page - 1].get_text()
            source = sources[key][old_page - 1].get_text()
            if title not in source:
                errors.append(f"source {key} page {old_page} lacks {title!r}")
            if title not in included:
                errors.append(f"page {new_page} lacks {title!r}")
            if section not in included:
                errors.append(f"page {new_page} lacks section {section!r}")
            if "Return to Main" not in included or "Backup Topics" not in included:
                errors.append(f"page {new_page} navigation text missing")
    finally:
        for src in sources.values():
            src.close()


def check_script(doc, errors):
    lines = SCRIPT.read_text().splitlines()
    headings = []
    for line in lines:
        if line.startswith("## 第 ") and "｜" in line:
            num = int(line.split("第", 1)[1].split("頁", 1)[0].strip())
            title = line.split("｜", 1)[1].strip()
            headings.append((num, title))
    if [n for n, _ in headings] != list(range(1, 53)):
        errors.append("script page headings are not 1..52")
        return
    for num, title in headings:
        if num == 1:
            continue
        if title not in doc[num - 1].get_text() and title.split(":")[0] not in doc[num - 1].get_text():
            errors.append(f"script title {title!r} is not on PDF page {num}")


def check_baseline(doc, baseline_path, errors):
    base = pymupdf.open(baseline_path)
    try:
        if base.page_count != 38:
            errors.append(f"baseline has {base.page_count} pages, expected 38")
            return
        for number in range(1, 14):
            old = base[number - 1].get_text()
            new = doc[number - 1].get_text()
            if number < 13 and old != new:
                errors.append(f"page {number} text differs from the baseline")
            if number == 13 and new.replace("Backup Topics\n", "", 1) != old and new.replace("\nBackup Topics", "", 1) != old:
                if "Backup Topics" not in new or old not in new.replace("Backup Topics", ""):
                    errors.append("page 13 text differs beyond Backup Topics")
        paper = (251, 252, 254)
        matrix = pymupdf.Matrix(1.4, 1.4)
        for number in range(1, 14):
            a = base[number - 1].get_pixmap(matrix=matrix, alpha=False)
            b = doc[number - 1].get_pixmap(matrix=matrix, alpha=False)
            moved = 0
            wa, wb = a.samples, b.samples
            for i in range(0, len(wa), a.n):
                ink_a = max(abs(wa[i] - paper[0]), abs(wa[i + 1] - paper[1]), abs(wa[i + 2] - paper[2])) > 18
                ink_b = max(abs(wb[i] - paper[0]), abs(wb[i + 1] - paper[1]), abs(wb[i + 2] - paper[2])) > 18
                if ink_a != ink_b:
                    moved += 1
            limit = 2500 if number == 13 else 900
            if moved > limit:
                errors.append(f"page {number} content mask moved {moved} pixels (limit {limit})")
            else:
                print(f"  page {number}: content-mask delta {moved} px")
    finally:
        base.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--baseline", type=Path, default=None)
    args = parser.parse_args()
    errors = []
    doc = pymupdf.open(args.pdf)
    try:
        check_structure(doc, errors)
        check_sources(doc, errors)
        check_script(doc, errors)
        if args.baseline:
            check_baseline(doc, args.baseline, errors)
    finally:
        doc.close()
    if errors:
        print(f"FAILED {len(errors)} check(s):")
        for item in errors:
            print(f"  - {item}")
        return 1
    print(f"OK {args.pdf} (52 pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
