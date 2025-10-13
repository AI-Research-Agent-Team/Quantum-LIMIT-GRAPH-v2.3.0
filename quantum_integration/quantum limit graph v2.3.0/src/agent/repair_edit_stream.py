# -*- coding: utf-8 -*-
"""
REPAIR Edit Stream for Quantum LIMIT-GRAPH v2.3.0
Applies REPAIR edits with dual-memory architecture
Tracks hallucination correction and edit provenance
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class EditType(Enum):
    """Types of REPAIR edits"""
    INSERTION = "insertion"
    DELETION = "deletion"
    SUBSTITUTION = "substitution"
    REORDERING = "reordering"

class HallucinationType(Enum):
    """Types of hallucinations detected"""
    FACTUAL_ERROR = "factual_error"
    ENTITY_MISMATCH = "entity_mismatch"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    UNSUPPORTED_CLAIM = "unsupported_claim"

@dataclass
class Edit:
    """Single REPAIR edit operation"""
    edit_id: str
    edit_type: EditType
    position: int
    original_text: str
    corrected_text: str
    confidence: float
    hallucination_type: Optional[HallucinationType] = None
    provenance: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MemoryEntry:
    """Dual-memory architecture entry"""
    content: str
    memory_type: str  # 'short_term' or 'long_term'
    edit_history: List[Edit] = field(default_factory=list)
    reliability_score: float = 1.0
    last_accessed: datetime = field(default_factory=datetime.now)

class REPAIREditStream:
    """
    REPAIR edit stream with dual-memory architecture
    Tracks hallucination correction and edit provenance
    """
    
    def __init__(self, 
                 short_term_capacity: int = 100,
                 long_term_capacity: int = 1000):
        """
        Initialize REPAIR edit stream
        
        Args:
            short_term_capacity: Max entries in short-term memory
            long_term_capacity: Max entries in long-term memory
        """
        self.short_term_memory: List[MemoryEntry] = []
        self.long_term_memory: List[MemoryEntry] = []
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self.edit_counter = 0
        self.hallucination_stats = {ht: 0 for ht in HallucinationType}
        
    def detect_hallucination(self, text: str, context: Dict) -> Optional[HallucinationType]:
        """
        Detect potential hallucinations in text
        
        Args:
            text: Text to check
            context: Context dictionary with ground truth
            
        Returns:
            Hallucination type if detected, None otherwise
        """
        # Simple heuristic-based detection
        # In production, use trained models
        
        # Check for unsupported claims (no citations)
        if "according to" not in text.lower() and "research shows" in text.lower():
            return HallucinationType.UNSUPPORTED_CLAIM
        
        # Check for entity mismatches
        context_entities = context.get('entities', [])
        if context_entities:
            # Simplified check
            for entity in context_entities:
                if entity.lower() in text.lower():
                    return None
            return HallucinationType.ENTITY_MISMATCH
        
        return None
    
    def create_edit(self,
                   edit_type: EditType,
                   position: int,
                   original: str,
                   corrected: str,
                   confidence: float,
                   hallucination_type: Optional[HallucinationType] = None,
                   provenance: Optional[str] = None) -> Edit:
        """
        Create a new edit operation
        
        Args:
            edit_type: Type of edit
            position: Position in text
            original: Original text
            corrected: Corrected text
            confidence: Confidence score
            hallucination_type: Type of hallucination corrected
            provenance: Source of correction
            
        Returns:
            Edit object
        """
        self.edit_counter += 1
        edit_id = f"edit_{self.edit_counter:06d}"
        
        if hallucination_type:
            self.hallucination_stats[hallucination_type] += 1
        
        return Edit(
            edit_id=edit_id,
            edit_type=edit_type,
            position=position,
            original_text=original,
            corrected_text=corrected,
            confidence=confidence,
            hallucination_type=hallucination_type,
            provenance=provenance
        )
    
    def apply_edit(self, text: str, edit: Edit) -> str:
        """
        Apply single edit to text
        
        Args:
            text: Original text
            edit: Edit to apply
            
        Returns:
            Edited text
        """
        if edit.edit_type == EditType.SUBSTITUTION:
            return text.replace(edit.original_text, edit.corrected_text, 1)
        elif edit.edit_type == EditType.INSERTION:
            return text[:edit.position] + edit.corrected_text + text[edit.position:]
        elif edit.edit_type == EditType.DELETION:
            return text.replace(edit.original_text, "", 1)
        else:
            return text
    
    def apply_edits(self, text: str, context: Dict) -> Dict:
        """
        Apply REPAIR edits to text with hallucination detection
        
        Args:
            text: Input text
            context: Context dictionary
            
        Returns:
            Dictionary with edited text and metadata
        """
        edits_applied = []
        current_text = text
        
        # Detect hallucinations
        hallucination = self.detect_hallucination(text, context)
        
        if hallucination:
            # Create correction edit
            edit = self.create_edit(
                edit_type=EditType.SUBSTITUTION,
                position=0,
                original=text,
                corrected=f"[CORRECTED] {text}",
                confidence=0.85,
                hallucination_type=hallucination,
                provenance=context.get('source', 'unknown')
            )
            
            current_text = self.apply_edit(current_text, edit)
            edits_applied.append(edit)
        
        # Store in dual memory
        memory_entry = MemoryEntry(
            content=current_text,
            memory_type='short_term',
            edit_history=edits_applied,
            reliability_score=1.0 - (0.1 * len(edits_applied))
        )
        
        self.add_to_memory(memory_entry)
        
        return {
            'original_text': text,
            'edited_text': current_text,
            'edits_applied': [
                {
                    'edit_id': e.edit_id,
                    'type': e.edit_type.value,
                    'hallucination': e.hallucination_type.value if e.hallucination_type else None,
                    'confidence': e.confidence,
                    'provenance': e.provenance
                }
                for e in edits_applied
            ],
            'reliability_score': memory_entry.reliability_score,
            'hallucination_detected': hallucination.value if hallucination else None
        }
    
    def add_to_memory(self, entry: MemoryEntry):
        """
        Add entry to dual-memory architecture
        
        Args:
            entry: Memory entry to add
        """
        # Add to short-term memory
        self.short_term_memory.append(entry)
        
        # Manage capacity
        if len(self.short_term_memory) > self.short_term_capacity:
            # Move oldest high-reliability entries to long-term
            reliable_entries = [
                e for e in self.short_term_memory
                if e.reliability_score > 0.8
            ]
            
            if reliable_entries:
                oldest = min(reliable_entries, key=lambda e: e.last_accessed)
                oldest.memory_type = 'long_term'
                self.long_term_memory.append(oldest)
                self.short_term_memory.remove(oldest)
            else:
                # Remove oldest entry
                self.short_term_memory.pop(0)
        
        # Manage long-term capacity
        if len(self.long_term_memory) > self.long_term_capacity:
            self.long_term_memory.pop(0)
    
    def get_edit_provenance(self, edit_id: str) -> Optional[Dict]:
        """
        Get full provenance for an edit
        
        Args:
            edit_id: Edit identifier
            
        Returns:
            Provenance dictionary
        """
        for memory in self.short_term_memory + self.long_term_memory:
            for edit in memory.edit_history:
                if edit.edit_id == edit_id:
                    return {
                        'edit_id': edit.edit_id,
                        'type': edit.edit_type.value,
                        'timestamp': edit.timestamp.isoformat(),
                        'hallucination_type': edit.hallucination_type.value if edit.hallucination_type else None,
                        'provenance': edit.provenance,
                        'confidence': edit.confidence,
                        'memory_type': memory.memory_type
                    }
        return None
    
    def get_statistics(self) -> Dict:
        """Get edit stream statistics"""
        return {
            'total_edits': self.edit_counter,
            'short_term_entries': len(self.short_term_memory),
            'long_term_entries': len(self.long_term_memory),
            'hallucination_stats': {
                ht.value: count
                for ht, count in self.hallucination_stats.items()
            },
            'avg_reliability': np.mean([
                e.reliability_score
                for e in self.short_term_memory + self.long_term_memory
            ]) if (self.short_term_memory or self.long_term_memory) else 0.0
        }


def apply_edits(traversal_path: Dict, 
                edit_stream: Optional[REPAIREditStream] = None) -> Dict:
    """
    Convenience function for applying REPAIR edits
    
    Args:
        traversal_path: Traversal result dictionary
        edit_stream: Optional pre-configured edit stream
        
    Returns:
        Final output with edits applied
    """
    if edit_stream is None:
        edit_stream = REPAIREditStream()
    
    # Extract text from traversal path
    path = traversal_path.get('path', [])
    text = " -> ".join(path)
    
    # Create context
    context = {
        'entities': path,
        'source': 'quantum_traversal',
        'coherence': traversal_path.get('coherence', 0.0)
    }
    
    # Apply edits
    result = edit_stream.apply_edits(text, context)
    result['traversal_info'] = traversal_path
    result['statistics'] = edit_stream.get_statistics()
    
    return result


# Import numpy for statistics
import numpy as np
