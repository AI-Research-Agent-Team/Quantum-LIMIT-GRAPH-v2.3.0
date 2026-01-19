"""
Multilingual Test Suite
Uses YOUR multilingual_parser.py as the gold standard for evaluation
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime

# Import YOUR quantum modules as gold standard
try:
    from quantum_integration.multilingual_parser import (
        detect_language,
        parse_query,
        normalize_text
    )
    QUANTUM_MODULES_AVAILABLE = True
except ImportError:
    print("⚠️ Quantum integration modules not available, using mocks")
    QUANTUM_MODULES_AVAILABLE = False
    
    def detect_language(text): return "en"
    def parse_query(text, lang="en"): return text.split()
    def normalize_text(text): return text.lower()


class MultilingualTestSuite:
    """
    Tests agent's multilingual capabilities using YOUR parser as gold standard
    
    Your multilingual_parser.py becomes the reference implementation.
    We test if purple agents can match your:
    - Language detection accuracy
    - Tokenization quality  
    - Cross-lingual consistency
    """
    
    def __init__(self):
        self.name = "Multilingual NLP Evaluation"
        
        # YOUR modules = gold standard
        self.reference_detector = detect_language
        self.reference_parser = parse_query
        self.reference_normalizer = normalize_text
        
        # Test queries in 15+ languages
        self.test_queries = [
            # English
            {"text": "What are recent advances in quantum machine learning?", "lang": "en"},
            {"text": "How does QAOA improve graph traversal efficiency?", "lang": "en"},
            
            # Spanish
            {"text": "¿Cuáles son los avances recientes en aprendizaje automático cuántico?", "lang": "es"},
            {"text": "¿Cómo mejora QAOA la eficiencia del recorrido de grafos?", "lang": "es"},
            
            # French
            {"text": "Quelles sont les avancées récentes dans l'apprentissage automatique quantique?", "lang": "fr"},
            
            # German
            {"text": "Was sind die neuesten Fortschritte im quantenmaschinellen Lernen?", "lang": "de"},
            
            # Chinese
            {"text": "量子机器学习的最新进展是什么？", "lang": "zh"},
            {"text": "QAOA如何提高图遍历效率？", "lang": "zh"},
            
            # Japanese
            {"text": "量子機械学習における最近の進歩は何ですか？", "lang": "ja"},
            
            # Korean
            {"text": "양자 기계 학습의 최근 발전은 무엇입니까?", "lang": "ko"},
            
            # Arabic
            {"text": "ما هي التطورات الأخيرة في التعلم الآلي الكمي؟", "lang": "ar"},
            
            # Hindi
            {"text": "क्वांटम मशीन लर्निंग में हालिया प्रगति क्या हैं?", "lang": "hi"},
            
            # Indonesian
            {"text": "Apa perkembangan terbaru dalam pembelajaran mesin kuantum?", "lang": "id"},
            
            # Portuguese
            {"text": "Quais são os avanços recentes em aprendizado de máquina quântico?", "lang": "pt"},
            
            # Russian
            {"text": "Каковы последние достижения в квантовом машинном обучении?", "lang": "ru"},
            
            # Vietnamese
            {"text": "Những tiến bộ gần đây trong học máy lượng tử là gì?", "lang": "vi"},
            
            # Thai
            {"text": "ความก้าวหน้าล่าสุดในการเรียนรู้ของเครื่องควอนตัมคืออะไร?", "lang": "th"},
            
            # Turkish
            {"text": "Kuantum makine öğrenmesindeki son gelişmeler nelerdir?", "lang": "tr"}
        ]
    
    async def evaluate(self, purple_agent, config: Dict) -> Dict[str, Any]:
        """
        Evaluate purple agent's multilingual capabilities
        
        Tests:
        1. Language Detection: Can they detect languages as well as YOUR parser?
        2. Tokenization: Do their tokens match YOUR parser's quality?
        3. Cross-lingual: Are they consistent across languages like YOUR parser?
        
        Args:
            purple_agent: Purple agent proxy (A2A client)
            config: Test configuration
            
        Returns:
            Evaluation results with scores
        """
        results = {
            "suite": "multilingual",
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(self.test_queries),
            "tests_passed": 0,
            "scores": {
                "language_detection": 0.0,
                "tokenization_quality": 0.0,
                "cross_lingual_consistency": 0.0
            },
            "metrics": {},
            "details": []
        }
        
        detection_scores = []
        tokenization_scores = []
        consistency_scores = defaultdict(list)
        
        # Run tests
        for idx, test in enumerate(self.test_queries):
            query_text = test["text"]
            expected_lang = test["lang"]
            
            try:
                # 1. Test Language Detection
                # YOUR parser detects the language (gold standard)
                our_detected_lang = self.reference_detector(query_text)
                
                # Get purple agent's response
                purple_response = await purple_agent.query(query_text)
                
                # Did purple agent detect language correctly?
                # (We infer from their response characteristics)
                agent_lang_correct = self._infer_language_detection(
                    purple_response, 
                    expected_lang
                )
                
                detection_score = 1.0 if agent_lang_correct else 0.0
                detection_scores.append(detection_score)
                
                # 2. Test Tokenization Quality
                # YOUR parser's tokenization (gold standard)
                our_tokens = self.reference_parser(query_text, lang=expected_lang)
                
                # Compare purple agent's response quality
                token_quality_score = self._evaluate_token_quality(
                    purple_response,
                    our_tokens,
                    expected_lang
                )
                
                tokenization_scores.append(token_quality_score)
                
                # 3. Cross-lingual consistency
                consistency_scores[expected_lang].append(
                    self._evaluate_consistency(purple_response, expected_lang)
                )
                
                # Record details
                results["details"].append({
                    "test_id": idx,
                    "query": query_text[:50] + "...",
                    "expected_lang": expected_lang,
                    "detected_correctly": agent_lang_correct,
                    "token_quality": token_quality_score,
                    "passed": detection_score > 0.5 and token_quality_score > 0.5
                })
                
                if detection_score > 0.5 and token_quality_score > 0.5:
                    results["tests_passed"] += 1
                
            except Exception as e:
                results["details"].append({
                    "test_id": idx,
                    "query": query_text[:50] + "...",
                    "error": str(e),
                    "passed": False
                })
        
        # Calculate scores
        results["scores"]["language_detection"] = (
            sum(detection_scores) / len(detection_scores) 
            if detection_scores else 0.0
        )
        
        results["scores"]["tokenization_quality"] = (
            sum(tokenization_scores) / len(tokenization_scores) 
            if tokenization_scores else 0.0
        )
        
        # Cross-lingual consistency: variance across languages
        lang_scores = [
            sum(scores) / len(scores) 
            for scores in consistency_scores.values() 
            if scores
        ]
        results["scores"]["cross_lingual_consistency"] = (
            sum(lang_scores) / len(lang_scores) 
            if lang_scores else 0.0
        )
        
        # Overall score (weighted average)
        results["score"] = (
            results["scores"]["language_detection"] * 0.4 +
            results["scores"]["tokenization_quality"] * 0.3 +
            results["scores"]["cross_lingual_consistency"] * 0.3
        )
        
        # Metrics
        results["metrics"] = {
            "languages_tested": len(set(t["lang"] for t in self.test_queries)),
            "pass_rate": results["tests_passed"] / results["total_tests"],
            "average_detection_accuracy": results["scores"]["language_detection"]
        }
        
        return results
    
    def _infer_language_detection(self, response: str, expected_lang: str) -> bool:
        """
        Infer if purple agent detected language correctly
        
        We check if their response:
        - Uses correct language
        - Has appropriate structure
        - Shows understanding of query language
        """
        if not response:
            return False
        
        # Simple heuristic: detect language in their response
        response_lang = self.reference_detector(response)
        
        # Purple agent should respond in same or related language
        return response_lang == expected_lang or response_lang == "en"
    
    def _evaluate_token_quality(
        self, 
        response: str, 
        our_tokens: List[str],
        lang: str
    ) -> float:
        """
        Evaluate tokenization quality compared to YOUR parser
        
        Checks:
        - Response completeness
        - Token-like structure
        - Language-appropriate formatting
        """
        if not response:
            return 0.0
        
        # Heuristic scoring based on response characteristics
        score = 0.0
        
        # Check response length (should be substantial)
        if len(response) > 50:
            score += 0.3
        
        # Check if response contains key terms from query
        # (indicates good tokenization understanding)
        response_lower = response.lower()
        key_term_present = any(
            term.lower() in response_lower 
            for term in our_tokens[:5]  # Check first few tokens
        )
        if key_term_present:
            score += 0.4
        
        # Check language-appropriate structure
        if lang in ["zh", "ja", "ko"]:  # Asian languages
            # Should not have excessive spaces
            if response.count(" ") / max(len(response), 1) < 0.2:
                score += 0.3
        else:
            # Should have reasonable word spacing
            if 0.1 < response.count(" ") / max(len(response), 1) < 0.3:
                score += 0.3
        
        return min(1.0, score)
    
    def _evaluate_consistency(self, response: str, lang: str) -> float:
        """Evaluate response consistency for language"""
        if not response:
            return 0.0
        
        # Check if response is coherent and substantial
        score = 0.5  # Base score
        
        if len(response) > 100:
            score += 0.3
        
        if len(response.split()) > 10:
            score += 0.2
        
        return min(1.0, score)


from collections import defaultdict  # Add missing import
