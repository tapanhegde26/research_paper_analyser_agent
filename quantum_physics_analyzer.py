"""
Quantum Physics Research Analyzer

Specialized configuration for analyzing quantum physics research papers.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from agents.orchestrator import ResearchOrchestrator


# Quantum Physics Research Topics
QUANTUM_TOPICS = {
    "entanglement": "Quantum Entanglement and Non-locality",
    "computing": "Quantum Computing Algorithms and Error Correction",
    "cryptography": "Quantum Cryptography and Quantum Key Distribution",
    "teleportation": "Quantum Teleportation and Quantum Communication",
    "decoherence": "Quantum Decoherence and Environmental Interactions",
    "simulation": "Quantum Simulation of Physical Systems",
    "foundations": "Foundations of Quantum Mechanics and Interpretations",
    "optics": "Quantum Optics and Photonics",
    "materials": "Quantum Materials and Topological Phases",
    "sensors": "Quantum Sensors and Metrology",
    "supremacy": "Quantum Supremacy and Computational Advantage",
    "machine_learning": "Quantum Machine Learning Applications"
}


async def analyze_quantum_topic(topic_key: str, num_papers: int = 10):
    """
    Analyze a specific quantum physics topic
    
    Args:
        topic_key: Key from QUANTUM_TOPICS
        num_papers: Number of papers to analyze
    """
    if topic_key not in QUANTUM_TOPICS:
        print(f"❌ Unknown topic: {topic_key}")
        print(f"Available topics: {', '.join(QUANTUM_TOPICS.keys())}")
        return
    
    topic = QUANTUM_TOPICS[topic_key]
    
    print("=" * 70)
    print("🔬 Quantum Physics Research Analyzer")
    print("=" * 70)
    print(f"\n📚 Topic: {topic}")
    print(f"📄 Papers to analyze: {num_papers}\n")
    
    # Create orchestrator
    orchestrator = ResearchOrchestrator()
    
    # Analyze the topic
    result = await orchestrator.analyze_topic(
        topic=topic,
        num_papers=num_papers,
        depth="comprehensive"
    )
    
    # Display results
    print("\n" + "=" * 70)
    print("📊 ANALYSIS RESULTS")
    print("=" * 70)
    print(f"\n✅ Papers Analyzed: {result.papers_analyzed}")
    print(f"\n📝 Executive Summary:\n{result.summary}\n")
    
    print("🔑 Key Findings:")
    for i, finding in enumerate(result.key_findings[:5], 1):
        print(f"{i}. {finding}")
    
    print("\n🔬 Research Gaps:")
    for i, gap in enumerate(result.research_gaps[:3], 1):
        print(f"{i}. {gap}")
    
    # Interactive Q&A
    print("\n" + "=" * 70)
    print("💬 Ask questions about the research")
    print("=" * 70)
    
    qa_agent = orchestrator.get_qa_agent()
    if qa_agent:
        # Example questions specific to quantum physics
        questions = [
            "What are the main experimental challenges?",
            "What theoretical frameworks are being used?",
            "What are the potential applications?",
        ]
        
        for question in questions:
            print(f"\n❓ {question}")
            answer = await qa_agent.ask(question)
            print(f"💡 {answer[:300]}...")
    
    print("\n" + "=" * 70)
    print("✅ Analysis Complete!")
    print("=" * 70)


async def compare_quantum_approaches():
    """
    Compare different approaches in quantum computing
    """
    print("=" * 70)
    print("🔬 Comparing Quantum Computing Approaches")
    print("=" * 70)
    
    orchestrator = ResearchOrchestrator()
    
    # Analyze multiple related topics
    topics = [
        "Superconducting Quantum Computing",
        "Ion Trap Quantum Computing",
        "Topological Quantum Computing"
    ]
    
    for topic in topics:
        print(f"\n📚 Analyzing: {topic}")
        result = await orchestrator.analyze_topic(
            topic=topic,
            num_papers=5,
            depth="standard"
        )
        print(f"✓ Completed: {result.papers_analyzed} papers")


async def quantum_literature_review():
    """
    Comprehensive literature review on a quantum topic
    """
    print("=" * 70)
    print("🔬 Quantum Physics Literature Review")
    print("=" * 70)
    
    # Ask user for topic
    print("\nAvailable topics:")
    for i, (key, topic) in enumerate(QUANTUM_TOPICS.items(), 1):
        print(f"{i:2d}. {key:20s} - {topic}")
    
    print("\nEnter topic key (or press Enter for 'entanglement'): ", end="")
    
    # For demo, use default
    topic_key = "entanglement"
    
    await analyze_quantum_topic(topic_key, num_papers=15)


# Main execution
if __name__ == "__main__":
    print("\n🔬 Quantum Physics Research Analyzer")
    print("=" * 70)
    print("\nChoose an option:")
    print("1. Analyze a specific topic")
    print("2. Compare quantum computing approaches")
    print("3. Full literature review")
    print()
    
    # For demo, run option 1
    print("Running: Analyze Quantum Entanglement\n")
    asyncio.run(analyze_quantum_topic("entanglement", num_papers=10))

