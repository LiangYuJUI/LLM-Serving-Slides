#!/usr/bin/env python3
"""Check backup navigation in the 10-minute review PDF.

Requires PyMuPDF (import pymupdf). Run from 2026-10-28-meeting/ or pass
absolute paths. Optional --baseline is the 12-page PDF from before the
appendix, used for a text and content-mask comparison of pages 1–12.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:  # pragma: no cover
    sys.stderr.write("PyMuPDF is required: python3 -m pip install pymupdf\n")
    sys.exit(2)

HERE = Path(__file__).resolve().parents[1]
DEFAULT_PDF = HERE / "output" / "pdf" / "2026-10-28-10min-Review.pdf"
TS_PDF = HERE.parent / "2026-10-21-meeting" / "output" / "pdf" / "2026-10-21-ThunderServe.pdf"
HETIS_PDF = HERE.parent / "2026-10-21-meeting" / "output" / "pdf" / "2026-10-21-Hetis.pdf"

# New PDF page (1-based) -> source (pdf key, 1-based page, title fragment)
INCLUDED = {
    14: ("ts", 4, "Different GPUs Favor Different Inference Phases"),
    15: ("ts", 6, "Cloud Networking Is Highly Heterogeneous"),
    16: ("ts", 10, "Scheduling as Two-Level Hierarchical Optimization"),
    17: ("ts", 12, "Four Neighbor Operations in Tabu Search"),
    18: ("ts", 15, "Deducing Parallel Configurations"),
    19: ("ts", 18, "Orchestrating Prefill and Decode Replicas"),
    20: ("ts", 19, "Modeling KV Cache Communication Cost"),
    21: ("ts", 21, "Network-Aware Deployment Plans"),
    22: ("ts", 22, "Request-Time Breakdown in Table 5"),
    23: ("ts", 25, "Lightweight Re-scheduling in Real Time"),
    24: ("ts", 27, "Quantize KV Cache for Communication Only"),
    25: ("ts", 35, "End-to-End System Throughput"),
    26: ("ts", 37, "Full Deployment Plans from Table 3"),
    27: ("ts", 41, "Simulator and Alpha-Beta Model Accuracy"),
    28: ("hetis", 3, "Coarse Splitting Wastes KV Cache Capacity"),
    29: ("hetis", 5, "MLP and Attention Scale Differently"),
    30: ("hetis", 6, "Primary Workers and Attention Workers"),
    31: ("hetis", 7, "Hetis System Architecture"),
    32: ("hetis", 10, "Why Split Attention by Head"),
    33: ("hetis", 12, "Dynamic Attention Placement Across Requests"),
    34: ("hetis", 13, "Head Integrity and Grouped-Query Attention"),
    35: ("hetis", 20, "Re-dispatching to Balance Computation"),
    36: ("hetis", 22, "Head-Level KV Management and Migration"),
    37: ("hetis", 31, "Dynamic Head and Cache Allocation"),
    38: ("hetis", 27, "Llama-70B"),
    39: ("hetis", 28, "Maximum Usable KV Cache"),
    40: ("hetis", 38, "HBM / HBF"),
}

# Formal page -> set of backup/index pages its GoTo links may target.
FORMAL_TARGETS = {
    1: set(),
    2: set(),
    3: {14, 19},
    4: {16, 18, 19, 23, 24},
    5: {25},
    6: {23},
    7: {28},
    8: {30, 32},
    9: {38},
    10: {35},
    11: {14, 19, 32, 38},
    12: {13},
}

# Topic runs on the new PDF: (first, last, return page). Index is page 13.
TOPICS = [
    (14, 15, 3),
    (16, 17, 4),
    (18, 18, 4),
    (19, 22, 4),
    (23, 23, 6),
    (24, 24, 4),
    (25, 26, 5),
    (27, 27, 5),
    (28, 29, 7),
    (30, 31, 8),
    (32, 34, 8),
    (35, 37, 10),
    (38, 39, 9),
    (40, 40, 10),
]
INDEX_TARGETS = {14, 16, 18, 19, 23, 24, 25, 27, 28, 30, 32, 35, 38, 40, 12}


def goto_pages(page):
    found = []
    for link in page.get_links():
        target = link.get("page")
        if target is not None and link.get("kind") != pymupdf.LINK_URI:
            found.append(target + 1)
    return found


def check_structure(doc, errors):
    if doc.page_count != 40:
        errors.append(f"page count is {doc.page_count}, expected 40")
    for number in range(1, 13):
        text = doc[number - 1].get_text()
        if f"{number} / 12" not in text:
            errors.append(f"page {number} footer is not {number}/12")
        if f"{number} / 40" in text:
            errors.append(f"page {number} footer includes /40")
    for number, expected in FORMAL_TARGETS.items():
        got = set(goto_pages(doc[number - 1]))
        if number == 10:
            got.discard(None)
        if got != expected:
            errors.append(f"page {number} GoTo targets {sorted(got)} != {sorted(expected)}")
    index = set(goto_pages(doc[12]))
    if index != INDEX_TARGETS:
        errors.append(f"index targets {sorted(index)} != {sorted(INDEX_TARGETS)}")
    for start, end, ret in TOPICS:
        for number in range(start, end + 1):
            got = set(goto_pages(doc[number - 1]))
            need = {13, ret}
            if number > start:
                need.add(number - 1)
            if number < end:
                need.add(number + 1)
            if got != need:
                errors.append(f"backup page {number} links {sorted(got)} != {sorted(need)}")


def check_sources(doc, errors):
    sources = {"ts": pymupdf.open(TS_PDF), "hetis": pymupdf.open(HETIS_PDF)}
    try:
        for new_page, (key, old_page, title) in INCLUDED.items():
            included = doc[new_page - 1].get_text()
            source = sources[key][old_page - 1].get_text()
            if title not in included and title not in source:
                errors.append(f"page {new_page}: title {title!r} missing from source page {old_page}")
            elif title not in included:
                errors.append(f"page {new_page}: included text does not contain {title!r}")
            # A distinctive source sentence, ignoring the old footer number.
            snippet = " ".join(source.split())
            if title.split()[0] not in included:
                errors.append(f"page {new_page}: included page lost the source heading")
            if "Backup " not in included or "Return to Review" not in included:
                errors.append(f"page {new_page}: navigation text missing")
            if snippet and title not in source:
                errors.append(f"source page {old_page} does not contain {title!r}")
    finally:
        for src in sources.values():
            src.close()


def check_baseline(doc, baseline_path, errors):
    base = pymupdf.open(baseline_path)
    try:
        if base.page_count != 12:
            errors.append(f"baseline has {base.page_count} pages, expected 12")
            return
        for number in range(1, 13):
            old = base[number - 1].get_text()
            new = doc[number - 1].get_text()
            if number < 12 and old != new:
                errors.append(f"page {number} text differs from the baseline")
            if number == 12:
                extra = new.replace("Backup topics\n", "", 1)
                if extra != old:
                    errors.append("page 12 text differs beyond the Backup topics link")
        # Content pixels: a color-only link stays non-paper in both renders.
        # A reflow moves ink on or off the paper color.
        paper = (251, 252, 254)
        zoom = 1.6
        matrix = pymupdf.Matrix(zoom, zoom)
        for number in range(1, 13):
            a = base[number - 1].get_pixmap(matrix=matrix, alpha=False)
            b = doc[number - 1].get_pixmap(matrix=matrix, alpha=False)
            if a.width != b.width or a.height != b.height:
                errors.append(f"page {number} render size changed")
                continue
            moved = 0
            wa, wb = a.samples, b.samples
            step = a.n
            for i in range(0, len(wa), step):
                da = max(abs(wa[i] - paper[0]), abs(wa[i + 1] - paper[1]), abs(wa[i + 2] - paper[2]))
                db = max(abs(wb[i] - paper[0]), abs(wb[i + 1] - paper[1]), abs(wb[i + 2] - paper[2]))
                ink_a = da > 18
                ink_b = db > 18
                if ink_a != ink_b:
                    moved += 1
            # Antialiased edges of recolored words move a thin halo.
            # Page 12 also gains the Backup topics line.
            limit = 2500 if number == 12 else 800
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
        if args.baseline:
            check_baseline(doc, args.baseline, errors)
    finally:
        doc.close()
    if errors:
        print(f"FAILED {len(errors)} check(s):")
        for item in errors:
            print(f"  - {item}")
        return 1
    print(f"OK {args.pdf} (40 pages, links and included pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
