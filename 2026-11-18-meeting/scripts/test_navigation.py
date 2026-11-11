#!/usr/bin/env python3
"""A valid page number is not enough: the link must still mean the contracted backup."""
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
        with tempfile.TemporaryDirectory(prefix='carbonslo-negative-') as folder:
            root = Path(folder)
            (root / 'scripts').mkdir()
            (root / 'output/qa').mkdir(parents=True)
            (root / 'output/overleaf').mkdir()
            (root / 'scripts/navigation-contracts.json').symlink_to(validate.CONTRACTS)
            (root / 'output/overleaf/CarbonSLO.zip').symlink_to(
                validate.ROOT / 'output/overleaf/CarbonSLO.zip')
            tex = root / validate.TEX.name
            tex.write_bytes(validate.TEX.read_bytes())
            pdf = root / 'mutated.pdf'
            with fitz.open(validate.PDF) as document:
                mutate(document)
                document.save(pdf)
            report = json.loads((validate.ROOT / 'output/qa/build-validation.json').read_text())
            report['pdf_sha256'] = hashlib.sha256(pdf.read_bytes()).hexdigest()
            report['source_sha256'] = hashlib.sha256(tex.read_bytes()).hexdigest()
            (root / 'output/qa/build-validation.json').write_text(json.dumps(report))
            with patch.multiple(validate, ROOT=root, TEX=tex, PDF=pdf, CONTRACTS=root / 'scripts/navigation-contracts.json'):
                with self.assertRaisesRegex(AssertionError, expected_error):
                    validate.validate(root / 'renders')

    def test_missing_table_link(self):
        def mutate(doc):
            page = doc[3]  # M04
            link = next(x for x in page.get_links() if x.get('nameddest') == 'B01')
            page.delete_link(link)
        self.rejects_pdf_mutation(mutate, 'contract pair drift')

    def test_table_link_points_at_limits(self):
        def mutate(doc):
            page = doc[3]
            link = next(x for x in page.get_links() if x.get('nameddest') == 'B01')
            doc.xref_set_key(link['xref'], 'A/D', '(B10)')
        self.rejects_pdf_mutation(mutate, 'contract pair drift')

    def test_right_page_without_table_evidence(self):
        def mutate(doc):
            page = doc[20]  # B01
            for area in page.search_for('SLIT'):
                page.add_redact_annot(area, text=' ')
            page.apply_redactions()
        self.rejects_pdf_mutation(mutate, 'semantic evidence missing')


if __name__ == '__main__':
    unittest.main()
