"""
Example usage of the Research Paper Analyzer Agent
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from agents.orchestrator import ResearchOrchestrator


async def basic_analysis_example():
    """Basic analysis example"""
    print("Example 1: Basic Research Analysis\n")
    
    # Create orchestrator
    orchestrator = ResearchOrchestrator()
    
    # Analyze a topic
    result = await orchestrator.analyze_topic(
        topic="Transformer architectures in deep learning",
        num_papers=5,
        depth="standard"
    )
    
    print(f"Analyzed {result.papers_analyzed} papers")
    print(f"Summary: {result.summary[:200]}...")
    print()


async def interactive_qa_example():
    """Interactive Q&A example"""
    print("Example 2: Interactive Q&A\n")
    
    orchestrator = ResearchOrchestrator()
    
    # First analyze
    result = await orchestrator.analyze_topic(
        topic="Neural machine translation",
        num_papers=5,
        depth="comprehensive"
    )
    
    # Then ask questions
    qa_agent = orchestrator.get_qa_agent()
    
    questions = [
        "What are the main approaches to neural machine translation?",
        "What are the limitations of current methods?",
        "What future research directions are suggested?"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        answer = await qa_agent.ask(question)
        print(f"A: {answer}\n")


async def comparison_example():
    """Compare specific papers"""
    print("Example 3: Paper Comparison\n")
    
    orchestrator = ResearchOrchestrator()
    
    # Compare two papers
    paper_urls = [
        "https://arxiv.org/abs/1706.03762",  # Attention is All You Need
        "https://arxiv.org/abs/1810.04805",  # BERT
    ]
    
    comparison = await orchestrator.compare_papers(paper_urls)
    
    print("Comparison Results:")
    print(f"Similarities: {comparison.get('similarities', [])}")
    print(f"Differences: {comparison.get('differences', [])}")
    print()


async def session_resume_example():
    """Resume a previous session"""
    print("Example 4: Session Resume\n")
    
    # Create initial session
    orchestrator1 = ResearchOrchestrator()
    result1 = await orchestrator1.analyze_topic(
        topic="Reinforcement learning",
        num_papers=3,
        depth="quick"
    )
    
    session_id = orchestrator1.get_session_id()
    print(f"Created session: {session_id}")
    
    # Resume session
    orchestrator2 = ResearchOrchestrator(session_id=session_id)
    print(f"Resumed session: {session_id}")
    
    # Access previous analysis
    qa_agent = orchestrator2.get_qa_agent()
    if qa_agent:
        answer = await qa_agent.ask("Summarize the key findings")
        print(f"Answer: {answer}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("Research Paper Analyzer Agent - Examples")
    print("=" * 70)
    print()
    
    # Run examples
    asyncio.run(basic_analysis_example())
    # asyncio.run(interactive_qa_example())
    # asyncio.run(comparison_example())
    # asyncio.run(session_resume_example())

