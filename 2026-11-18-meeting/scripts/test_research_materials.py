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
            link = next(x for x in doc[1].get_links() if x.get('nameddest') == 'WORKLOAD')
            doc.xref_set_key(link['xref'], 'A/D', '(GEO)')
        self.reject(mutate)

    def test_missing_category(self):
        def mutate(doc):
            link = next(x for x in doc[1].get_links() if x.get('nameddest') == 'ENVIRONMENT')
            doc[1].delete_link(link)
        self.reject(mutate)

    def test_missing_reel_supplement(self):
        def mutate(doc):
            link = next(x for x in doc[16].get_links() if x.get('nameddest') == 'REELABOUT')
            doc[16].delete_link(link)
        self.reject(mutate)

    def test_missing_reel_supplement_return(self):
        def mutate(doc):
            # The button and its automatic page reference both link back.
            for link in doc[20].get_links():
                if link.get('nameddest') == 'REEL1':
                    doc[20].delete_link(link)
        self.reject(mutate)

    def test_valid_deck(self):
        with fitz.open(build.PDF) as doc:
            build.validate(doc)

    def test_missing_memory_supplement(self):
        def mutate(doc):
            link = next(x for x in doc[8].get_links() if x.get('nameddest') == 'MEMORYSOURCES')
            doc[8].delete_link(link)
        self.reject(mutate)

    def test_missing_memory_supplement_return(self):
        def mutate(doc):
            # The button and its automatic page reference both link back.
            for link in doc[21].get_links():
                if link.get('nameddest') == 'MEMORY':
                    doc[21].delete_link(link)
        self.reject(mutate)

    def add_text(self, page, text, point=(40, 150)):
        def mutate(doc):
            doc[page].insert_text(point, text, fontsize=10)
        self.reject(mutate)

    # Slide 1 (cover): only title and subtitle.
    def test_cover_author_returns(self):
        self.add_text(0, 'Yu-Jui Liang')

    def test_cover_institution_returns(self):
        self.add_text(0, 'National Taiwan University / Academia Sinica')

    def test_cover_missing_subtitle(self):
        self.remove_text(0, 'Compute and Memory Resources')

    # Slide 2 (index): new cards, no HBM/HBF wording.
    def test_index_mentions_hbf(self):
        self.add_text(1, 'Workload and HBM/HBF Evidence', (40, 150))

    def test_index_missing_new_takeaway(self):
        self.remove_text(1, 'energy- and carbon-efficient LLM serving')

    # Slide 7 (workload table).
    def test_workload_missing_agentic_row(self):
        self.remove_text(6, 'Repeated context')

    def test_workload_scope_note_returns(self):
        self.add_text(6, 'Coding and Conversation follow the workloads evaluated in ThunderServe, not universal definitions.', (40, 150))

    def test_workload_subtitle_returns(self):
        self.add_text(6, 'Workload characteristics influence GPU compute, memory, and scheduling demand.', (40, 150))

    def test_workload_hbf_returns(self):
        self.add_text(6, 'HBM/HBF data placement', (40, 150))

    # Slide 8 (research direction).
    def test_direction_missing_carbon_card(self):
        self.remove_text(7, 'Carbon-Aware Scheduling')

    def test_direction_hbf_returns(self):
        self.add_text(7, 'HBM/HBF capacity, latency and read/write energy', (40, 150))

    def test_direction_novelty_claim_returns(self):
        self.add_text(7, 'Novelty requires further comparison', (40, 150))

    def test_missing_geo_shared_state(self):
        def mutate(doc):
            for rect in doc[2].search_for('same snapshot'):
                doc[2].add_redact_annot(rect)
            doc[2].apply_redactions()
        self.reject(mutate)

    def remove_text(self, page, text):
        def mutate(doc):
            rects = doc[page].search_for(text)
            self.assertTrue(rects, text)
            for rect in rects: doc[page].add_redact_annot(rect)
            doc[page].apply_redactions()
        self.reject(mutate)

    def test_missing_thunder_figure(self):
        def mutate(doc):
            page = doc[5]
            for im in page.get_image_info():
                page.add_redact_annot(fitz.Rect(im['bbox']))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
        self.reject(mutate)

    def test_missing_hbf_scope_note(self):
        self.remove_text(10, 'Published MoE-based simulation evidence')

    def test_missing_simulator_boundary(self):
        self.remove_text(13, 'No HBF hardware is assumed')

    def test_missing_helix_figure(self):
        def mutate(doc):
            page = doc[4]
            for im in page.get_image_info():
                page.add_redact_annot(fitz.Rect(im['bbox']))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
        self.reject(mutate)

    # Source footers were removed from every slide; a returning footer must be rejected.
    def test_source_footer_returns(self):
        self.add_text(3, 'Source: Carbon–SLO, Secs. III-A, III-C.', (40, 240))

    def test_missing_hbf_scope_note_on_slide_10(self):
        self.remove_text(9, 'Published MoE-based simulation evidence')

    def test_missing_static_power_note(self):
        self.remove_text(10, 'static/background power excluded')

    def test_wrong_thank_you_position(self):
        self.reject(lambda doc: doc.move_page(15, 17))

    def test_wrong_page_count(self):
        self.reject(lambda doc: doc.delete_page(13))

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NavigationContracts))
    (build.QA/'research-materials-navigation-tests.json').write_text(json.dumps(dict(
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        passed=result.wasSuccessful(), pdf_sha256=build.digest(build.PDF)), indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
