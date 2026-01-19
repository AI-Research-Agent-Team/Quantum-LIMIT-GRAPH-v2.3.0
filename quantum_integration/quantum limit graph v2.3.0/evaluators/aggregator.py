# evaluators/aggregator.py
"""Score aggregation across test suites"""

from typing import Dict, Any

class ScoreAggregator:
    """Aggregates scores from multiple test suites"""
    
    def aggregate_results(self, participants: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results across all participants"""
        
        if not participants:
            return {"overall_score": 0.0}
        
        # Calculate average scores across participants
        all_scores = []
        suite_scores = {}
        
        for participant, results in participants.items():
            if "scores" in results:
                for suite, score in results["scores"].items():
                    if suite not in suite_scores:
                        suite_scores[suite] = []
                    suite_scores[suite].append(score)
                
                all_scores.append(results.get("overall_score", 0.0))
        
        # Average by suite
        avg_suite_scores = {
            suite: sum(scores) / len(scores)
            for suite, scores in suite_scores.items()
        }
        
        return {
            "overall_score": sum(all_scores) / len(all_scores) if all_scores else 0.0,
            "suite_scores": avg_suite_scores,
            "participants_count": len(participants),
            "ranking": self._create_ranking(participants)
        }
    
    def _create_ranking(self, participants: Dict[str, Any]) -> list:
        """Create ranking of participants"""
        ranked = [
            {
                "role": role,
                "score": results.get("overall_score", 0.0)
            }
            for role, results in participants.items()
        ]
        
        return sorted(ranked, key=lambda x: x["score"], reverse=True)
