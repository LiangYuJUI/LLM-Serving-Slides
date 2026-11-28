#!/usr/bin/env python3
"""Validate manifest-driven outputs and required evidence/navigation coverage."""
import json, re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "deck_manifest.json").read_text())
report = json.loads((root / "output/qa/validation.json").read_text())
review_key = "2026-12-02-Paper-Review"
discussion_key = "2026-12-02-Research-Discussion"
review = report[review_key]
discussion = report[discussion_key]
expected_review = manifest[review_key]
expected_discussion = manifest[discussion_key]
assert review["main_slides"] == expected_review["main_slides"]
assert review["backup_slides"] == expected_review["backup_slides"]
assert review["pages"] == expected_review["main_slides"] + expected_review["backup_slides"]
assert discussion["pages"] == expected_discussion["main_slides"] == 10
assert discussion["backup_slides"] == 0
assert review["local_zip_text_pixel_match"] and discussion["local_zip_text_pixel_match"]
assert review["local_warning_count"] == review["zip_warning_count"] == 0
assert discussion["local_warning_count"] == discussion["zip_warning_count"] == 0
assert len(review["internal_links"]) >= expected_review["backup_slides"]
for page in range(expected_review["main_slides"] + 1, review["pages"] + 1):
    assert any(link["from"] == page for link in review["internal_links"]), page
research_text = "\n".join(discussion["page_text"])
assert [research_text.index(f"Topic {topic}:") for topic in "ABC"] == sorted(research_text.index(f"Topic {topic}:") for topic in "ABC")
for path in [
    "2026-12-02-Paper-Review-Evidence.md", "2026-12-02-Research-Discussion-Evidence.md",
    "2026-12-02-Research-Discussion-SPEC.md", "README.md", "deck_manifest.json",
    "output/pdf/2026-12-02-Kareto.pdf", "output/overleaf/Paper-Review.zip",
    "output/qa/paper-review-montage.png",
]:
    assert (root / path).is_file(), path
for page in range(1, review["pages"] + 1):
    prefix = "paper-review" if page <= review["pages"] else "research-discussion"
    assert (root / "output/qa/pages" / f"{prefix}-{page:02}.png").is_file()
evidence = (root / "2026-12-02-Paper-Review-Evidence.md").read_text()
for status in ["Verified from primary source", "Conceptual illustration", "Proposed research direction", "Hypothesis to validate", "Needs further verification"]:
    assert status in evidence, status
print(f"PASS: {review['main_slides']} main + {review['backup_slides']} backup slides, Research Discussion retained, links and deliverables valid.")
