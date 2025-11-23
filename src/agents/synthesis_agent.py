"""
Synthesis Agent

This agent creates comprehensive knowledge synthesis from multiple papers:
- Executive summary of the research area
- Key findings synthesis
- Methodological trends
- Future research directions
- Comprehensive report generation
"""

from typing import List, Dict, Any
import json

from observability.logger import get_logger
from observability.tracer import trace_operation

logger = get_logger(__name__)


class SynthesisAgent:
    """
    Agent specialized in synthesizing knowledge from multiple research papers
    into coherent, comprehensive reports.
    """
    
    def __init__(self, model):
        """
        Initialize the Synthesis Agent
        
        Args:
            model: Gemini model instance
        """
        self.model = model
        logger.info("Synthesis Agent initialized")
    
    @trace_operation("synthesize_knowledge")
    async def synthesize(
        self,
        topic: str,
        summaries: List[Dict[str, Any]],
        cross_references: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize knowledge from multiple papers
        
        Args:
            topic: Research topic
            summaries: List of paper summaries
            cross_references: Cross-reference analysis
        
        Returns:
            Comprehensive synthesis report
        """
        logger.info(f"Synthesizing knowledge for topic: {topic}")
        
        try:
            # Create synthesis prompt
            prompt = self._create_synthesis_prompt(
                topic,
                summaries,
                cross_references
            )
            
            # Generate synthesis using LLM
            response = self.model.generate_content(prompt)
            
            # Parse and structure synthesis
            synthesis = self._parse_synthesis_response(response.text, topic)
            
            logger.info("Knowledge synthesis complete")
            return synthesis
            
        except Exception as e:
            logger.error(f"Error in synthesis: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "executive_summary": f"Error synthesizing research on {topic}",
                "key_findings": []
            }
    
    def _create_synthesis_prompt(
        self,
        topic: str,
        summaries: List[Dict[str, Any]],
        cross_references: Dict[str, Any]
    ) -> str:
        """
        Create comprehensive synthesis prompt
        
        Args:
            topic: Research topic
            summaries: Paper summaries
            cross_references: Cross-reference analysis
        
        Returns:
            Formatted prompt
        """
        # Format papers
        papers_section = self._format_papers(summaries)
        
        # Format cross-references
        connections = cross_references.get("connections", [])
        contradictions = cross_references.get("contradictions", [])
        gaps = cross_references.get("research_gaps", [])
        
        prompt = f"""
        You are a senior research analyst creating a comprehensive knowledge synthesis.
        
        RESEARCH TOPIC: {topic}
        
        PAPERS ANALYZED:
        {papers_section}
        
        CONNECTIONS IDENTIFIED:
        {self._format_list(connections)}
        
        CONTRADICTIONS FOUND:
        {self._format_list(contradictions)}
        
        RESEARCH GAPS:
        {self._format_list(gaps)}
        
        Create a COMPREHENSIVE RESEARCH SYNTHESIS that includes:
        
        1. EXECUTIVE SUMMARY (4-5 sentences)
           - Current state of the field
           - Major achievements
           - Open questions
        
        2. KEY FINDINGS (synthesized across all papers)
           - What do we now know?
           - What are the major breakthroughs?
           - What are the consensus points?
        
        3. METHODOLOGICAL LANDSCAPE
           - Common approaches
           - Emerging techniques
           - Methodological innovations
        
        4. RESULTS & EVIDENCE
           - Consistent findings across papers
           - Quantitative results (if available)
           - Qualitative insights
        
        5. DEBATES & DISAGREEMENTS
           - Where do researchers disagree?
           - Unresolved questions
           - Alternative perspectives
        
        6. RESEARCH GAPS & OPPORTUNITIES
           - What's missing from current research?
           - Promising directions
           - Methodological needs
        
        7. PRACTICAL IMPLICATIONS
           - Real-world applications
           - Impact on the field
           - Who benefits from this research?
        
        8. FUTURE RESEARCH DIRECTIONS
           - Next logical steps
           - High-priority questions
           - Emerging trends
        
        9. NOTABLE CITATIONS
           - Key papers in this analysis
           - Most influential work
           - Recommended reading order
        
        10. CONCLUSION
            - Synthesis of overall landscape
            - State of the art
            - Long-term outlook
        
        Format as JSON with keys: executive_summary, key_findings (list),
        methodological_landscape, results_evidence, debates, research_gaps (list),
        practical_implications, future_directions (list), notable_citations (list),
        conclusion, full_report (markdown formatted comprehensive report)
        
        Be specific, cite paper titles when relevant, and provide actionable insights.
        """
        
        return prompt
    
    def _format_papers(
        self,
        summaries: List[Dict[str, Any]]
    ) -> str:
        """Format paper summaries for synthesis"""
        formatted = []
        for i, summary in enumerate(summaries, 1):
            text = f"""
            [{i}] "{summary.get('title', 'Unknown')}"
                Authors: {', '.join(summary.get('authors', [])[:2])} et al.
                Year: {summary.get('published_date', 'Unknown')[:4]}
                Summary: {summary.get('executive_summary', 'N/A')}
                Key Contribution: {summary.get('contributions', 'N/A')}
            """
            formatted.append(text)
        
        return "\n".join(formatted)
    
    def _format_list(
        self,
        items: List[Any]
    ) -> str:
        """Format list items for display"""
        if not items:
            return "None identified"
        
        if isinstance(items[0], dict):
            formatted = []
            for item in items:
                desc = item.get('description', str(item))
                formatted.append(f"- {desc}")
            return "\n".join(formatted)
        else:
            return "\n".join([f"- {item}" for item in items])
    
    def _parse_synthesis_response(
        self,
        response_text: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        Parse synthesis response into structured format
        
        Args:
            response_text: Raw LLM response
            topic: Research topic
        
        Returns:
            Structured synthesis dictionary
        """
        try:
            # Clean and parse JSON
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            synthesis = json.loads(cleaned)
            
            # Ensure all required fields exist
            required_fields = [
                "executive_summary",
                "key_findings",
                "research_gaps",
                "future_directions"
            ]
            
            for field in required_fields:
                if field not in synthesis:
                    synthesis[field] = []
            
            # Add metadata
            synthesis["topic"] = topic
            synthesis["papers_analyzed"] = self._count_papers(response_text)
            
            return synthesis
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON synthesis, using text format")
            return {
                "topic": topic,
                "executive_summary": response_text[:500],
                "full_report": response_text,
                "key_findings": [],
                "research_gaps": [],
                "future_directions": [],
                "parse_error": True
            }
    
    def _count_papers(self, text: str) -> int:
        """Estimate number of papers mentioned in synthesis"""
        # Simple heuristic: count paper references
        count = text.count('[1]') or text.count('Paper 1')
        return max(count, 1)

