# -*- coding: utf-8 -*-
"""
Cross-Lingual Alignment Scoring for Quantum LIMIT-GRAPH v2.3.0
Computes alignment using entity linking and semantic overlap
"""

from typing import Dict, List, Set, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class AlignmentResult:
    """Cross-lingual alignment result"""
    source_lang: str
    target_lang: str
    entity_overlap: float
    semantic_similarity: float
    structural_alignment: float
    overall_score: float

class CrossLingualAlignmentScorer:
    """
    Computes cross-lingual alignment scores using multiple metrics
    """
    
    def __init__(self):
        """Initialize alignment scorer"""
        # Common entities across languages (simplified)
        self.universal_entities = {
            'quantum', 'machine learning', 'computer', 'algorithm',
            'data', 'model', 'network', 'system'
        }
        
    def extract_entities(self, text: str, lang: str) -> Set[str]:
        """
        Extract entities from text
        
        Args:
            text: Input text
            lang: Language code
            
        Returns:
            Set of extracted entities
        """
        # Simplified entity extraction
        # In production, use NER models
        entities = set()
        
        text_lower = text.lower()
        for entity in self.universal_entities:
            if entity in text_lower:
                entities.add(entity)
        
        return entities
    
    def compute_entity_overlap(self, 
                              entities1: Set[str],
                              entities2: Set[str]) -> float:
        """
        Compute Jaccard similarity between entity sets
        
        Args:
            entities1: First entity set
            entities2: Second entity set
            
        Returns:
            Overlap score (0.0 to 1.0)
        """
        if not entities1 and not entities2:
            return 1.0
        
        if not entities1 or not entities2:
            return 0.0
        
        intersection = len(entities1 & entities2)
        union = len(entities1 | entities2)
        
        return intersection / union if union > 0 else 0.0
    
    def compute_semantic_similarity(self,
                                   emb1: np.ndarray,
                                   emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between embeddings
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        
        # Normalize to [0, 1]
        return (similarity + 1.0) / 2.0
    
    def compute_structural_alignment(self,
                                    tokens1: List[str],
                                    tokens2: List[str]) -> float:
        """
        Compute structural alignment based on token sequences
        
        Args:
            tokens1: First token sequence
            tokens2: Second token sequence
            
        Returns:
            Alignment score (0.0 to 1.0)
        """
        # Use longest common subsequence ratio
        len1, len2 = len(tokens1), len(tokens2)
        
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Dynamic programming for LCS
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if tokens1[i-1] == tokens2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[len1][len2]
        
        # Normalize by average length
        avg_length = (len1 + len2) / 2.0
        return lcs_length / avg_length if avg_length > 0 else 0.0
    
    def compute_alignment(self,
                         text1: str,
                         text2: str,
                         lang1: str,
                         lang2: str,
                         emb1: Optional[np.ndarray] = None,
                         emb2: Optional[np.ndarray] = None) -> AlignmentResult:
        """
        Compute comprehensive cross-lingual alignment
        
        Args:
            text1: First text
            text2: Second text
            lang1: First language code
            lang2: Second language code
            emb1: Optional embedding for text1
            emb2: Optional embedding for text2
            
        Returns:
            Alignment result
        """
        # Extract entities
        entities1 = self.extract_entities(text1, lang1)
        entities2 = self.extract_entities(text2, lang2)
        
        # Compute entity overlap
        entity_overlap = self.compute_entity_overlap(entities1, entities2)
        
        # Compute semantic similarity
        if emb1 is not None and emb2 is not None:
            semantic_sim = self.compute_semantic_similarity(emb1, emb2)
        else:
            # Generate random embeddings for demo
            emb1 = np.random.randn(768)
            emb2 = np.random.randn(768)
            semantic_sim = self.compute_semantic_similarity(emb1, emb2)
        
        # Compute structural alignment
        tokens1 = text1.lower().split()
        tokens2 = text2.lower().split()
        structural = self.compute_structural_alignment(tokens1, tokens2)
        
        # Weighted overall score
        overall = (
            0.4 * entity_overlap +
            0.4 * semantic_sim +
            0.2 * structural
        )
        
        return AlignmentResult(
            source_lang=lang1,
            target_lang=lang2,
            entity_overlap=entity_overlap,
            semantic_similarity=semantic_sim,
            structural_alignment=structural,
            overall_score=overall
        )
    
    def batch_alignment(self,
                       texts: Dict[str, str],
                       embeddings: Optional[Dict[str, np.ndarray]] = None) -> List[AlignmentResult]:
        """
        Compute pairwise alignments for multiple texts
        
        Args:
            texts: Dictionary mapping language codes to texts
            embeddings: Optional embeddings for each text
            
        Returns:
            List of alignment results
        """
        results = []
        langs = list(texts.keys())
        
        for i in range(len(langs)):
            for j in range(i + 1, len(langs)):
                lang1, lang2 = langs[i], langs[j]
                text1, text2 = texts[lang1], texts[lang2]
                
                emb1 = embeddings.get(lang1) if embeddings else None
                emb2 = embeddings.get(lang2) if embeddings else None
                
                result = self.compute_alignment(text1, text2, lang1, lang2, emb1, emb2)
                results.append(result)
        
        return results


def compute_alignment_score(text1: str, text2: str, lang1: str, lang2: str) -> float:
    """
    Convenience function for computing alignment score
    
    Args:
        text1: First text
        text2: Second text
        lang1: First language
        lang2: Second language
        
    Returns:
        Overall alignment score
    """
    scorer = CrossLingualAlignmentScorer()
    result = scorer.compute_alignment(text1, text2, lang1, lang2)
    return result.overall_score


# Import Optional
from typing import Optional
