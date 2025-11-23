"""
Memory Bank

Long-term memory storage for research papers and analysis.
Implements vector storage for semantic search and retrieval.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
import json

from observability.logger import get_logger

logger = get_logger(__name__)


class MemoryBank:
    """
    Long-term memory storage for research analysis.
    
    Features:
    - Stores analyzed papers and summaries
    - Semantic search over stored content
    - Context retrieval for Q&A
    - Cross-session memory persistence
    
    Note: This is a simplified in-memory implementation.
    For production, use ChromaDB or similar vector database.
    """
    
    def __init__(self):
        """Initialize memory bank"""
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._session_index: Dict[str, List[str]] = defaultdict(list)
        self._topic_index: Dict[str, List[str]] = defaultdict(list)
        logger.info("Memory Bank initialized")
    
    async def store_analysis(
        self,
        session_id: str,
        topic: str,
        papers: List[Dict[str, Any]],
        summaries: List[Dict[str, Any]],
        cross_refs: Dict[str, Any],
        synthesis: Dict[str, Any]
    ) -> str:
        """
        Store complete analysis in memory
        
        Args:
            session_id: Session identifier
            topic: Research topic
            papers: Original papers
            summaries: Paper summaries
            cross_refs: Cross-reference analysis
            synthesis: Knowledge synthesis
        
        Returns:
            Memory ID
        """
        memory_id = f"{session_id}_{topic.replace(' ', '_')}"
        
        memory_entry = {
            "memory_id": memory_id,
            "session_id": session_id,
            "topic": topic,
            "papers": papers,
            "summaries": summaries,
            "cross_references": cross_refs,
            "synthesis": synthesis,
            "stored_at": self._get_timestamp()
        }
        
        # Store in main storage
        self._storage[memory_id] = memory_entry
        
        # Update indices
        self._session_index[session_id].append(memory_id)
        self._topic_index[topic].append(memory_id)
        
        # Also index individual papers for retrieval
        for paper in papers:
            paper_id = paper.get("arxiv_id", "unknown")
            self._storage[f"paper_{paper_id}"] = paper
        
        logger.info(f"Stored analysis in memory: {memory_id}")
        return memory_id
    
    async def retrieve_context(
        self,
        session_id: str,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query
        
        Args:
            session_id: Session identifier
            query: Search query
            limit: Maximum number of papers to return
        
        Returns:
            Context dictionary with relevant papers and synthesis
        """
        logger.info(f"Retrieving context for query: {query[:100]}...")
        
        # Get all memories for this session
        memory_ids = self._session_index.get(session_id, [])
        
        if not memory_ids:
            logger.warning(f"No memories found for session: {session_id}")
            return {"papers": [], "synthesis": None}
        
        # For now, use simple keyword matching
        # In production, use vector embeddings for semantic search
        relevant_papers = []
        synthesis_data = None
        
        for memory_id in memory_ids:
            memory = self._storage.get(memory_id)
            if not memory:
                continue
            
            # Get synthesis
            if not synthesis_data and "synthesis" in memory:
                synthesis_data = memory["synthesis"].get("executive_summary", "")
            
            # Get papers
            summaries = memory.get("summaries", [])
            for summary in summaries:
                if self._is_relevant(summary, query):
                    relevant_papers.append(summary)
                    if len(relevant_papers) >= limit:
                        break
            
            if len(relevant_papers) >= limit:
                break
        
        return {
            "papers": relevant_papers[:limit],
            "synthesis": synthesis_data
        }
    
    def _is_relevant(
        self,
        paper: Dict[str, Any],
        query: str
    ) -> bool:
        """
        Check if paper is relevant to query (simple keyword matching)
        
        Args:
            paper: Paper dictionary
            query: Search query
        
        Returns:
            True if relevant
        """
        query_lower = query.lower()
        
        # Check title
        title = paper.get("title", "").lower()
        if query_lower in title:
            return True
        
        # Check abstract/summary
        summary = paper.get("executive_summary", "").lower()
        if query_lower in summary:
            return True
        
        # Check key findings
        findings = str(paper.get("key_findings", "")).lower()
        if query_lower in findings:
            return True
        
        # Simple keyword overlap
        query_words = set(query_lower.split())
        content = f"{title} {summary} {findings}"
        content_words = set(content.split())
        
        overlap = len(query_words & content_words)
        return overlap >= min(3, len(query_words))
    
    async def get_session_memories(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of memory entries
        """
        memory_ids = self._session_index.get(session_id, [])
        memories = [
            self._storage[mid]
            for mid in memory_ids
            if mid in self._storage
        ]
        return memories
    
    async def get_topic_memories(
        self,
        topic: str
    ) -> List[Dict[str, Any]]:
        """
        Get all memories related to a topic
        
        Args:
            topic: Research topic
        
        Returns:
            List of memory entries
        """
        memory_ids = self._topic_index.get(topic, [])
        memories = [
            self._storage[mid]
            for mid in memory_ids
            if mid in self._storage
        ]
        return memories
    
    async def search_papers(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for papers across all memories
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching papers
        """
        results = []
        
        for memory_id, memory in self._storage.items():
            if not memory_id.startswith("paper_"):
                continue
            
            if "summaries" in memory:
                for summary in memory["summaries"]:
                    if self._is_relevant(summary, query):
                        results.append(summary)
                        if len(results) >= limit:
                            return results
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory bank statistics
        
        Returns:
            Statistics dictionary
        """
        total_memories = len([k for k in self._storage.keys() if not k.startswith("paper_")])
        total_papers = len([k for k in self._storage.keys() if k.startswith("paper_")])
        total_sessions = len(self._session_index)
        total_topics = len(self._topic_index)
        
        return {
            "total_memories": total_memories,
            "total_papers": total_papers,
            "total_sessions": total_sessions,
            "total_topics": total_topics,
            "storage_size_mb": self._estimate_size()
        }
    
    def _estimate_size(self) -> float:
        """Estimate storage size in MB"""
        try:
            size_bytes = len(json.dumps(self._storage).encode())
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def clear(self):
        """Clear all memory (use with caution!)"""
        self._storage.clear()
        self._session_index.clear()
        self._topic_index.clear()
        logger.warning("Memory bank cleared!")

