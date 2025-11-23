"""
Paper Retrieval Agent

This agent is responsible for finding and retrieving relevant research papers
from various sources including arXiv, Semantic Scholar, and Google Scholar.

Tools Used:
- arXiv API integration
- Google Search API
- Custom PDF downloader
"""

import arxiv
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from observability.logger import get_logger
from observability.tracer import trace_operation

logger = get_logger(__name__)


class PaperRetrievalAgent:
    """
    Agent specialized in retrieving research papers from multiple sources.
    
    Capabilities:
    - Search arXiv by topic/keywords
    - Fetch specific papers by URL
    - Download and parse PDFs
    - Extract metadata
    """
    
    def __init__(self, model):
        """
        Initialize the Paper Retrieval Agent
        
        Args:
            model: Gemini model instance for intelligent query refinement
        """
        self.model = model
        self.arxiv_client = arxiv.Client()
        logger.info("Paper Retrieval Agent initialized")
    
    @trace_operation("search_papers")
    async def search_papers(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search for papers related to a topic
        
        Args:
            query: Search query
            max_results: Maximum number of results
            sort_by: Sort criteria ("relevance", "date", "citations")
        
        Returns:
            List of paper metadata dictionaries
        """
        logger.info(f"Searching for papers: '{query}'")
        
        try:
            # Step 1: Refine query using LLM
            refined_query = await self._refine_query(query)
            logger.info(f"Refined query: '{refined_query}'")
            
            # Step 2: Search arXiv
            arxiv_results = await self._search_arxiv(
                refined_query,
                max_results
            )
            
            # Step 3: Enrich with additional metadata
            enriched_papers = []
            for paper in arxiv_results:
                enriched = await self._enrich_paper_metadata(paper)
                enriched_papers.append(enriched)
            
            logger.info(f"Retrieved {len(enriched_papers)} papers")
            return enriched_papers
            
        except Exception as e:
            logger.error(f"Error searching papers: {str(e)}", exc_info=True)
            raise
    
    async def _refine_query(self, query: str) -> str:
        """
        Use LLM to refine search query for better results
        
        Args:
            query: Original query
        
        Returns:
            Refined query string
        """
        prompt = f"""
        You are a research librarian expert. Refine this research query to get 
        better results from academic databases like arXiv.
        
        Original query: {query}
        
        Provide a refined query that:
        1. Uses proper academic terminology
        2. Includes relevant keywords
        3. Is specific but not overly narrow
        
        Return ONLY the refined query, no explanation.
        """
        
        try:
            response = self.model.generate_content(prompt)
            refined = response.text.strip()
            return refined
        except Exception as e:
            logger.warning(f"Query refinement failed, using original: {str(e)}")
            return query
    
    async def _search_arxiv(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            List of paper dictionaries
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in self.arxiv_client.results(search):
            paper = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "published_date": result.published.isoformat(),
                "updated_date": result.updated.isoformat(),
                "arxiv_id": result.entry_id.split("/")[-1],
                "pdf_url": result.pdf_url,
                "categories": result.categories,
                "primary_category": result.primary_category,
                "comment": result.comment,
                "journal_ref": result.journal_ref,
                "doi": result.doi,
                "source": "arxiv"
            }
            papers.append(paper)
        
        return papers
    
    async def _enrich_paper_metadata(
        self,
        paper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich paper metadata with additional information
        
        Args:
            paper: Base paper dictionary
        
        Returns:
            Enriched paper dictionary
        """
        # Add retrieval timestamp
        paper["retrieved_at"] = datetime.now().isoformat()
        
        # TODO: Add citation count from Semantic Scholar
        # TODO: Add related papers
        # TODO: Add influence metrics
        
        return paper
    
    async def fetch_papers(
        self,
        paper_urls: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Fetch specific papers by URL
        
        Args:
            paper_urls: List of paper URLs
        
        Returns:
            List of paper metadata
        """
        papers = []
        for url in paper_urls:
            if "arxiv.org" in url:
                # Extract arXiv ID from URL
                arxiv_id = url.split("/")[-1].replace(".pdf", "")
                paper = await self._fetch_arxiv_by_id(arxiv_id)
                if paper:
                    papers.append(paper)
        
        return papers
    
    async def _fetch_arxiv_by_id(
        self,
        arxiv_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific arXiv paper by ID
        
        Args:
            arxiv_id: arXiv paper ID
        
        Returns:
            Paper metadata or None
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(self.arxiv_client.results(search))
            
            if results:
                result = results[0]
                return {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "published_date": result.published.isoformat(),
                    "arxiv_id": arxiv_id,
                    "pdf_url": result.pdf_url,
                    "categories": result.categories,
                    "source": "arxiv"
                }
        except Exception as e:
            logger.error(f"Error fetching arXiv paper {arxiv_id}: {str(e)}")
        
        return None

