#!/usr/bin/env python3
"""Regression checks: valid destinations alone must not pass navigation QA."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pymupdf as fitz
import validate


class NavigationRegressionTests(unittest.TestCase):
    def rejects_pdf_mutation(self, mutate, expected_error):
        with tempfile.TemporaryDirectory(prefix='greencache-negative-') as folder:
            root = Path(folder)
            (root / 'scripts').mkdir()
            (root / 'output/qa').mkdir(parents=True)
            (root / 'output/overleaf').mkdir()
            for relative in ['scripts/navigation-contracts.json', 'output/overleaf/GreenCache.zip']:
                (root / relative).symlink_to(validate.ROOT / relative)
            tex = root / validate.TEX.name
            tex.write_bytes(validate.TEX.read_bytes())
            pdf = root / 'mutated.pdf'
            with fitz.open(validate.PDF) as document:
                mutate(document)
                document.save(pdf)
            # Allow this intentionally modified PDF through freshness checking so
            # the test exercises navigation checks, not just artifact hashes.
            report = json.loads((validate.ROOT / 'output/qa/build-validation.json').read_text())
            report['pdf_sha256'] = hashlib.sha256(pdf.read_bytes()).hexdigest()
            (root / 'output/qa/build-validation.json').write_text(json.dumps(report))
            with patch.multiple(validate, ROOT=root, TEX=tex, PDF=pdf):
                with self.assertRaisesRegex(AssertionError, expected_error):
                    validate.validate(root / 'renders')

    def test_missing_worked_example(self):
        def mutate(doc):
            page = doc[9]  # M10
            link = next(x for x in page.get_links() if x.get('nameddest') == 'B13')
            page.delete_link(link)
        self.rejects_pdf_mutation(mutate, 'Navigation contract drift')

    def test_valid_but_semantically_wrong_destination(self):
        def mutate(doc):
            page = doc[10]  # M11: leave visible Eq. 9 wording but point at workload.
            link = next(x for x in page.get_links() if x.get('nameddest') == 'B25')
            doc.xref_set_key(link['xref'], 'A/D', '(B27)')
        self.rejects_pdf_mutation(mutate, 'Navigation contract drift')

    def test_missing_visible_secondary_return(self):
        def mutate(doc):
            page = doc[29]  # B09 shared by M05, M08, M18.
            link = next(x for x in page.get_links() if x.get('nameddest') == 'M18')
            page.delete_link(link)
        self.rejects_pdf_mutation(mutate, 'visible return missing')


if __name__ == '__main__':
    unittest.main()
