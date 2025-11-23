"""
Research Paper Analyzer Agent - Orchestrator

This is the main orchestrator agent that coordinates all sub-agents
in the research paper analysis pipeline.

Key Features:
- Coordinates workflow between specialized agents
- Manages parallel processing of papers
- Implements sequential pipeline for analysis
- Provides session and memory management
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import google.generativeai as genai

from config.agent_config import get_config
from agents.retrieval_agent import PaperRetrievalAgent
from agents.summary_agent import SummaryAgent
from agents.cross_reference_agent import CrossReferenceAgent
from agents.synthesis_agent import SynthesisAgent
from agents.qa_agent import QAAgent
from memory.session_manager import SessionManager
from memory.memory_bank import MemoryBank
from observability.logger import get_logger
from observability.tracer import trace_operation
from observability.metrics import record_metric


logger = get_logger(__name__)


@dataclass
class AnalysisResult:
    """Result of research paper analysis"""
    topic: str
    papers_analyzed: int
    summary: str
    key_findings: List[str]
    research_gaps: List[str]
    cross_references: Dict[str, Any]
    synthesis_report: str
    session_id: str
    metadata: Dict[str, Any]


class ResearchOrchestrator:
    """
    Main orchestrator agent that coordinates the multi-agent system
    for research paper analysis.
    
    This agent demonstrates:
    - Multi-agent coordination
    - Parallel processing
    - Sequential workflows
    - Session management
    - Memory integration
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the research orchestrator
        
        Args:
            session_id: Optional session ID to resume previous session
        """
        self.config = get_config()
        
        # Configure Gemini
        genai.configure(api_key=self.config.llm.api_key)
        self.model = genai.GenerativeModel(self.config.llm.model)
        
        # Initialize sub-agents
        self.retrieval_agent = PaperRetrievalAgent(self.model)
        self.cross_reference_agent = CrossReferenceAgent(self.model)
        self.synthesis_agent = SynthesisAgent(self.model)
        
        # Initialize memory and session
        self.session_manager = SessionManager()
        self.memory_bank = MemoryBank()
        
        # Session handling
        if session_id:
            self.session_id = session_id
            self.session_manager.resume_session(session_id)
            logger.info(f"Resumed session: {session_id}")
        else:
            self.session_id = self.session_manager.create_session()
            logger.info(f"Created new session: {self.session_id}")
        
        # QA agent will be initialized after analysis
        self.qa_agent: Optional[QAAgent] = None
        
        logger.info("Research Orchestrator initialized")
    
    @trace_operation("analyze_topic")
    async def analyze_topic(
        self,
        topic: str,
        num_papers: int = 10,
        depth: str = "comprehensive"
    ) -> AnalysisResult:
        """
        Analyze a research topic by retrieving and synthesizing papers.
        
        This method orchestrates the entire pipeline:
        1. Retrieve relevant papers (Retrieval Agent)
        2. Summarize papers in parallel (Multiple Summary Agents)
        3. Cross-reference findings (Cross-Reference Agent)
        4. Synthesize knowledge (Synthesis Agent)
        5. Store in memory for Q&A
        
        Args:
            topic: Research topic to analyze
            num_papers: Maximum number of papers to analyze
            depth: Analysis depth ("quick", "standard", "comprehensive")
        
        Returns:
            AnalysisResult: Complete analysis results
        """
        logger.info(f"Starting analysis for topic: {topic}")
        record_metric("analysis_started", 1, {"topic": topic})
        
        try:
            # Step 1: Retrieve papers (AGENT 1)
            logger.info("Step 1: Retrieving papers...")
            papers = await self.retrieval_agent.search_papers(
                query=topic,
                max_results=num_papers
            )
            logger.info(f"Retrieved {len(papers)} papers")
            
            # Store in session
            self.session_manager.store_data(
                self.session_id,
                "papers",
                papers
            )
            
            # Step 2: Summarize papers in PARALLEL (MULTIPLE SUMMARY AGENTS)
            logger.info("Step 2: Summarizing papers in parallel...")
            summaries = await self._parallel_summarize(papers, depth)
            logger.info(f"Generated {len(summaries)} summaries")
            
            # Store summaries
            self.session_manager.store_data(
                self.session_id,
                "summaries",
                summaries
            )
            
            # Step 3: Cross-reference findings (AGENT N-1)
            logger.info("Step 3: Cross-referencing findings...")
            cross_refs = await self.cross_reference_agent.analyze(
                papers=papers,
                summaries=summaries
            )
            logger.info("Cross-referencing complete")
            
            # Step 4: Synthesize knowledge (AGENT N)
            logger.info("Step 4: Synthesizing knowledge...")
            synthesis = await self.synthesis_agent.synthesize(
                topic=topic,
                summaries=summaries,
                cross_references=cross_refs
            )
            logger.info("Synthesis complete")
            
            # Step 5: Store in long-term memory for Q&A
            logger.info("Step 5: Storing in memory bank...")
            await self.memory_bank.store_analysis(
                session_id=self.session_id,
                topic=topic,
                papers=papers,
                summaries=summaries,
                cross_refs=cross_refs,
                synthesis=synthesis
            )
            
            # Initialize Q&A agent with the analysis
            self.qa_agent = QAAgent(
                model=self.model,
                memory_bank=self.memory_bank,
                session_id=self.session_id
            )
            
            # Create result
            result = AnalysisResult(
                topic=topic,
                papers_analyzed=len(papers),
                summary=synthesis.get("executive_summary", ""),
                key_findings=synthesis.get("key_findings", []),
                research_gaps=synthesis.get("research_gaps", []),
                cross_references=cross_refs,
                synthesis_report=synthesis.get("full_report", ""),
                session_id=self.session_id,
                metadata={
                    "depth": depth,
                    "timestamp": self.session_manager.get_session_time(self.session_id)
                }
            )
            
            record_metric("analysis_completed", 1, {"papers": len(papers)})
            logger.info(f"Analysis complete for topic: {topic}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            record_metric("analysis_failed", 1, {"error": str(e)})
            raise
    
    async def _parallel_summarize(
        self,
        papers: List[Dict[str, Any]],
        depth: str
    ) -> List[Dict[str, Any]]:
        """
        Summarize papers in parallel using multiple Summary Agents.
        
        This demonstrates parallel agent execution for improved performance.
        
        Args:
            papers: List of papers to summarize
            depth: Depth of analysis
        
        Returns:
            List of summaries
        """
        max_parallel = self.config.agent.max_parallel_agents
        
        # Create tasks for parallel execution
        tasks = []
        for paper in papers:
            agent = SummaryAgent(self.model)
            task = agent.summarize(paper, depth)
            tasks.append(task)
        
        # Execute in batches to respect max_parallel_agents
        summaries = []
        for i in range(0, len(tasks), max_parallel):
            batch = tasks[i:i + max_parallel]
            batch_results = await asyncio.gather(*batch)
            summaries.extend(batch_results)
            logger.info(f"Completed batch {i//max_parallel + 1}")
        
        return summaries
    
    async def compare_papers(
        self,
        paper_urls: List[str]
    ) -> Dict[str, Any]:
        """
        Compare specific papers by URL
        
        Args:
            paper_urls: List of paper URLs (arXiv or other)
        
        Returns:
            Comparison results
        """
        logger.info(f"Comparing {len(paper_urls)} papers")
        
        # Retrieve specific papers
        papers = await self.retrieval_agent.fetch_papers(paper_urls)
        
        # Summarize
        summaries = await self._parallel_summarize(papers, "comprehensive")
        
        # Cross-reference for comparison
        comparison = await self.cross_reference_agent.compare(
            papers=papers,
            summaries=summaries
        )
        
        return comparison
    
    def get_qa_agent(self) -> Optional[QAAgent]:
        """
        Get the Q&A agent for interactive queries
        
        Returns:
            QAAgent if analysis has been performed, None otherwise
        """
        return self.qa_agent
    
    def get_session_id(self) -> str:
        """Get the current session ID"""
        return self.session_id
    
    def export_results(self, format: str = "markdown") -> str:
        """
        Export analysis results in specified format
        
        Args:
            format: Output format ("markdown", "pdf", "html")
        
        Returns:
            Path to exported file
        """
        # TODO: Implement export functionality
        pass

