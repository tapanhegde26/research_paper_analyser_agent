"""
Summary Agent

This agent extracts key information from research papers including:
- Executive summary
- Key findings and contributions
- Methodology overview
- Results and conclusions
- Limitations

Multiple instances of this agent run in parallel for efficiency.
"""

from typing import Dict, Any
import json

from observability.logger import get_logger
from observability.tracer import trace_operation

logger = get_logger(__name__)


class SummaryAgent:
    """
    Agent specialized in summarizing research papers.
    
    This agent can be instantiated multiple times for parallel processing.
    """
    
    def __init__(self, model):
        """
        Initialize the Summary Agent
        
        Args:
            model: Gemini model instance
        """
        self.model = model
    
    @trace_operation("summarize_paper")
    async def summarize(
        self,
        paper: Dict[str, Any],
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Summarize a research paper
        
        Args:
            paper: Paper metadata including abstract
            depth: Level of detail ("quick", "standard", "comprehensive")
        
        Returns:
            Summary dictionary with extracted information
        """
        logger.info(f"Summarizing paper: {paper['title'][:50]}...")
        
        try:
            # Create prompt based on depth
            prompt = self._create_summary_prompt(paper, depth)
            
            # Generate summary using LLM
            response = self.model.generate_content(prompt)
            
            # Parse response
            summary = self._parse_summary_response(response.text, paper)
            
            logger.info(f"Summary complete for: {paper['title'][:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing paper: {str(e)}", exc_info=True)
            # Return basic summary on error
            return {
                "paper_id": paper.get("arxiv_id", "unknown"),
                "title": paper["title"],
                "executive_summary": paper.get("abstract", "")[:500],
                "error": str(e)
            }
    
    def _create_summary_prompt(
        self,
        paper: Dict[str, Any],
        depth: str
    ) -> str:
        """
        Create summarization prompt based on depth level
        
        Args:
            paper: Paper metadata
            depth: Summary depth
        
        Returns:
            Formatted prompt string
        """
        base_info = f"""
        Title: {paper['title']}
        Authors: {', '.join(paper.get('authors', [])[:5])}
        Published: {paper.get('published_date', 'Unknown')}
        Abstract: {paper.get('abstract', 'No abstract available')}
        """
        
        if depth == "quick":
            prompt = f"""
            {base_info}
            
            Provide a QUICK summary (2-3 sentences) covering:
            1. Main contribution
            2. Key result
            
            Format as JSON with keys: executive_summary, key_contribution, main_result
            """
        
        elif depth == "comprehensive":
            prompt = f"""
            {base_info}
            
            Provide a COMPREHENSIVE analysis covering:
            1. Executive Summary (3-4 sentences)
            2. Problem Statement (what gap does this address?)
            3. Key Contributions (bulleted list)
            4. Methodology (brief overview)
            5. Main Results (quantitative if available)
            6. Conclusions
            7. Limitations
            8. Future Work suggestions
            9. Key Citations/References mentioned
            
            Format as JSON with appropriate keys.
            """
        
        else:  # standard
            prompt = f"""
            {base_info}
            
            Provide a STANDARD summary covering:
            1. Executive Summary (2-3 sentences)
            2. Main Problem Addressed
            3. Key Contributions (3-5 points)
            4. Methodology Overview
            5. Primary Results
            6. Conclusions
            7. Notable Limitations
            
            Format as JSON with keys: executive_summary, problem, contributions, 
            methodology, results, conclusions, limitations
            """
        
        return prompt
    
    def _parse_summary_response(
        self,
        response_text: str,
        paper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse LLM response into structured summary
        
        Args:
            response_text: Raw LLM response
            paper: Original paper metadata
        
        Returns:
            Structured summary dictionary
        """
        try:
            # Try to parse as JSON
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            summary_data = json.loads(cleaned)
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, using text format")
            # Fallback: use text directly
            summary_data = {
                "executive_summary": response_text[:500],
                "full_text": response_text
            }
        
        # Add paper metadata
        summary_data.update({
            "paper_id": paper.get("arxiv_id", "unknown"),
            "title": paper["title"],
            "authors": paper.get("authors", []),
            "published_date": paper.get("published_date"),
            "pdf_url": paper.get("pdf_url"),
            "source": paper.get("source", "unknown")
        })
        
        return summary_data

