#!/usr/bin/env python3
"""Negative checks for Research Materials navigation and page-count contracts."""
import json
import unittest
import pymupdf as fitz
import build_research_materials as build

class NavigationContracts(unittest.TestCase):
    def reject(self, mutate):
        with fitz.open(build.PDF) as doc:
            mutate(doc)
            with fitz.open(stream=doc.tobytes(), filetype='pdf') as changed:
                with self.assertRaises(AssertionError):
                    build.validate(changed)

    def test_misrouted_category(self):
        def mutate(doc):
            link = next(x for x in doc[1].get_links() if x.get('nameddest') == 'GPU')
            doc.xref_set_key(link['xref'], 'A/D', '(MEMORY)')
        self.reject(mutate)

    def test_missing_return(self):
        def mutate(doc):
            link = next(x for x in doc[2].get_links() if x.get('nameddest') == 'EINDEX')
            doc[2].delete_link(link)
        self.reject(mutate)

    def test_missing_reel_supplement(self):
        def mutate(doc):
            link = next(x for x in doc[9].get_links() if x.get('nameddest') == 'REELABOUT')
            doc[9].delete_link(link)
        self.reject(mutate)

    def test_missing_reel_supplement_return(self):
        def mutate(doc):
            link = next(x for x in doc[15].get_links() if x.get('nameddest') == 'REEL1')
            doc[15].delete_link(link)
        self.reject(mutate)

    def test_valid_deck(self):
        with fitz.open(build.PDF) as doc:
            build.validate(doc)

    def test_missing_memory_supplement(self):
        def mutate(doc):
            link = next(x for x in doc[3].get_links() if x.get('nameddest') == 'MEMORYSOURCES')
            doc[3].delete_link(link)
        self.reject(mutate)

    def test_missing_memory_supplement_return(self):
        def mutate(doc):
            link = next(x for x in doc[16].get_links() if x.get('nameddest') == 'MEMORY')
            doc[16].delete_link(link)
        self.reject(mutate)

    def test_missing_geo_evidence(self):
        def mutate(doc):
            for rect in doc[6].search_for('19.4%'):
                doc[6].add_redact_annot(rect)
            doc[6].apply_redactions()
        self.reject(mutate)

    def test_wrong_page_count(self):
        self.reject(lambda doc: doc.delete_page(13))

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NavigationContracts))
    (build.QA/'research-materials-navigation-tests.json').write_text(json.dumps(dict(
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        passed=result.wasSuccessful(), pdf_sha256=build.digest(build.PDF)), indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
