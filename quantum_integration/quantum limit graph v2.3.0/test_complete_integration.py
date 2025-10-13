# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Complete Integration Test Suite for Quantum LIMIT-GRAPH v2.3.0
Tests all components end-to-end
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import unittest
import numpy as np
import networkx as nx
from src.agent.multilingual_parser import MultilingualParser, parse_query
from src.graph.quantum_traversal import QuantumGraphTraversal, traverse_graph
from src.context.ace_context_router import ACEContextRouter, ContextLayer, ContextEntry, route_context
from src.agent.repair_edit_stream import REPAIREditStream, EditType, apply_edits
from src.evaluation.alignment_score import CrossLingualAlignmentScorer
from src.evaluation.layer_balance_test import LayerBalanceTest


class TestMultilingualParser(unittest.TestCase):
    """Test multilingual parsing functionality"""
    
    def setUp(self):
        self.parser = MultilingualParser()
    
    def test_language_detection(self):
        """Test language detection across multiple languages"""
        test_cases = [
            ('Hello world', 'en'),
            ('你好世界', 'zh'),
            ('مرحبا بالعالم', 'ar'),
            ('こんにちは世界', 'ja'),
            ('안녕하세요 세계', 'ko')
        ]
        
        for text, expected_lang in test_cases:
            detected = self.parser.detect_language(text)
            self.assertEqual(detected, expected_lang, 
                           f"Failed to detect {expected_lang} in '{text}'")
    
    def test_text_normalization(self):
        """Test text normalization"""
        text = "  Multiple   spaces  "
        normalized = self.parser.normalize_text(text, 'en')
        self.assertEqual(normalized, "Multiple spaces")
    
    def test_subgraph_routing(self):
        """Test language-to-subgraph routing"""
        routes = {
            'en': 'latin_western',
            'zh': 'cjk',
            'ar': 'rtl_semitic',
            'hi': 'indic'
        }
        
        for lang, expected_subgraph in routes.items():
            subgraph = self.parser.route_to_subgraph(lang)
            self.assertEqual(subgraph, expected_subgraph)
    
    def test_complete_parsing(self):
        """Test complete parsing pipeline"""
        query = "What is quantum computing?"
        result = self.parser.parse_query(query, 'en')
        
        self.assertIn('original', result)
        self.assertIn('normalized', result)
        self.assertIn('language', result)
        self.assertIn('tokens', result)
        self.assertIn('subgraph', result)
        self.assertEqual(result['language'], 'en')


class TestQuantumTraversal(unittest.TestCase):
    """Test quantum graph traversal"""
    
    def setUp(self):
        # Create test graph
        self.graph = nx.Graph()
        nodes = ['A', 'B', 'C', 'D', 'E']
        for node in nodes:
            self.graph.add_node(node)
        
        edges = [
            ('A', 'B', 0.8, 'semantic'),
            ('B', 'C', 0.9, 'citation'),
            ('C', 'D', 0.7, 'semantic'),
            ('D', 'E', 0.85, 'citation'),
            ('A', 'C', 0.6, 'semantic')
        ]
        
        for src, dst, weight, edge_type in edges:
            self.graph.add_edge(src, dst, weight=weight, type=edge_type)
        
        self.traversal = QuantumGraphTraversal(self.graph, use_quantum=False)
    
    def test_semantic_coherence(self):
        """Test semantic coherence computation"""
        path = ['A', 'B', 'C']
        coherence = self.traversal.compute_semantic_coherence(path)
        self.assertGreater(coherence, 0.0)
        self.assertLessEqual(coherence, 1.0)
    
    def test_citation_walk(self):
        """Test citation-based walk"""
        citations = self.traversal.citation_walk('B', max_depth=2)
        self.assertIn('B', citations)
        self.assertGreater(len(citations), 0)
    
    def test_classical_traversal(self):
        """Test classical traversal"""
        path, cost = self.traversal.classical_traversal('A', 'E')
        self.assertIn('A', path)
        self.assertIn('E', path)
        self.assertGreater(len(path), 1)
    
    def test_complete_traversal(self):
        """Test complete traversal with all features"""
        result = self.traversal.traverse('A', 'E', use_citations=True)
        
        self.assertIn('path', result)
        self.assertIn('citations', result)
        self.assertIn('coherence', result)
        self.assertIn('method', result)
        self.assertIn('latency_ms', result)


class TestACEContextRouter(unittest.TestCase):
    """Test ACE context routing"""
    
    def setUp(self):
        self.router = ACEContextRouter()
        
        # Add test entries
        for layer in ContextLayer:
            for i in range(5):
                embedding = np.random.randn(768)
                embedding = embedding / np.linalg.norm(embedding)
                
                entry = ContextEntry(
                    content=f"Test content {i} for {layer.value}",
                    layer=layer,
                    embedding=embedding,
                    language='en',
                    domain='test' if layer == ContextLayer.DOMAIN else None
                )
                
                self.router.add_context(entry)
    
    def test_similarity_computation(self):
        """Test similarity computation"""
        emb1 = np.array([1.0, 0.0, 0.0])
        emb2 = np.array([1.0, 0.0, 0.0])
        similarity = self.router.compute_similarity(emb1, emb2)
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_threshold_adjustment(self):
        """Test dynamic threshold adjustment"""
        threshold = self.router.adjust_threshold(
            ContextLayer.GLOBAL,
            query_complexity=0.7,
            language_match=True
        )
        self.assertGreaterEqual(threshold, self.router.min_threshold)
        self.assertLessEqual(threshold, self.router.max_threshold)
    
    def test_context_routing(self):
        """Test context routing across layers"""
        query_emb = np.random.randn(768)
        query_emb = query_emb / np.linalg.norm(query_emb)
        
        results = self.router.route_context(
            query_embedding=query_emb,
            query_language='en',
            query_complexity=0.5,
            top_k=3
        )
        
        self.assertEqual(len(results), 3)  # 3 layers
        for layer in ContextLayer:
            self.assertIn(layer, results)
    
    def test_context_merging(self):
        """Test context merging"""
        query_emb = np.random.randn(768)
        query_emb = query_emb / np.linalg.norm(query_emb)
        
        routed = self.router.route_context(
            query_embedding=query_emb,
            query_language='en',
            top_k=2
        )
        
        merged = self.router.merge_context(routed, max_tokens=1000)
        self.assertIsInstance(merged, str)
        self.assertGreater(len(merged), 0)


class TestREPAIREditStream(unittest.TestCase):
    """Test REPAIR edit stream"""
    
    def setUp(self):
        self.edit_stream = REPAIREditStream()
    
    def test_hallucination_detection(self):
        """Test hallucination detection"""
        text = "Research shows quantum computers are faster."
        context = {'entities': []}
        
        hallucination = self.edit_stream.detect_hallucination(text, context)
        self.assertIsNotNone(hallucination)
    
    def test_edit_creation(self):
        """Test edit creation"""
        edit = self.edit_stream.create_edit(
            edit_type=EditType.SUBSTITUTION,
            position=0,
            original='old',
            corrected='new',
            confidence=0.9
        )
        
        self.assertEqual(edit.edit_type, EditType.SUBSTITUTION)
        self.assertEqual(edit.confidence, 0.9)
        self.assertIsNotNone(edit.edit_id)
    
    def test_edit_application(self):
        """Test edit application"""
        text = "The cat is fast."
        edit = self.edit_stream.create_edit(
            edit_type=EditType.SUBSTITUTION,
            position=0,
            original='fast',
            corrected='quick',
            confidence=0.9
        )
        
        result = self.edit_stream.apply_edit(text, edit)
        self.assertIn('quick', result)
    
    def test_memory_management(self):
        """Test dual-memory architecture"""
        for i in range(150):
            self.edit_stream.apply_edits(
                f'Test text {i}',
                {'entities': ['test'], 'source': 'test'}
            )
        
        stats = self.edit_stream.get_statistics()
        self.assertLessEqual(stats['short_term_entries'], 
                           self.edit_stream.short_term_capacity)
        self.assertLessEqual(stats['long_term_entries'],
                           self.edit_stream.long_term_capacity)
    
    def test_edit_provenance(self):
        """Test edit provenance tracking"""
        result = self.edit_stream.apply_edits(
            'Test text',
            {'entities': [], 'source': 'test'}
        )
        
        for edit_info in result['edits_applied']:
            provenance = self.edit_stream.get_edit_provenance(edit_info['edit_id'])
            self.assertIsNotNone(provenance)
            self.assertIn('edit_id', provenance)
            self.assertIn('provenance', provenance)


class TestCrossLingualAlignment(unittest.TestCase):
    """Test cross-lingual alignment scoring"""
    
    def setUp(self):
        self.scorer = CrossLingualAlignmentScorer()
    
    def test_entity_extraction(self):
        """Test entity extraction"""
        text = "Quantum machine learning algorithms"
        entities = self.scorer.extract_entities(text, 'en')
        self.assertGreater(len(entities), 0)
    
    def test_entity_overlap(self):
        """Test entity overlap computation"""
        entities1 = {'quantum', 'computer'}
        entities2 = {'quantum', 'machine'}
        
        overlap = self.scorer.compute_entity_overlap(entities1, entities2)
        self.assertGreater(overlap, 0.0)
        self.assertLessEqual(overlap, 1.0)
    
    def test_alignment_computation(self):
        """Test complete alignment computation"""
        text1 = "Quantum computing is powerful"
        text2 = "La computación cuántica es poderosa"
        
        result = self.scorer.compute_alignment(text1, text2, 'en', 'es')
        
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 1.0)
        self.assertEqual(result.source_lang, 'en')
        self.assertEqual(result.target_lang, 'es')


class TestEndToEndIntegration(unittest.TestCase):
    """Test complete end-to-end integration"""
    
    def test_complete_pipeline(self):
        """Test complete pipeline from query to output"""
        # 1. Parse query
        query = "What are quantum algorithms?"
        parsed = parse_query(query, 'en')
        self.assertEqual(parsed['language'], 'en')
        
        # 2. Route context
        query_emb = np.random.randn(768)
        query_emb = query_emb / np.linalg.norm(query_emb)
        context = route_context(parsed, query_emb)
        self.assertIn('merged_context', context)
        
        # 3. Traverse graph
        test_graph = nx.Graph()
        test_graph.add_edge('A', 'B', weight=0.8, type='semantic')
        test_graph.add_edge('B', 'C', weight=0.9, type='citation')
        
        context['start_node'] = 'A'
        context['target_node'] = 'C'
        traversal = traverse_graph(context, test_graph)
        self.assertIn('path', traversal)
        
        # 4. Apply edits
        final = apply_edits(traversal)
        self.assertIn('edited_text', final)
        self.assertIn('statistics', final)


def run_tests():
    """Run all tests"""
    print("="*60)
    print("Quantum LIMIT-GRAPH v2.3.0 - Complete Integration Tests")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMultilingualParser))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumTraversal))
    suite.addTests(loader.loadTestsFromTestCase(TestACEContextRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestREPAIREditStream))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossLingualAlignment))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
