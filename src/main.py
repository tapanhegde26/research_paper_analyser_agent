"""
Research Paper Analyzer Agent - Main Entry Point

Multi-agent system for analyzing research papers.
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from agents.orchestrator import ResearchOrchestrator, AnalysisResult
from evaluation.evaluator import AgentEvaluator
from observability.logger import get_logger
from observability.metrics import get_registry
from config.agent_config import get_config

logger = get_logger(__name__)


async def main():
    """Main application entry point"""
    
    print("=" * 70)
    print("🔬 Research Paper Analyzer Agent")
    print("   Multi-Agent System for Knowledge Synthesis")
    print("=" * 70)
    print()
    
    try:
        # Load configuration
        config = get_config()
        logger.info("Configuration loaded successfully")
        
        # Create orchestrator
        print("🤖 Initializing multi-agent system...")
        orchestrator = ResearchOrchestrator()
        print(f"   Session ID: {orchestrator.get_session_id()}")
        print()
        
        # Example analysis
        print("📚 Analyzing research topic...")
        print()
        
        topic = "Quantum Entanglement and Non-locality"
        num_papers = 10
        depth = "comprehensive"
        
        print(f"   Topic: {topic}")
        print(f"   Papers: {num_papers}")
        print(f"   Depth: {depth}")
        print()
        
        start_time = time.time()
        
        # Run analysis
        result = await orchestrator.analyze_topic(
            topic=topic,
            num_papers=num_papers,
            depth=depth
        )
        
        end_time = time.time()
        
        # Display results
        print("\n" + "=" * 70)
        print("📊 ANALYSIS RESULTS")
        print("=" * 70)
        print()
        
        print(f"✅ Papers Analyzed: {result.papers_analyzed}")
        print(f"⏱️  Time Taken: {end_time - start_time:.2f} seconds")
        print()
        
        print("📝 EXECUTIVE SUMMARY")
        print("-" * 70)
        print(result.summary)
        print()
        
        print("🔑 KEY FINDINGS")
        print("-" * 70)
        for i, finding in enumerate(result.key_findings[:5], 1):
            print(f"{i}. {finding}")
        print()
        
        print("🔬 RESEARCH GAPS")
        print("-" * 70)
        for i, gap in enumerate(result.research_gaps[:3], 1):
            print(f"{i}. {gap}")
        print()
        
        # Q&A Demo
        print("\n" + "=" * 70)
        print("💬 INTERACTIVE Q&A DEMO")
        print("=" * 70)
        print()
        
        qa_agent = orchestrator.get_qa_agent()
        if qa_agent:
            questions = [
                "What are the main challenges in using LLMs for code generation?",
                "What methodologies are commonly used?",
            ]
            
            for question in questions:
                print(f"❓ Q: {question}")
                answer = await qa_agent.ask(question)
                print(f"💡 A: {answer[:300]}...")
                print()
        
        # Evaluation
        print("\n" + "=" * 70)
        print("📈 AGENT EVALUATION")
        print("=" * 70)
        print()
        
        evaluator = AgentEvaluator()
        eval_results = await evaluator.comprehensive_evaluation(
            result,
            start_time,
            end_time,
            orchestrator.model
        )
        
        for metric_name, eval_result in eval_results.items():
            print(f"✓ {metric_name.replace('_', ' ').title()}: {eval_result.percentage:.1f}%")
        print()
        
        # Metrics Summary
        print("\n" + "=" * 70)
        print("📊 SYSTEM METRICS")
        print("=" * 70)
        print()
        
        metrics = get_registry().get_all_metrics()
        for name, metric_data in list(metrics.items())[:5]:
            if metric_data['type'] == 'counter':
                print(f"   {name}: {metric_data['value']}")
            elif metric_data['type'] == 'gauge':
                print(f"   {name}: {metric_data['value']}")
        print()
        
        print("=" * 70)
        print("✅ Analysis Complete!")
        print("=" * 70)
        print()
        
        # Save results
        output_dir = Path(config.output.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"analysis_{result.session_id}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Research Analysis: {topic}\n\n")
            f.write(f"Session ID: {result.session_id}\n")
            f.write(f"Papers Analyzed: {result.papers_analyzed}\n\n")
            f.write(f"## Executive Summary\n\n{result.summary}\n\n")
            f.write(f"## Key Findings\n\n")
            for finding in result.key_findings:
                f.write(f"- {finding}\n")
            f.write(f"\n## Research Gaps\n\n")
            for gap in result.research_gaps:
                f.write(f"- {gap}\n")
            f.write(f"\n## Full Report\n\n{result.synthesis_report}\n")
        
        print(f"📄 Results saved to: {output_file}")
        print()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}\n")
        return 1


def run():
    """Run the application"""
    return asyncio.run(main())


if __name__ == "__main__":
    sys.exit(run())

