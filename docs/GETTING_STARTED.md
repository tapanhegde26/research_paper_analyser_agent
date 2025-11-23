# Getting Started with Research Paper Analyzer Agent

This guide will help you get up and running with the Research Paper Analyzer Agent in minutes!

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   ```

2. **Google API Key** for Gemini
   - Get it from: https://ai.google.dev/
   - Free tier available!

3. **Git** (optional, for cloning)

## 🚀 Quick Start (5 minutes)

### Step 1: Navigate to Project Directory

```bash
cd /Users/thegde/learning/sai-kumar-projects/research-paper-analyzer-agent
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This may take a few minutes as it installs all required packages.

### Step 4: Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

**Option B: Create .env file**
```bash
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Step 5: Run the Application!

```bash
python src/main.py
```

You should see:
```
🔬 Research Paper Analyzer Agent
   Multi-Agent System for Knowledge Synthesis
======================================================================

🤖 Initializing multi-agent system...
   Session ID: abc123...

📚 Analyzing research topic...
```

## 📖 Usage Examples

### Example 1: Basic Analysis

```python
import asyncio
from src.agents.orchestrator import ResearchOrchestrator

async def main():
    # Create orchestrator
    orchestrator = ResearchOrchestrator()
    
    # Analyze a topic
    result = await orchestrator.analyze_topic(
        topic="Transformer architectures in NLP",
        num_papers=10,
        depth="comprehensive"
    )
    
    # Display results
    print(f"Papers Analyzed: {result.papers_analyzed}")
    print(f"Summary: {result.summary}")
    print(f"Key Findings: {result.key_findings}")

asyncio.run(main())
```

### Example 2: Interactive Q&A

```python
# After analysis, ask questions
qa_agent = orchestrator.get_qa_agent()

answer = await qa_agent.ask(
    "What are the main challenges in transformer models?"
)
print(answer)
```

### Example 3: Compare Papers

```python
comparison = await orchestrator.compare_papers([
    "https://arxiv.org/abs/1706.03762",  # Attention is All You Need
    "https://arxiv.org/abs/1810.04805",  # BERT
])

print(comparison)
```

## 🎛️ Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional - Model Settings
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192

# Optional - Agent Settings
MAX_PARALLEL_AGENTS=5
MAX_PAPERS_PER_QUERY=20

# Optional - Logging
LOG_LEVEL=INFO
LOG_FORMAT=standard
```

### Depth Levels

Choose analysis depth:

- **`"quick"`** - Fast summary (2-3 papers, 30 seconds)
- **`"standard"`** - Balanced analysis (5-10 papers, 2-3 minutes)
- **`"comprehensive"`** - Deep dive (10-20 papers, 5-10 minutes)

## 📊 Understanding the Output

After analysis, you'll get:

1. **Executive Summary** - High-level overview of the research area
2. **Key Findings** - Main discoveries and contributions
3. **Research Gaps** - Unanswered questions and opportunities
4. **Synthesis Report** - Full detailed analysis
5. **Q&A Agent** - Ask follow-up questions

### Output Files

Results are saved to:
```
output/
  └── analysis_<session_id>.md
```

## 🏗️ Project Structure

```
research-paper-analyzer-agent/
├── src/
│   ├── agents/           # All agent implementations
│   ├── memory/           # Session and memory management
│   ├── observability/    # Logging, tracing, metrics
│   └── evaluation/       # Quality evaluation
├── config/               # Configuration files
├── tests/                # Unit tests
├── docs/                 # Documentation
├── output/              # Generated reports
└── requirements.txt     # Dependencies
```

## 🔧 Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:**
```bash
export GOOGLE_API_KEY="your_key_here"
# Or add to .env file
```

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Rate limit exceeded"

**Solution:**
- Reduce `MAX_PAPERS_PER_QUERY`
- Add delays between requests
- Check your API quota

### Issue: Slow performance

**Solution:**
- Reduce number of papers
- Use "quick" depth mode
- Increase `MAX_PARALLEL_AGENTS` (if you have quota)

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📚 Next Steps

1. **Try the Examples**
   ```bash
   python examples.py
   ```

2. **Read the Architecture**
   - See `docs/architecture.md` for deep dive

3. **Customize Agents**
   - Modify prompts in `src/agents/`
   - Add new tools in `src/tools/`

4. **Deploy**
   - See `docs/deployment.md` for deployment options

## 💡 Tips for Best Results

### 1. Choose Specific Topics
❌ Bad: "AI"
✅ Good: "Transformer attention mechanisms in neural machine translation"

### 2. Start Small
- Begin with 3-5 papers
- Use "quick" or "standard" depth
- Scale up as needed

### 3. Use Q&A Effectively
Ask specific questions:
- "What methods achieved the best results?"
- "What are the common limitations across papers?"
- "Which paper should I read first?"

### 4. Monitor Costs
```python
# Check metrics
from src.observability.metrics import get_registry
metrics = get_registry().get_all_metrics()
print(metrics)
```

## 🎯 Common Use Cases

### Use Case 1: Literature Review
```python
result = await orchestrator.analyze_topic(
    topic="Deep learning for medical imaging",
    num_papers=15,
    depth="comprehensive"
)
# Get comprehensive review with research gaps
```

### Use Case 2: Paper Discovery
```python
result = await orchestrator.analyze_topic(
    topic="Recent advances in reinforcement learning",
    num_papers=20,
    depth="quick"
)
# Quickly scan recent work
```

### Use Case 3: Research Question
```python
# First analyze
result = await orchestrator.analyze_topic(...)

# Then ask specific questions
qa = orchestrator.get_qa_agent()
answer = await qa.ask("Is approach X better than Y?")
```

## 🤝 Getting Help

1. **Check Documentation**
   - README.md
   - docs/architecture.md
   - docs/deployment.md

2. **Review Examples**
   - examples.py
   - tests/test_agents.py

3. **Common Issues**
   - API key problems
   - Rate limiting
   - Memory issues

## 🎓 Learning Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **arXiv API**: https://arxiv.org/help/api
- **Agent Development Kit**: https://github.com/google/adk-python

## ✅ Checklist

Before you start, make sure:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API key configured
- [ ] Test run successful

## 🚀 You're Ready!

Congratulations! You're all set to analyze research papers with AI agents.

Start with:
```bash
python src/main.py
```

Happy researching! 🔬📚

