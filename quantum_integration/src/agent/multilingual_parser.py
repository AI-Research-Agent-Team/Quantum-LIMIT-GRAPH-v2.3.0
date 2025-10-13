# -*- coding: utf-8 -*-
"""
Multilingual Parser for Quantum LIMIT-GRAPH v2.3.0
Detects language, normalizes input, tokenizes using mBART-50
Routes to language-specific subgraph
"""

from typing import Dict, List, Tuple, Optional
import re
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
import torch

class MultilingualParser:
    """
    Detects language, normalizes input, and tokenizes using mBART-50
    Routes queries to appropriate language-specific subgraphs
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'en_XX', 'es': 'es_XX', 'fr': 'fr_XX', 'de': 'de_DE',
        'zh': 'zh_CN', 'ja': 'ja_XX', 'ko': 'ko_KR', 'ar': 'ar_AR',
        'hi': 'hi_IN', 'id': 'id_ID', 'pt': 'pt_XX', 'ru': 'ru_RU',
        'vi': 'vi_VN', 'th': 'th_TH', 'tr': 'tr_TR'
    }
    
    def __init__(self, model_name: str = "facebook/mbart-large-50"):
        """Initialize multilingual parser with mBART-50"""
        self.tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def detect_language(self, text: str) -> str:
        """
        Detect language using character patterns and mBART tokenization
        
        Args:
            text: Input text
            
        Returns:
            ISO language code (e.g., 'en', 'zh', 'ar')
        """
        # Simple heuristic-based detection
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        elif re.search(r'[\u0600-\u06ff]', text):
            return 'ar'
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return 'ja'
        elif re.search(r'[\uac00-\ud7af]', text):
            return 'ko'
        elif re.search(r'[\u0e00-\u0e7f]', text):
            return 'th'
        elif re.search(r'[\u0900-\u097f]', text):
            return 'hi'
        
        # Default to English for Latin scripts
        return 'en'
    
    def normalize_text(self, text: str, lang: str) -> str:
        """
        Normalize text based on language-specific rules
        
        Args:
            text: Input text
            lang: Language code
            
        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Language-specific normalization
        if lang in ['zh', 'ja']:
            # Remove spaces between CJK characters
            text = re.sub(r'([\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff])\s+([\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff])', r'\1\2', text)
        elif lang == 'ar':
            # Normalize Arabic characters
            text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        
        return text
    
    def tokenize(self, text: str, lang: str) -> Dict[str, torch.Tensor]:
        """
        Tokenize text using mBART-50 tokenizer
        
        Args:
            text: Input text
            lang: Language code
            
        Returns:
            Tokenized inputs
        """
        # Set source language
        src_lang = self.SUPPORTED_LANGUAGES.get(lang, 'en_XX')
        self.tokenizer.src_lang = src_lang
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        return {k: v.to(self.device) for k, v in inputs.items()}
    
    def route_to_subgraph(self, lang: str) -> str:
        """
        Route to language-specific subgraph
        
        Args:
            lang: Language code
            
        Returns:
            Subgraph identifier
        """
        # Map languages to subgraph categories
        subgraph_mapping = {
            'en': 'latin_western',
            'es': 'latin_western', 'fr': 'latin_western', 'de': 'latin_western', 'pt': 'latin_western',
            'zh': 'cjk', 'ja': 'cjk', 'ko': 'cjk',
            'ar': 'rtl_semitic',
            'hi': 'indic', 'th': 'indic',
            'ru': 'cyrillic',
            'id': 'latin_sea', 'vi': 'latin_sea', 'tr': 'latin_sea'
        }
        
        return subgraph_mapping.get(lang, 'latin_western')
    
    def parse_query(self, query: str, lang: Optional[str] = None) -> Dict:
        """
        Complete parsing pipeline
        
        Args:
            query: Input query
            lang: Optional language code (auto-detected if not provided)
            
        Returns:
            Parsed query with tokens and routing info
        """
        # Detect language if not provided
        if lang is None:
            lang = self.detect_language(query)
        
        # Normalize
        normalized = self.normalize_text(query, lang)
        
        # Tokenize
        tokens = self.tokenize(normalized, lang)
        
        # Route to subgraph
        subgraph = self.route_to_subgraph(lang)
        
        return {
            'original': query,
            'normalized': normalized,
            'language': lang,
            'tokens': tokens,
            'subgraph': subgraph,
            'mbart_lang': self.SUPPORTED_LANGUAGES.get(lang, 'en_XX')
        }


def parse_query(query: str, lang: Optional[str] = None) -> Dict:
    """
    Convenience function for parsing queries
    
    Args:
        query: Input query
        lang: Optional language code
        
    Returns:
        Parsed query dictionary
    """
    parser = MultilingualParser()
    return parser.parse_query(query, lang)
