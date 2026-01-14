"""
Leaderboard API Routes
Endpoints for agent rankings and leaderboard management
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from api.models.leaderboard import (
    LeaderboardEntry,
    LeaderboardResponse,
    AgentRanking,
    TimeRange
)
from api.services.leaderboard_service import LeaderboardService
from api.middleware.auth import get_api_key, optional_api_key
from monitoring.logger import logger

router = APIRouter()

# Dependency injection
def get_leaderboard_service() -> LeaderboardService:
    return LeaderboardService()

@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    metric: str = Query(
        "overall_score",
        description="Metric to rank by (overall_score, parsing_accuracy, etc.)"
    ),
    time_range: TimeRange = Query(
        TimeRange.ALL_TIME,
        description="Time range filter"
    ),
    language: Optional[str] = Query(
        None,
        description="Filter by language (en, es, zh, etc.)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    service: LeaderboardService = Depends(get_leaderboard_service),
    api_key: Optional[str] = Depends(optional_api_key)
):
    """
    Get current leaderboard rankings
    
    Returns ranked list of agents based on specified metric and filters.
    """
    try:
        # Calculate time range
        start_time = None
        if time_range != TimeRange.ALL_TIME:
            days = {
                TimeRange.LAST_DAY: 1,
                TimeRange.LAST_WEEK: 7,
                TimeRange.LAST_MONTH: 30,
                TimeRange.LAST_YEAR: 365
            }
            start_time = datetime.utcnow() - timedelta(days=days[time_range])
        
        # Get leaderboard data
        leaderboard = await service.get_leaderboard(
            metric=metric,
            language=language,
            start_time=start_time,
            limit=limit,
            offset=offset
        )
        
        logger.info(
            f"Leaderboard requested",
            extra={
                "metric": metric,
                "time_range": time_range,
                "language": language,
                "entries": len(leaderboard.rankings)
            }
        )
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/{agent_id}", response_model=AgentRanking)
async def get_agent_ranking(
    agent_id: str,
    metric: str = Query("overall_score"),
    time_range: TimeRange = Query(TimeRange.ALL_TIME),
    service: LeaderboardService = Depends(get_leaderboard_service)
):
    """
    Get ranking for specific agent
    
    Returns detailed ranking information for a single agent.
    """
    try:
        ranking = await service.get_agent_ranking(
            agent_id=agent_id,
            metric=metric,
            time_range=time_range
        )
        
        if not ranking:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found in leaderboard"
            )
        
        return ranking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/{agent_id}")
async def get_agent_trends(
    agent_id: str,
    metric: str = Query("overall_score"),
    days: int = Query(30, ge=1, le=365),
    service: LeaderboardService = Depends(get_leaderboard_service)
):
    """
    Get historical performance trends for an agent
    
    Returns time-series data of agent performance over specified period.
    """
    try:
        trends = await service.get_agent_trends(
            agent_id=agent_id,
            metric=metric,
            days=days
        )
        
        return {
            "agent_id": agent_id,
            "metric": metric,
            "period_days": days,
            "data_points": len(trends),
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error fetching agent trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare")
async def compare_agents(
    agent_ids: str = Query(
        ...,
        description="Comma-separated list of agent IDs to compare"
    ),
    metric: str = Query("overall_score"),
    service: LeaderboardService = Depends(get_leaderboard_service)
):
    """
    Compare performance of multiple agents
    
    Returns comparative analysis of specified agents.
    """
    try:
        ids = [id.strip() for id in agent_ids.split(",")]
        
        if len(ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 agent IDs required for comparison"
            )
        
        if len(ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 agents can be compared at once"
            )
        
        comparison = await service.compare_agents(
            agent_ids=ids,
            metric=metric
        )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/available")
async def get_available_metrics(
    service: LeaderboardService = Depends(get_leaderboard_service)
):
    """
    Get list of available metrics for ranking
    
    Returns all metrics that can be used for leaderboard rankings.
    """
    return {
        "metrics": [
            {
                "id": "overall_score",
                "name": "Overall Score",
                "description": "Weighted average of all component scores",
                "range": [0.0, 1.0]
            },
            {
                "id": "parsing_accuracy",
                "name": "Parsing Accuracy",
                "description": "Multilingual parsing success rate",
                "range": [0.0, 1.0]
            },
            {
                "id": "semantic_coherence",
                "name": "Semantic Coherence",
                "description": "Query-response semantic alignment",
                "range": [0.0, 1.0]
            },
            {
                "id": "hallucination_avoidance",
                "name": "Hallucination Avoidance",
                "description": "Factual accuracy score",
                "range": [0.0, 1.0]
            },
            {
                "id": "latency_score",
                "name": "Latency Performance",
                "description": "Response time optimization",
                "range": [0.0, 1.0]
            },
            {
                "id": "quantum_performance",
                "name": "Quantum Performance",
                "description": "Quantum speedup vs classical",
                "range": [0.0, 1.0]
            }
        ]
    }

@router.post("/update", dependencies=[Depends(get_api_key)])
async def update_leaderboard(
    agent_id: str,
    evaluation_results: dict,
    service: LeaderboardService = Depends(get_leaderboard_service),
    api_key: str = Depends(get_api_key)
):
    """
    Update leaderboard with new evaluation results
    
    Protected endpoint for submitting evaluation results.
    Requires API key authentication.
    """
    try:
        updated = await service.update_rankings(
            agent_id=agent_id,
            results=evaluation_results
        )
        
        logger.info(
            f"Leaderboard updated for agent {agent_id}",
            extra={"results": evaluation_results}
        )
        
        return {
            "success": True,
            "agent_id": agent_id,
            "previous_rank": updated.get("previous_rank"),
            "current_rank": updated.get("current_rank"),
            "rank_change": updated.get("rank_change")
        }
        
    except Exception as e:
        logger.error(f"Error updating leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_leaderboard_stats(
    service: LeaderboardService = Depends(get_leaderboard_service)
):
    """
    Get overall leaderboard statistics
    
    Returns aggregate statistics about the leaderboard.
    """
    try:
        stats = await service.get_stats()
        
        return {
            "total_agents": stats.get("total_agents", 0),
            "total_evaluations": stats.get("total_evaluations", 0),
            "active_agents_7d": stats.get("active_agents_7d", 0),
            "active_agents_30d": stats.get("active_agents_30d", 0),
            "average_overall_score": stats.get("avg_overall_score", 0.0),
            "top_score": stats.get("top_score", 0.0),
            "supported_languages": stats.get("languages", []),
            "last_updated": stats.get("last_updated")
        }
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agent/{agent_id}", dependencies=[Depends(get_api_key)])
async def remove_from_leaderboard(
    agent_id: str,
    service: LeaderboardService = Depends(get_leaderboard_service),
    api_key: str = Depends(get_api_key)
):
    """
    Remove an agent from the leaderboard
    
    Protected endpoint. Requires API key authentication.
    """
    try:
        success = await service.remove_agent(agent_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found in leaderboard"
            )
        
        logger.info(f"Agent {agent_id} removed from leaderboard")
        
        return {
            "success": True,
            "agent_id": agent_id,
            "message": "Agent removed from leaderboard"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing agent from leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
