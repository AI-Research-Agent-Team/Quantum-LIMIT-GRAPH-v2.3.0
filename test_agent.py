"""
Integration tests for Quantum LIMIT-GRAPH Green Agent
Tests the agent's evaluation capabilities
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Import our agent
from agent import QuantumLimitAgent

@pytest.fixture
def agent():
    """Create a QuantumLimitAgent instance for testing"""
    return QuantumLimitAgent()

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test that the agent initializes correctly"""
    assert agent is not None
    assert len(agent.supported_languages) == 15
    assert "en" in agent.supported_languages
    assert "zh" in agent.supported_languages

@pytest.mark.asyncio
async def test_evaluate_response_english(agent):
    """Test evaluation of an English query-response pair"""
    result = await agent._evaluate_response(
        query="What is quantum computing?",
        response="Quantum computing uses quantum mechanics to process information.",
        expected_lang="en"
    )
    
    assert "scores" in result
    assert "metrics" in result
    assert "overall_score" in result
    assert 0.0 <= result["overall_score"] <= 1.0
    assert result["metrics"]["detected_language"] == "en"

@pytest.mark.asyncio
async def test_evaluate_response_multilingual(agent):
    """Test evaluation across multiple languages"""
    test_cases = [
        ("en", "What is AI?", "AI is artificial intelligence"),
        ("es", "¿Qué es la IA?", "La IA es inteligencia artificial"),
        ("zh", "什么是人工智能？", "人工智能是计算机科学的一个分支")
    ]
    
    for lang, query, response in test_cases:
        result = await agent._evaluate_response(
            query=query,
            response=response,
            expected_lang=lang
        )
        
        assert result["overall_score"] > 0
        assert result["metrics"]["detected_language"] == lang

@pytest.mark.asyncio
async def test_calculate_coherence(agent):
    """Test semantic coherence calculation"""
    score1 = agent._calculate_coherence(
        "quantum computing",
        "Quantum computing uses quantum mechanics"
    )
    
    score2 = agent._calculate_coherence(
        "quantum computing",
        "The weather is nice today"
    )
    
    assert score1 > score2
    assert 0.0 <= score1 <= 1.0
    assert 0.0 <= score2 <= 1.0

@pytest.mark.asyncio
async def test_calculate_latency_score(agent):
    """Test latency scoring"""
    assert agent._calculate_latency_score(40) == 1.0    # Excellent
    assert agent._calculate_latency_score(80) == 0.8    # Good
    assert agent._calculate_latency_score(150) == 0.6   # Acceptable
    assert agent._calculate_latency_score(300) == 0.4   # Slow
    assert agent._calculate_latency_score(600) == 0.2   # Too slow

@pytest.mark.asyncio
async def test_get_default_queries(agent):
    """Test that default queries are properly formatted"""
    queries = agent._get_default_queries()
    
    assert len(queries) >= 4
    
    for query in queries:
        assert "query" in query
        assert "language" in query
        assert query["language"] in agent.supported_languages

@pytest.mark.asyncio
async def test_calculate_final_scores(agent):
    """Test aggregation of multiple evaluation results"""
    mock_results = [
        {
            "scores": {
                "parsing_accuracy": 1.0,
                "semantic_coherence": 0.8,
                "hallucination_avoidance": 0.9,
                "latency_score": 0.85,
                "quantum_performance": 0.7
            },
            "passed": True
        },
        {
            "scores": {
                "parsing_accuracy": 0.95,
                "semantic_coherence": 0.75,
                "hallucination_avoidance": 0.85,
                "latency_score": 0.8,
                "quantum_performance": 0.65
            },
            "passed": True
        }
    ]
    
    final = agent._calculate_final_scores(mock_results)
    
    assert "summary" in final
    assert "aggregated_scores" in final
    assert "detailed_results" in final
    assert final["summary"]["total_tests"] == 2
    assert final["summary"]["passed_tests"] == 2
    assert 0.0 <= final["summary"]["overall_score"] <= 1.0

@pytest.mark.asyncio
async def test_calculate_final_scores_empty(agent):
    """Test that empty results are handled gracefully"""
    final = agent._calculate_final_scores([])
    assert "error" in final

@pytest.mark.asyncio
async def test_evaluation_with_quantum_modules_unavailable(agent):
    """Test that agent works even without quantum modules"""
    # This test passes as long as the agent doesn't crash
    result = await agent._evaluate_response(
        query="Test query",
        response="Test response",
        expected_lang="en"
    )
    
    assert result is not None
    assert "overall_score" in result
    # Should use mock implementations if quantum modules unavailable

@pytest.mark.asyncio
async def test_handle_assessment_basic():
    """Test basic assessment flow"""
    agent = QuantumLimitAgent()
    
    # Mock assessment request
    mock_request = Mock()
    mock_request.participants = {
        "test_agent": "http://localhost:8001"
    }
    mock_request.config = {
        "test_queries": [
            {"query": "What is AI?", "language": "en"}
        ]
    }
    
    # Mock the purple agent response
    with patch.object(agent, '_get_purple_agent_response', new_callable=AsyncMock) as mock_response:
        mock_response.return_value = "AI is artificial intelligence."
        
        updates = []
        async for update in agent.handle_assessment(mock_request):
            updates.append(update)
        
        # Should have multiple updates
        assert len(updates) > 0
        
        # Last update should be completed
        assert updates[-1].status == "completed"
        
        # Should have artifacts with results
        assert len(updates[-1].artifacts) > 0
        assert updates[-1].artifacts[0].type == "evaluation_results"

# Test scores are within valid ranges
@pytest.mark.asyncio
async def test_all_scores_in_valid_range(agent):
    """Ensure all generated scores are between 0 and 1"""
    result = await agent._evaluate_response(
        query="Test query about quantum computing",
        response="Quantum computing is a field that uses quantum mechanics",
        expected_lang="en"
    )
    
    for score_name, score_value in result["scores"].items():
        assert 0.0 <= score_value <= 1.0, f"{score_name} score out of range: {score_value}"
    
    assert 0.0 <= result["overall_score"] <= 1.0

# Performance test
@pytest.mark.asyncio
async def test_evaluation_performance(agent):
    """Test that evaluation completes in reasonable time"""
    import time
    
    start = time.time()
    
    result = await agent._evaluate_response(
        query="What is machine learning?",
        response="Machine learning is a subset of AI that learns from data.",
        expected_lang="en"
    )
    
    duration = time.time() - start
    
    # Should complete in under 5 seconds (generous for testing)
    assert duration < 5.0, f"Evaluation too slow: {duration}s"
    assert result is not None

# Integration test markers
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_assessment_flow():
    """Integration test for complete assessment flow"""
    agent = QuantumLimitAgent()
    
    mock_request = Mock()
    mock_request.participants = {
        "baseline_agent": "http://localhost:8001"
    }
    mock_request.config = {}
    
    with patch.object(agent, '_get_purple_agent_response', new_callable=AsyncMock) as mock_response:
        mock_response.return_value = "This is a test response."
        
        completed = False
        async for update in agent.handle_assessment(mock_request):
            if update.status == "completed":
                completed = True
                assert update.artifacts is not None
                results = update.artifacts[0].data
                assert "summary" in results
                assert "aggregated_scores" in results
        
        assert completed, "Assessment did not complete"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
