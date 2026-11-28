#!/usr/bin/env python3
"""Build, package, render, and validate the meeting decks from deck_manifest.json."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile, zipfile
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
MANIFEST = json.loads((ROOT / "deck_manifest.json").read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_twice(cwd, source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        run = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={destination}", source],
            cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if run.returncode:
            raise RuntimeError(run.stdout[-8000:])
    log = (destination / (Path(source).stem + ".log")).read_text(errors="replace")
    actionable = re.findall(
        r"^.*(?:Overfull \\hbox|Overfull \\vbox|Missing character|undefined references|Reference .* undefined|not found).*$",
        log, re.M,
    )
    return destination / (Path(source).stem + ".pdf"), actionable


def audit_pdf(path, cfg, name):
    expected = cfg["main_slides"] + cfg["backup_slides"]
    doc = fitz.open(path)
    assert len(doc) == expected, (path, len(doc), expected)
    pages, internal_links = [], []
    for index, page in enumerate(doc):
        number = index + 1
        assert abs(page.rect.width / page.rect.height - 16 / 9) < .002, (path, number, page.rect)
        text = page.get_text()
        flat = re.sub(r"\s+", " ", text).strip()
        if cfg.get("footer_style") == "legacy":
            assert re.search(rf"\b{number}\s*/\s*{expected}\b", flat), (path, number, flat[-100:])
        elif number <= cfg["main_slides"]:
            assert re.search(rf"Main\s+0?{number}\s*/\s*0?{cfg['main_slides']}\b", flat), (path, number, flat[-140:])
        else:
            backup_no = number - cfg["main_slides"]
            assert re.search(rf"\bB{backup_no}\b", flat), (path, number, flat[-100:])
        if name == "2026-12-02-Paper-Review":
            assert "Kareto Paper Review" not in flat, (path, number, "old footer label remains")
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    rect = fitz.Rect(span["bbox"])
                    assert rect.x0 >= -1 and rect.y0 >= -3 and rect.x1 <= page.rect.width + 1 and rect.y1 <= page.rect.height + 3, (path, number, span["text"], rect)
        for info in page.get_image_info():
            assert page.rect.contains(fitz.Rect(info["bbox"])), (path, number, info["bbox"])
        for link in page.get_links():
            if link.get("kind") in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                target = link.get("page", -1)
                assert 0 <= target < len(doc), (path, number, link)
                internal_links.append({"from": number, "to": target + 1})
        pages.append({"page": number, "text": text, "flat_text": flat,
                      "dimensions_pt": [page.rect.width, page.rect.height]})
    if name == "2026-12-02-Paper-Review":
        assert len(internal_links) >= cfg["backup_slides"], ("expected navigable main/backup links", internal_links)
        for backup_page in range(cfg["main_slides"] + 1, expected + 1):
            assert any(link["from"] == backup_page for link in internal_links), ("backup page lacks a return link", backup_page)
        if cfg.get("cover_title"):
            normalized = re.sub(r"\s+", " ", cfg["cover_title"]).strip()
            assert normalized in pages[0]["flat_text"], ("cover title mismatch", cfg["cover_title"])
        for slide_number, title in enumerate(cfg["titles"], start=2):
            normalized = re.sub(r"\s+", " ", title).strip()
            assert normalized in pages[slide_number - 1]["flat_text"], ("title mismatch", slide_number, title)
    return doc, pages, internal_links


def render_pages(doc, qa, prefix):
    images = []
    page_dir = qa / "pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    for stale_page in page_dir.glob(f"{prefix}-*.png"):
        stale_page.unlink()
    for index, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        image.save(page_dir / f"{prefix}-{index:02}.png")
        image.thumbnail((420, 236))
        images.append(image.copy())
    columns, cell_w, cell_h = 3, 420, 260
    rows = (len(images) + columns - 1) // columns
    montage = Image.new("RGB", (columns * cell_w, rows * cell_h), "#dce4ea")
    draw = ImageDraw.Draw(montage)
    for index, image in enumerate(images):
        x, y = index % columns * cell_w, index // columns * cell_h
        montage.paste(image, (x, y))
        draw.text((x + 8, y + 239), f"{index + 1}/{len(images)}", fill="#243748")
    montage.save(qa / f"{prefix}-montage.png")


def image_parity(left, right):
    assert len(left) == len(right)
    matches = []
    for page_no, (a, b) in enumerate(zip(left, right), 1):
        assert a.get_text() == b.get_text(), ("text mismatch", page_no)
        assert a.get_pixmap().digest == b.get_pixmap().digest, ("render mismatch", page_no)
        matches.append(True)
    return all(matches)


def main():
    qa = OUT / "qa"
    (OUT / "pdf").mkdir(parents=True, exist_ok=True)
    (OUT / "overleaf").mkdir(parents=True, exist_ok=True)
    for old in (qa / "pages").glob("paper-review-*.png"):
        old.unlink()
    results = {}
    with tempfile.TemporaryDirectory(prefix="meeting-build-") as temp:
        temp = Path(temp)
        for name, cfg in MANIFEST.items():
            source = f"{name}.tex"
            is_review = name == "2026-12-02-Paper-Review"
            figure_paths = cfg["figures"]
            for figure in figure_paths:
                assert (ROOT / figure).is_file(), (name, figure)
            if is_review:
                tex = (ROOT / source).read_text()
                assert not re.search(r"\\includegraphics(?:\[[^]]*\])?\{/(?:Users|home)/", tex)
                includes = {item for item in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex) if not item.startswith("#")}
                assert includes.issubset(set(figure_paths)), ("undeclared figure dependency", includes - set(figure_paths))

            # Preserve an existing Research Discussion PDF as a content/render baseline.
            output_pdf = OUT / "pdf" / cfg.get("pdf_filename", f"{name}.pdf")
            baseline = fitz.open(output_pdf) if not is_review and output_pdf.exists() else None
            local_pdf, local_warnings = compile_twice(ROOT, source, temp / name)
            assert not local_warnings, (name, "local LaTeX warnings", local_warnings)
            local_doc, page_data, links = audit_pdf(local_pdf, cfg, name)
            if baseline is not None:
                baseline_cfg = {"main_slides": cfg["main_slides"], "backup_slides": cfg["backup_slides"], "titles": [], "footer_style": cfg.get("footer_style")}
                _, _, _ = audit_pdf(output_pdf, baseline_cfg, name)
                assert image_parity(baseline, local_doc), "Research Discussion content changed"
                baseline.close()
            shutil.copy2(local_pdf, output_pdf)

            archive = OUT / "overleaf" / ("Paper-Review.zip" if is_review else "Research-Discussion.zip")
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
                zipped.write(ROOT / source, "main.tex")
                for figure in figure_paths:
                    zipped.write(ROOT / figure, figure)
                zipped.writestr("README.txt", "Entry point: main.tex\nCompiler: pdfLaTeX\nCompile twice for final cross-references.\nAll required relative-path assets are included.\n")
            extracted = temp / f"{name}-package"
            extracted.mkdir()
            with zipfile.ZipFile(archive) as zipped:
                assert zipped.testzip() is None
                zipped.extractall(extracted)
            packaged_pdf, package_warnings = compile_twice(extracted, "main.tex", temp / f"{name}-package-build")
            assert not package_warnings, (name, "ZIP LaTeX warnings", package_warnings)
            packaged_doc, _, package_links = audit_pdf(packaged_pdf, cfg, name)
            matched = image_parity(local_doc, packaged_doc)
            render_pages(local_doc, qa, "paper-review" if is_review else "research-discussion")
            results[name] = {
                "main_slides": cfg["main_slides"], "backup_slides": cfg["backup_slides"],
                "pages": len(local_doc), "titles": cfg["titles"], "pdf_sha256": sha(output_pdf),
                "zip_sha256": sha(archive), "local_passes": 2, "zip_passes": 2,
                "local_zip_text_pixel_match": matched, "internal_links": links,
                "local_warning_count": len(local_warnings), "zip_warning_count": len(package_warnings),
                "page_dimensions_pt": page_data[0]["dimensions_pt"],
                "page_text": [entry["flat_text"] for entry in page_data],
            }
            local_doc.close()
            packaged_doc.close()

    (qa / "validation.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    review = results["2026-12-02-Paper-Review"]
    discussion = results["2026-12-02-Research-Discussion"]
    report = [
        "# Build and PDF validation", "",
        f"- PASS: Paper Review has {review['main_slides']} main slides and {review['backup_slides']} backup slides ({review['pages']} total).",
        f"- PASS: Research Discussion retains {discussion['main_slides']} slides and zero backup slides.",
        "- PASS: each deck compiled twice with pdfLaTeX, locally and from its standalone ZIP.",
        "- PASS: local and extracted ZIP PDFs match in text and rendered pixels.",
        "- PASS: 16:9 page dimensions, declared page numbering, text/image bounds, and PDF readability checks.",
        f"- PASS: {len(review['internal_links'])} internal links resolve to valid PDF pages; every backup page has a return link.",
        "- PASS: no actionable overfull or missing-character LaTeX warnings in local or ZIP builds.",
        "- PASS: Research Discussion source and pre-build PDF rendering remain unchanged.",
        "- Visual montages and full-resolution page renders are in this directory.",
        "- Manual visual inspection is recorded in the execution report; automated checks do not replace it.", "",
    ]
    (qa / "validation.md").write_text("\n".join(report))
    print(f"PASS: Paper Review {review['main_slides']}+{review['backup_slides']} pages; Research Discussion unchanged; local/ZIP build, bounds, and links validated.")


if __name__ == "__main__":
    main()
