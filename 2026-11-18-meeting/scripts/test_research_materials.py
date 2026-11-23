#!/usr/bin/env python3
"""Mutation checks for the current 20-page Research Materials deck contracts."""
import json
import unittest
import pymupdf as fitz
import build_research_materials as build

class DeckContracts(unittest.TestCase):
    def rejects(self, mutate):
        with fitz.open(build.PDF) as original:
            mutate(original)
            with fitz.open(stream=original.tobytes(), filetype='pdf') as changed:
                with self.assertRaises(AssertionError): build.validate(changed)

    def remove_phrase(self, label, phrase):
        def mutate(doc):
            page=doc[build.PAGE[label]]
            boxes=page.search_for(phrase)
            self.assertTrue(boxes,phrase)
            for box in boxes: page.add_redact_annot(box)
            page.apply_redactions()
        self.rejects(mutate)

    def test_valid_deck(self):
        with fitz.open(build.PDF) as doc: self.assertEqual(build.validate(doc),28)

    def test_page_count(self): self.rejects(lambda doc: doc.delete_page(7))
    def test_contents_destination(self):
        def mutate(doc):
            link=next(x for x in doc[1].get_links() if x.get('nameddest')=='WORKLOAD')
            doc.xref_set_key(link['xref'],'A/D','(GEO)')
        self.rejects(mutate)
    def test_thank_you_position(self): self.remove_phrase('THANKYOU','Thank you')
    def test_main_idea_required(self): self.remove_phrase('HELIX','Use max-flow-based layer placement')
    def test_prism_memory_method_required(self): self.remove_phrase('PRISM','Memory ballooning')
    def test_first_goal_required(self): self.remove_phrase('PRISM','Goal: SLO attainment')
    def test_scepsy_allocation_required(self): self.remove_phrase('PRISM','give each LLM GPUs in proportion')
    def test_second_goal_required(self): self.remove_phrase('PRISM','Goal: latency at target throughput')
    def test_workload_evidence_required(self): self.remove_phrase('WORKLOAD','Repeated context')
    def test_research_gap_required(self): self.remove_phrase('ACCOUNT','Prism and Scepsy address multi-model sharing')
    def test_slide_7_extra_text_rejected(self):
        def mutate(doc): doc[build.PAGE['PRISM']].insert_text((40,150),'Main Idea',fontsize=10)
        self.rejects(mutate)
    def test_environment_required(self): self.remove_phrase('ENVIRONMENT','Academia Sinica CITI GPU Cluster')
    def test_hbf_evidence_note_required(self): self.remove_phrase('PLACEMENTENERGY','Published MoE-based simulation evidence')
    def test_static_power_note_required(self): self.remove_phrase('PLACEMENTENERGY','static/background power excluded')
    def test_reel_value_required(self): self.remove_phrase('REEL2','225.9')
    def test_backup_round_trip_required(self):
        def mutate(doc):
            p=doc[build.PAGE['MEMORYSOURCES']]
            for link in p.get_links():
                if link.get('nameddest')=='MEMORY': p.delete_link(link)
        self.rejects(mutate)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeckContracts))
    (build.QA/'research-materials-navigation-tests.json').write_text(json.dumps(dict(
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        passed=result.wasSuccessful(), pdf_sha256=build.sha(build.PDF)),indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
