# -*- coding: utf-8 -*-
"""
ACE Context Router for Quantum LIMIT-GRAPH v2.3.0
Routes context across global/domain/language layers
Adjusts similarity thresholds dynamically (0.70–0.95)
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum

class ContextLayer(Enum):
    """Context layer types"""
    GLOBAL = "global"
    DOMAIN = "domain"
    LANGUAGE = "language"

@dataclass
class ContextEntry:
    """Single context entry"""
    content: str
    layer: ContextLayer
    embedding: np.ndarray
    language: str
    domain: Optional[str] = None
    metadata: Optional[Dict] = None

class ACEContextRouter:
    """
    Routes context across hierarchical layers with dynamic threshold adjustment
    """
    
    def __init__(self, 
                 base_threshold: float = 0.80,
                 threshold_range: Tuple[float, float] = (0.70, 0.95)):
        """
        Initialize ACE context router
        
        Args:
            base_threshold: Base similarity threshold
            threshold_range: Min and max threshold values
        """
        self.base_threshold = base_threshold
        self.min_threshold, self.max_threshold = threshold_range
        self.context_store: Dict[ContextLayer, List[ContextEntry]] = {
            ContextLayer.GLOBAL: [],
            ContextLayer.DOMAIN: [],
            ContextLayer.LANGUAGE: []
        }
        
    def add_context(self, entry: ContextEntry):
        """Add context entry to appropriate layer"""
        self.context_store[entry.layer].append(entry)
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
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
        
        return np.dot(emb1, emb2) / (norm1 * norm2)
    
    def adjust_threshold(self, 
                        layer: ContextLayer,
                        query_complexity: float,
                        language_match: bool) -> float:
        """
        Dynamically adjust similarity threshold
        
        Args:
            layer: Context layer
            query_complexity: Query complexity score (0.0 to 1.0)
            language_match: Whether language matches
            
        Returns:
            Adjusted threshold
        """
        threshold = self.base_threshold
        
        # Layer-specific adjustments
        if layer == ContextLayer.GLOBAL:
            threshold += 0.05  # Higher threshold for global context
        elif layer == ContextLayer.LANGUAGE:
            threshold -= 0.05  # Lower threshold for language-specific
        
        # Complexity adjustment
        threshold += (query_complexity - 0.5) * 0.1
        
        # Language match bonus
        if language_match:
            threshold -= 0.03
        
        # Clamp to valid range
        return np.clip(threshold, self.min_threshold, self.max_threshold)
    
    def route_context(self, 
                     query_embedding: np.ndarray,
                     query_language: str,
                     query_domain: Optional[str] = None,
                     query_complexity: float = 0.5,
                     top_k: int = 5) -> Dict[ContextLayer, List[Tuple[ContextEntry, float]]]:
        """
        Route and retrieve relevant context from all layers
        
        Args:
            query_embedding: Query embedding vector
            query_language: Query language code
            query_domain: Optional domain identifier
            query_complexity: Query complexity score
            top_k: Number of results per layer
            
        Returns:
            Dictionary mapping layers to retrieved context entries with scores
        """
        results = {}
        
        for layer in ContextLayer:
            layer_results = []
            
            # Get threshold for this layer
            language_match = (layer == ContextLayer.LANGUAGE)
            threshold = self.adjust_threshold(layer, query_complexity, language_match)
            
            # Search in layer
            for entry in self.context_store[layer]:
                # Language filtering for language layer
                if layer == ContextLayer.LANGUAGE and entry.language != query_language:
                    continue
                
                # Domain filtering for domain layer
                if layer == ContextLayer.DOMAIN and query_domain:
                    if entry.domain != query_domain:
                        continue
                
                # Compute similarity
                similarity = self.compute_similarity(query_embedding, entry.embedding)
                
                # Apply threshold
                if similarity >= threshold:
                    layer_results.append((entry, similarity))
            
            # Sort by similarity and take top-k
            layer_results.sort(key=lambda x: x[1], reverse=True)
            results[layer] = layer_results[:top_k]
        
        return results
    
    def merge_context(self, 
                     routed_context: Dict[ContextLayer, List[Tuple[ContextEntry, float]]],
                     max_tokens: int = 2048) -> str:
        """
        Merge context from multiple layers into final context string
        
        Args:
            routed_context: Routed context from all layers
            max_tokens: Maximum context length in tokens (approximate)
            
        Returns:
            Merged context string
        """
        context_parts = []
        token_count = 0
        
        # Priority order: Language > Domain > Global
        layer_priority = [ContextLayer.LANGUAGE, ContextLayer.DOMAIN, ContextLayer.GLOBAL]
        
        for layer in layer_priority:
            entries = routed_context.get(layer, [])
            
            for entry, score in entries:
                # Approximate token count (4 chars per token)
                entry_tokens = len(entry.content) // 4
                
                if token_count + entry_tokens > max_tokens:
                    break
                
                context_parts.append(f"[{layer.value}|{score:.3f}] {entry.content}")
                token_count += entry_tokens
            
            if token_count >= max_tokens:
                break
        
        return "\n\n".join(context_parts)
    
    def get_layer_stats(self) -> Dict[str, int]:
        """Get statistics about context store"""
        return {
            layer.value: len(entries)
            for layer, entries in self.context_store.items()
        }


def route_context(tokens: Dict, 
                 query_embedding: Optional[np.ndarray] = None,
                 router: Optional[ACEContextRouter] = None) -> Dict:
    """
    Convenience function for context routing
    
    Args:
        tokens: Tokenized query dictionary
        query_embedding: Optional query embedding
        router: Optional pre-configured router
        
    Returns:
        Routed context dictionary
    """
    if router is None:
        router = ACEContextRouter()
    
    # Create dummy embedding if not provided
    if query_embedding is None:
        query_embedding = np.random.randn(768)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
    
    # Extract language from tokens
    language = tokens.get('language', 'en')
    
    # Route context
    routed = router.route_context(
        query_embedding=query_embedding,
        query_language=language,
        query_complexity=0.5,
        top_k=3
    )
    
    # Merge context
    merged_context = router.merge_context(routed)
    
    return {
        'routed_context': routed,
        'merged_context': merged_context,
        'layer_stats': router.get_layer_stats(),
        'language': language
    }
