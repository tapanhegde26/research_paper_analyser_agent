"""
Agent Evaluation Framework

Evaluates agent performance on various metrics:
- Summary quality
- Citation accuracy
- Response time
- Cost efficiency
"""

from typing import Dict, Any, List
from datetime import datetime

from observability.logger import get_logger
from observability.metrics import record_metric

logger = get_logger(__name__)


class EvaluationResult:
    """Result of an evaluation"""
    
    def __init__(
        self,
        metric_name: str,
        score: float,
        max_score: float = 1.0,
        details: Dict[str, Any] = None
    ):
        self.metric_name = metric_name
        self.score = score
        self.max_score = max_score
        self.percentage = (score / max_score) * 100 if max_score > 0 else 0
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_name": self.metric_name,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round(self.percentage, 2),
            "details": self.details,
            "timestamp": self.timestamp
        }


class AgentEvaluator:
    """
    Evaluates agent performance across multiple dimensions
    """
    
    def __init__(self):
        logger.info("Agent Evaluator initialized")
    
    async def evaluate_summary_quality(
        self,
        original_abstract: str,
        summary: Dict[str, Any],
        model
    ) -> EvaluationResult:
        """
        Evaluate quality of a summary
        
        Args:
            original_abstract: Original paper abstract
            summary: Generated summary
            model: LLM model for evaluation
        
        Returns:
            EvaluationResult
        """
        logger.info("Evaluating summary quality")
        
        prompt = f"""
        Evaluate the quality of this research paper summary.
        
        ORIGINAL ABSTRACT:
        {original_abstract}
        
        GENERATED SUMMARY:
        {summary.get('executive_summary', 'N/A')}
        
        KEY CONTRIBUTIONS:
        {summary.get('contributions', 'N/A')}
        
        Evaluate on these criteria (score 0-10 for each):
        1. Accuracy: Does it accurately represent the original?
        2. Completeness: Does it cover key points?
        3. Clarity: Is it clear and well-written?
        4. Conciseness: Is it appropriately concise?
        
        Provide scores in JSON format:
        {{
            "accuracy": score,
            "completeness": score,
            "clarity": score,
            "conciseness": score,
            "overall": average,
            "reasoning": "brief explanation"
        }}
        """
        
        try:
            response = model.generate_content(prompt)
            
            # Parse response
            import json
            cleaned = response.text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3]
            
            scores = json.loads(cleaned.strip())
            
            overall_score = scores.get("overall", 0) / 10.0  # Normalize to 0-1
            
            result = EvaluationResult(
                metric_name="summary_quality",
                score=overall_score,
                max_score=1.0,
                details=scores
            )
            
            # Record metric
            record_metric("summary_quality_score", overall_score, metric_type="histogram")
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating summary: {str(e)}")
            return EvaluationResult(
                metric_name="summary_quality",
                score=0.5,
                details={"error": str(e)}
            )
    
    async def evaluate_citation_accuracy(
        self,
        papers: List[Dict[str, Any]],
        synthesis: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Evaluate citation accuracy in synthesis
        
        Args:
            papers: Original papers
            synthesis: Generated synthesis
        
        Returns:
            EvaluationResult
        """
        logger.info("Evaluating citation accuracy")
        
        # Extract paper titles
        paper_titles = set(p.get("title", "").lower() for p in papers)
        
        # Check synthesis for citations
        synthesis_text = str(synthesis).lower()
        
        citations_found = 0
        for title in paper_titles:
            if title[:30] in synthesis_text:  # Check first 30 chars
                citations_found += 1
        
        total_papers = len(paper_titles)
        accuracy = citations_found / total_papers if total_papers > 0 else 0
        
        result = EvaluationResult(
            metric_name="citation_accuracy",
            score=accuracy,
            max_score=1.0,
            details={
                "papers_cited": citations_found,
                "total_papers": total_papers
            }
        )
        
        record_metric("citation_accuracy", accuracy, metric_type="histogram")
        
        return result
    
    async def evaluate_response_time(
        self,
        start_time: float,
        end_time: float,
        num_papers: int
    ) -> EvaluationResult:
        """
        Evaluate response time performance
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            num_papers: Number of papers processed
        
        Returns:
            EvaluationResult
        """
        duration = end_time - start_time
        time_per_paper = duration / num_papers if num_papers > 0 else duration
        
        # Target: < 60 seconds per paper
        target_time = 60.0
        score = min(target_time / time_per_paper, 1.0) if time_per_paper > 0 else 1.0
        
        result = EvaluationResult(
            metric_name="response_time",
            score=score,
            max_score=1.0,
            details={
                "total_duration_seconds": round(duration, 2),
                "time_per_paper_seconds": round(time_per_paper, 2),
                "num_papers": num_papers,
                "target_time_seconds": target_time
            }
        )
        
        record_metric("agent_operation_duration_seconds", duration, metric_type="histogram")
        
        return result
    
    async def evaluate_cost_efficiency(
        self,
        tokens_used: int,
        num_papers: int,
        cost_per_million_tokens: float = 1.0
    ) -> EvaluationResult:
        """
        Evaluate cost efficiency
        
        Args:
            tokens_used: Total tokens consumed
            num_papers: Number of papers processed
            cost_per_million_tokens: Cost per 1M tokens
        
        Returns:
            EvaluationResult
        """
        total_cost = (tokens_used / 1_000_000) * cost_per_million_tokens
        cost_per_paper = total_cost / num_papers if num_papers > 0 else total_cost
        
        # Target: < $0.20 per paper
        target_cost = 0.20
        score = min(target_cost / cost_per_paper, 1.0) if cost_per_paper > 0 else 1.0
        
        result = EvaluationResult(
            metric_name="cost_efficiency",
            score=score,
            max_score=1.0,
            details={
                "total_cost_usd": round(total_cost, 4),
                "cost_per_paper_usd": round(cost_per_paper, 4),
                "tokens_used": tokens_used,
                "num_papers": num_papers,
                "target_cost_usd": target_cost
            }
        )
        
        return result
    
    async def comprehensive_evaluation(
        self,
        analysis_result: Any,
        start_time: float,
        end_time: float,
        model
    ) -> Dict[str, EvaluationResult]:
        """
        Run comprehensive evaluation
        
        Args:
            analysis_result: Analysis result to evaluate
            start_time: Start timestamp
            end_time: End timestamp
            model: LLM model
        
        Returns:
            Dictionary of evaluation results
        """
        logger.info("Running comprehensive evaluation")
        
        results = {}
        
        try:
            # Response time
            results["response_time"] = await self.evaluate_response_time(
                start_time,
                end_time,
                analysis_result.papers_analyzed
            )
            
            # Citation accuracy
            # Note: Would need access to original papers
            # results["citation_accuracy"] = await self.evaluate_citation_accuracy(...)
            
            # Record overall evaluation
            avg_score = sum(r.score for r in results.values()) / len(results)
            record_metric("overall_evaluation_score", avg_score, metric_type="histogram")
            
            logger.info(f"Evaluation complete. Average score: {avg_score:.2%}")
            
        except Exception as e:
            logger.error(f"Error in comprehensive evaluation: {str(e)}")
        
        return results
    
    def generate_report(
        self,
        results: Dict[str, EvaluationResult]
    ) -> str:
        """
        Generate evaluation report
        
        Args:
            results: Dictionary of evaluation results
        
        Returns:
            Markdown formatted report
        """
        report = ["# Agent Evaluation Report\n"]
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("## Metrics\n")
        
        for name, result in results.items():
            report.append(f"### {result.metric_name.replace('_', ' ').title()}\n")
            report.append(f"- Score: {result.percentage:.1f}% ({result.score:.3f}/{result.max_score})\n")
            
            if result.details:
                report.append("- Details:\n")
                for key, value in result.details.items():
                    report.append(f"  - {key}: {value}\n")
            
            report.append("\n")
        
        # Overall score
        if results:
            avg_percentage = sum(r.percentage for r in results.values()) / len(results)
            report.append(f"## Overall Score: {avg_percentage:.1f}%\n")
        
        return "".join(report)

