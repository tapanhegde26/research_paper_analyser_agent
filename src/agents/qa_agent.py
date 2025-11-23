"""
Q&A Agent

This agent provides interactive question-answering based on
the analyzed research papers stored in memory.
"""

from typing import Dict, Any, Optional
import json

from memory.memory_bank import MemoryBank
from observability.logger import get_logger
from observability.tracer import trace_operation

logger = get_logger(__name__)


class QAAgent:
    """
    Interactive Q&A agent that answers questions about analyzed research.
    
    Uses memory bank to retrieve relevant context before answering.
    """
    
    def __init__(
        self,
        model,
        memory_bank: MemoryBank,
        session_id: str
    ):
        """
        Initialize Q&A Agent
        
        Args:
            model: Gemini model instance
            memory_bank: Memory bank with stored research
            session_id: Current session ID
        """
        self.model = model
        self.memory_bank = memory_bank
        self.session_id = session_id
        logger.info(f"Q&A Agent initialized for session: {session_id}")
    
    @trace_operation("qa_ask")
    async def ask(
        self,
        question: str,
        context_limit: int = 5
    ) -> str:
        """
        Ask a question about the analyzed research
        
        Args:
            question: User's question
            context_limit: Max number of papers to use as context
        
        Returns:
            Answer string
        """
        logger.info(f"Q&A question: {question[:100]}...")
        
        try:
            # Retrieve relevant context from memory
            context = await self.memory_bank.retrieve_context(
                session_id=self.session_id,
                query=question,
                limit=context_limit
            )
            
            # Create prompt with context
            prompt = self._create_qa_prompt(question, context)
            
            # Generate answer
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            logger.info("Q&A answer generated")
            return answer
            
        except Exception as e:
            logger.error(f"Error in Q&A: {str(e)}", exc_info=True)
            return f"I encountered an error answering your question: {str(e)}"
    
    async def ask_with_citations(
        self,
        question: str,
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Ask a question and get answer with citations
        
        Args:
            question: User's question
            context_limit: Max context papers
        
        Returns:
            Dictionary with answer and citations
        """
        logger.info(f"Q&A with citations: {question[:100]}...")
        
        try:
            # Retrieve context
            context = await self.memory_bank.retrieve_context(
                session_id=self.session_id,
                query=question,
                limit=context_limit
            )
            
            # Create prompt requesting citations
            prompt = self._create_qa_prompt_with_citations(question, context)
            
            # Generate answer
            response = self.model.generate_content(prompt)
            
            # Parse response
            result = self._parse_cited_answer(response.text)
            
            logger.info("Q&A with citations generated")
            return result
            
        except Exception as e:
            logger.error(f"Error in Q&A with citations: {str(e)}", exc_info=True)
            return {
                "answer": f"Error: {str(e)}",
                "citations": []
            }
    
    def _create_qa_prompt(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Create Q&A prompt with context
        
        Args:
            question: User's question
            context: Retrieved context
        
        Returns:
            Formatted prompt
        """
        papers_text = self._format_context(context)
        
        prompt = f"""
        You are a research assistant answering questions based on analyzed papers.
        
        RESEARCH CONTEXT:
        {papers_text}
        
        QUESTION: {question}
        
        Provide a clear, accurate answer based ONLY on the research context provided.
        If the context doesn't contain enough information, say so.
        Be specific and reference paper findings when relevant.
        """
        
        return prompt
    
    def _create_qa_prompt_with_citations(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Create Q&A prompt requesting citations
        
        Args:
            question: User's question
            context: Retrieved context
        
        Returns:
            Formatted prompt
        """
        papers_text = self._format_context(context)
        
        prompt = f"""
        You are a research assistant answering questions with proper citations.
        
        RESEARCH CONTEXT:
        {papers_text}
        
        QUESTION: {question}
        
        Provide a comprehensive answer with citations in this JSON format:
        {{
            "answer": "Your detailed answer here, referencing [Paper ID] when citing",
            "citations": [
                {{
                    "paper_id": "arxiv_id",
                    "title": "Paper title",
                    "relevant_finding": "Specific finding relevant to the question"
                }}
            ],
            "confidence": "high/medium/low based on evidence quality"
        }}
        
        Base your answer ONLY on the provided context.
        """
        
        return prompt
    
    def _format_context(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Format context for prompt
        
        Args:
            context: Context dictionary
        
        Returns:
            Formatted context string
        """
        if not context or "papers" not in context:
            return "No relevant context available."
        
        papers = context["papers"]
        formatted = []
        
        for i, paper in enumerate(papers, 1):
            text = f"""
            [Paper {i}] ID: {paper.get('paper_id', 'unknown')}
            Title: {paper.get('title', 'Unknown')}
            Summary: {paper.get('executive_summary', 'N/A')}
            Key Findings: {paper.get('key_findings', 'N/A')}
            """
            formatted.append(text)
        
        # Include synthesis if available
        if "synthesis" in context:
            formatted.append(f"\n\nRESEARCH SYNTHESIS:\n{context['synthesis']}")
        
        return "\n".join(formatted)
    
    def _parse_cited_answer(
        self,
        response_text: str
    ) -> Dict[str, Any]:
        """
        Parse answer with citations
        
        Args:
            response_text: Raw LLM response
        
        Returns:
            Parsed dictionary
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
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse cited answer, using text")
            return {
                "answer": response_text,
                "citations": [],
                "confidence": "unknown"
            }

