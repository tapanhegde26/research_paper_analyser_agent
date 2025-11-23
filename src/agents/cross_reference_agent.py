"""
Cross-Reference Agent

This agent identifies:
- Connections between papers
- Contradictions or disagreements
- Complementary insights
- Research gaps
- Citation relationships
"""

from typing import List, Dict, Any
import json

from observability.logger import get_logger
from observability.tracer import trace_operation

logger = get_logger(__name__)


class CrossReferenceAgent:
    """
    Agent specialized in cross-referencing multiple papers to find
    connections, contradictions, and research gaps.
    """
    
    def __init__(self, model):
        """
        Initialize the Cross-Reference Agent
        
        Args:
            model: Gemini model instance
        """
        self.model = model
        logger.info("Cross-Reference Agent initialized")
    
    @trace_operation("cross_reference_analyze")
    async def analyze(
        self,
        papers: List[Dict[str, Any]],
        summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze connections and contradictions between papers
        
        Args:
            papers: List of paper metadata
            summaries: List of paper summaries
        
        Returns:
            Cross-reference analysis
        """
        logger.info(f"Cross-referencing {len(papers)} papers")
        
        try:
            # Create comprehensive prompt with all summaries
            prompt = self._create_cross_reference_prompt(summaries)
            
            # Analyze using LLM
            response = self.model.generate_content(prompt)
            
            # Parse response
            analysis = self._parse_cross_reference_response(response.text)
            
            logger.info("Cross-reference analysis complete")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in cross-reference analysis: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "connections": [],
                "contradictions": [],
                "research_gaps": []
            }
    
    async def compare(
        self,
        papers: List[Dict[str, Any]],
        summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare specific papers for similarities and differences
        
        Args:
            papers: Papers to compare
            summaries: Paper summaries
        
        Returns:
            Comparison results
        """
        logger.info(f"Comparing {len(papers)} papers")
        
        prompt = f"""
        Compare the following research papers:
        
        {self._format_summaries_for_comparison(summaries)}
        
        Provide a detailed comparison including:
        1. Similarities (shared approaches, findings, or conclusions)
        2. Differences (methodologies, results, or perspectives)
        3. Complementary Insights (how they work together)
        4. Which paper is most comprehensive for each aspect
        5. Synthesis (combined understanding from all papers)
        
        Format as JSON with keys: similarities, differences, complementary_insights,
        best_for, synthesis
        """
        
        try:
            response = self.model.generate_content(prompt)
            comparison = self._parse_json_response(response.text)
            logger.info("Comparison complete")
            return comparison
        except Exception as e:
            logger.error(f"Error in comparison: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def _create_cross_reference_prompt(
        self,
        summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Create prompt for cross-reference analysis
        
        Args:
            summaries: Paper summaries
        
        Returns:
            Formatted prompt
        """
        # Format summaries for analysis
        papers_text = self._format_summaries(summaries)
        
        prompt = f"""
        You are a research analyst expert at identifying connections between papers.
        
        Analyze the following research papers:
        
        {papers_text}
        
        Provide a comprehensive cross-reference analysis:
        
        1. CONNECTIONS: Identify papers that:
           - Build on each other's work
           - Use similar methodologies
           - Address related problems
           - Have complementary findings
           
        2. CONTRADICTIONS: Identify where papers:
           - Have conflicting results
           - Disagree on approaches
           - Challenge each other's assumptions
           - Present alternative explanations
        
        3. RESEARCH GAPS: Identify:
           - Questions none of these papers fully answer
           - Methodological limitations across papers
           - Areas for future research
           - Missing perspectives or approaches
        
        4. CITATION NETWORK: Identify:
           - Which papers cite each other
           - Common references
           - Influential works mentioned
        
        5. TEMPORAL EVOLUTION: How has thinking evolved over time?
        
        Format as JSON with keys: connections, contradictions, research_gaps,
        citation_network, temporal_evolution
        
        Each connection/contradiction should include:
        - paper_ids: list of relevant paper IDs
        - description: what the connection/contradiction is
        - significance: why it matters
        """
        
        return prompt
    
    def _format_summaries(
        self,
        summaries: List[Dict[str, Any]]
    ) -> str:
        """Format summaries for prompt"""
        formatted = []
        for i, summary in enumerate(summaries, 1):
            text = f"""
            Paper {i}:
            ID: {summary.get('paper_id', 'unknown')}
            Title: {summary.get('title', 'Unknown')}
            Authors: {', '.join(summary.get('authors', [])[:3])}
            Published: {summary.get('published_date', 'Unknown')}
            
            Summary: {summary.get('executive_summary', 'No summary')}
            
            Key Contributions: {summary.get('contributions', 'N/A')}
            
            Methodology: {summary.get('methodology', 'N/A')}
            
            Results: {summary.get('results', 'N/A')}
            """
            formatted.append(text)
        
        return "\n\n".join(formatted)
    
    def _format_summaries_for_comparison(
        self,
        summaries: List[Dict[str, Any]]
    ) -> str:
        """Format summaries specifically for comparison"""
        return self._format_summaries(summaries)
    
    def _parse_cross_reference_response(
        self,
        response_text: str
    ) -> Dict[str, Any]:
        """
        Parse cross-reference analysis response
        
        Args:
            response_text: Raw LLM response
        
        Returns:
            Parsed analysis dictionary
        """
        return self._parse_json_response(response_text)
    
    def _parse_json_response(
        self,
        response_text: str
    ) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
        
        Args:
            response_text: Raw response
        
        Returns:
            Parsed dictionary
        """
        try:
            # Clean response
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return {
                "raw_text": response_text,
                "parse_error": True
            }

