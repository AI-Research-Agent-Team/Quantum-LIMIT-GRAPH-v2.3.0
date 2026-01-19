# config.py
"""Configuration for Quantum LIMIT-GRAPH Green Agent"""

class Config:
    """Green agent configuration"""
    
    def __init__(self):
        # Test suites to run
        self.test_suites = [
            "multilingual",
            "quantum",
            "hallucination",
            "context_routing"
        ]
        
        # Supported languages
        self.languages = [
            "en", "es", "fr", "de", "zh", "ja", "ko",
            "ar", "hi", "id", "pt", "ru", "vi", "th", "tr"
        ]
        
        # Scoring weights
        self.weights = {
            "multilingual": 0.25,
            "quantum": 0.25,
            "hallucination": 0.30,
            "context_routing": 0.20
        }
        
        # Timeout settings
        self.timeout = 300  # seconds
        
    def to_dict(self):
        return {
            "test_suites": self.test_suites,
            "languages": self.languages,
            "weights": self.weights,
            "timeout": self.timeout
        }
