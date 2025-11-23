"""
Basic tests for the Research Paper Analyzer Agent
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.orchestrator import ResearchOrchestrator
from agents.retrieval_agent import PaperRetrievalAgent
from agents.summary_agent import SummaryAgent
from memory.session_manager import SessionManager
from memory.memory_bank import MemoryBank


class TestSessionManager:
    """Test session management"""
    
    def test_create_session(self):
        """Test session creation"""
        manager = SessionManager()
        session_id = manager.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        
        session = manager.get_session(session_id)
        assert session is not None
        assert session["session_id"] == session_id
        assert session["state"] == "active"
    
    def test_store_and_retrieve_data(self):
        """Test data storage"""
        manager = SessionManager()
        session_id = manager.create_session()
        
        # Store data
        test_data = {"key": "value", "number": 42}
        manager.store_data(session_id, "test", test_data)
        
        # Retrieve data
        retrieved = manager.get_data(session_id, "test")
        assert retrieved == test_data
    
    def test_pause_resume_session(self):
        """Test session pause/resume"""
        manager = SessionManager()
        session_id = manager.create_session()
        
        # Pause session
        assert manager.pause_session(session_id)
        session = manager.get_session(session_id)
        assert session["state"] == "paused"
        
        # Resume session
        assert manager.resume_session(session_id)
        session = manager.get_session(session_id)
        assert session["state"] == "active"


class TestMemoryBank:
    """Test memory bank"""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_analysis(self):
        """Test storing analysis"""
        memory = MemoryBank()
        
        test_papers = [
            {"arxiv_id": "1234", "title": "Test Paper"}
        ]
        test_summaries = [
            {"paper_id": "1234", "executive_summary": "Test summary"}
        ]
        
        memory_id = await memory.store_analysis(
            session_id="test_session",
            topic="Test Topic",
            papers=test_papers,
            summaries=test_summaries,
            cross_refs={},
            synthesis={}
        )
        
        assert memory_id is not None
        
        # Retrieve
        memories = await memory.get_session_memories("test_session")
        assert len(memories) > 0
        assert memories[0]["topic"] == "Test Topic"
    
    @pytest.mark.asyncio
    async def test_context_retrieval(self):
        """Test context retrieval"""
        memory = MemoryBank()
        
        # Store test data
        await memory.store_analysis(
            session_id="test",
            topic="Machine Learning",
            papers=[],
            summaries=[{
                "paper_id": "1",
                "title": "ML Paper",
                "executive_summary": "This paper discusses machine learning algorithms"
            }],
            cross_refs={},
            synthesis={}
        )
        
        # Retrieve context
        context = await memory.retrieve_context(
            session_id="test",
            query="machine learning",
            limit=5
        )
        
        assert context is not None
        assert "papers" in context


class TestSummaryAgent:
    """Test summary agent"""
    
    @pytest.mark.asyncio
    async def test_summarize_paper(self):
        """Test paper summarization"""
        # Mock model
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "executive_summary": "Test summary",
            "contributions": ["Contribution 1"],
            "methodology": "Test methodology"
        }
        '''
        mock_model.generate_content = Mock(return_value=mock_response)
        
        agent = SummaryAgent(mock_model)
        
        test_paper = {
            "title": "Test Paper",
            "authors": ["Author 1"],
            "abstract": "Test abstract",
            "arxiv_id": "1234"
        }
        
        summary = await agent.summarize(test_paper, depth="standard")
        
        assert summary is not None
        assert "executive_summary" in summary
        assert summary["title"] == "Test Paper"


class TestRetrievalAgent:
    """Test retrieval agent"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        mock_model = Mock()
        agent = PaperRetrievalAgent(mock_model)
        
        assert agent is not None
        assert agent.model == mock_model


class TestOrchestrator:
    """Test orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator creation"""
        # This will fail without API key, but tests the structure
        try:
            orchestrator = ResearchOrchestrator()
            assert orchestrator is not None
        except ValueError as e:
            # Expected if no API key
            assert "GOOGLE_API_KEY" in str(e)


# Integration tests (require API key)
@pytest.mark.integration
class TestIntegration:
    """Integration tests - require API key"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_flow(self):
        """Test complete analysis flow"""
        # Skip if no API key
        import os
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("No API key available")
        
        orchestrator = ResearchOrchestrator()
        
        # Small test
        result = await orchestrator.analyze_topic(
            topic="test topic",
            num_papers=2,
            depth="quick"
        )
        
        assert result is not None
        assert result.papers_analyzed >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

