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

    def test_misrouted_gap_category(self):
        def mutate(doc):
            link = next(x for x in doc[1].get_links() if x.get('nameddest') == 'ACCOUNT')
            doc.xref_set_key(link['xref'], 'A/D', '(ENVIRONMENT)')
        self.reject(mutate)

    def test_missing_gap_category(self):
        def mutate(doc):
            link = next(x for x in doc[1].get_links() if x.get('nameddest') == 'ACCOUNT')
            doc[1].delete_link(link)
        self.reject(mutate)

    def test_missing_category(self):
        def mutate(doc):
            link = next(x for x in doc[1].get_links() if x.get('nameddest') == 'ENVIRONMENT')
            doc[1].delete_link(link)
        self.reject(mutate)

    def test_missing_reel_supplement(self):
        def mutate(doc):
            page = doc[build.PAGE['REEL1']]
            link = next(x for x in page.get_links() if x.get('nameddest') == 'REELABOUT')
            page.delete_link(link)
        self.reject(mutate)

    def test_missing_reel_supplement_return(self):
        def mutate(doc):
            # The button and its automatic page reference both link back.
            page = doc[build.PAGE['REELABOUT']]
            for link in page.get_links():
                if link.get('nameddest') == 'REEL1':
                    page.delete_link(link)
        self.reject(mutate)

    def test_valid_deck(self):
        with fitz.open(build.PDF) as doc:
            build.validate(doc)

    def test_missing_memory_supplement(self):
        def mutate(doc):
            page = doc[build.PAGE['MEMORY']]
            link = next(x for x in page.get_links() if x.get('nameddest') == 'MEMORYSOURCES')
            page.delete_link(link)
        self.reject(mutate)

    def test_missing_memory_supplement_return(self):
        def mutate(doc):
            # The button and its automatic page reference both link back.
            page = doc[build.PAGE['MEMORYSOURCES']]
            for link in page.get_links():
                if link.get('nameddest') == 'MEMORY':
                    page.delete_link(link)
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

    # Slide 11 (research gaps and proposed direction).
    def test_gaps_missing_carbon_card(self):
        self.remove_text(build.PAGE['ACCOUNT'], 'Carbon-Aware Cost')

    def test_gaps_missing_research_question(self):
        self.remove_text(build.PAGE['ACCOUNT'], 'satisfying latency SLOs')

    def test_gaps_hbf_returns(self):
        self.add_text(build.PAGE['ACCOUNT'], 'HBM/HBF capacity, latency and read/write energy', (40, 150))

    def test_gaps_novelty_claim_returns(self):
        self.add_text(build.PAGE['ACCOUNT'], 'Novelty requires further comparison', (40, 150))

    def test_gaps_unsupported_claim_returns(self):
        self.add_text(build.PAGE['ACCOUNT'], 'Heterogeneous GPU carbon optimization is entirely unexplored', (40, 150))

    def test_gaps_old_direction_returns(self):
        self.add_text(build.PAGE['ACCOUNT'], 'Research Direction: Power- and Carbon-Aware Heterogeneous GPU Scheduling', (40, 150))

    # Slide 12 (proposed coordinated architecture).
    def test_architecture_missing_global_scheduler(self):
        self.remove_text(build.PAGE['GEOARCH'], 'Global Carbon-Aware Scheduler')

    def test_architecture_missing_feedback_flow(self):
        self.remove_text(build.PAGE['GEOARCH'], 'Predicted performance')

    def test_architecture_missing_evaluation_caveat(self):
        self.remove_text(build.PAGE['GEOARCH'], 'snapshot freshness')

    def test_architecture_gpu_model_name_returns(self):
        self.add_text(build.PAGE['GEOARCH'], 'Data Center A: A100 and H100', (40, 150))

    def test_architecture_hbf_returns(self):
        self.add_text(build.PAGE['GEOARCH'], 'HBF tier placement', (40, 150))

    # Slide 13 (experimental plan and roadmap).
    def test_plan_missing_profiling_card(self):
        self.remove_text(build.PAGE['ENVIRONMENT'], 'Academia Sinica RCITI GPU Cluster')

    def test_plan_missing_phase(self):
        self.remove_text(build.PAGE['ENVIRONMENT'], 'Phase 3')

    def test_plan_detailed_baselines_return(self):
        self.add_text(build.PAGE['ENVIRONMENT'], 'Baselines: homogeneous GPUs, independent regional routing', (40, 150))

    def test_plan_hbf_comodeling_returns(self):
        self.add_text(build.PAGE['ENVIRONMENT'], 'Workload-Aware HBM/HBF Co-Design', (40, 150))

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
            page = doc[build.PAGE['THUNDER']]
            for im in page.get_image_info():
                page.add_redact_annot(fitz.Rect(im['bbox']))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
        self.reject(mutate)

    def test_missing_hbf_scope_note(self):
        self.remove_text(build.PAGE['PLACEMENTENERGY'], 'Published MoE-based simulation evidence')

    def test_missing_cluster_access_boundary(self):
        self.remove_text(build.PAGE['ENVIRONMENT'], 'cluster access remain to be confirmed')

    def test_missing_helix_figure(self):
        def mutate(doc):
            page = doc[build.PAGE['HELIX']]
            for im in page.get_image_info():
                page.add_redact_annot(fitz.Rect(im['bbox']))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
        self.reject(mutate)

    # Source footers were removed from every slide; a returning footer must be rejected.
    def test_source_footer_returns(self):
        self.add_text(build.PAGE['RELATED'], 'Source: Carbon–SLO, Secs. III-A, III-C.', (40, 240))

    def test_missing_hbf_scope_note_on_slide_9(self):
        self.remove_text(build.PAGE['PLACEMENT'], 'Published MoE-based simulation evidence')

    def test_missing_static_power_note(self):
        self.remove_text(build.PAGE['PLACEMENTENERGY'], 'static/background power excluded')

    def test_wrong_thank_you_position(self):
        self.reject(lambda doc: doc.move_page(build.PAGE['THANKYOU'], build.PAGE['REEL2']))

    def test_wrong_page_count(self):
        self.reject(lambda doc: doc.delete_page(build.PAGE['ENVIRONMENT']))

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NavigationContracts))
    (build.QA/'research-materials-navigation-tests.json').write_text(json.dumps(dict(
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        passed=result.wasSuccessful(), pdf_sha256=build.digest(build.PDF)), indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
