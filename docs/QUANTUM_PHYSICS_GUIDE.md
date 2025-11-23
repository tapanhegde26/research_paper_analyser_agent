# Domain-Specific Customization Guide

## 🔬 Adapting for Quantum Physics Research

This guide shows how to customize the Research Paper Analyzer for specific domains like quantum physics.

---

## 🎯 Quick Start - Change Topic Only

### **Option 1: Modify main.py (Simplest)**

Edit `src/main.py` line 47-49:

```python
topic = "Quantum Entanglement and Non-locality"  # Your quantum topic
num_papers = 10  # How many papers to analyze
depth = "comprehensive"  # Analysis depth
```

### **Option 2: Use the Quantum Physics Analyzer**

```bash
python quantum_physics_analyzer.py
```

This specialized script includes:
- 12 pre-defined quantum physics topics
- Domain-specific questions
- Comparative analysis features

---

## 📚 Quantum Physics Topics (Pre-configured)

The system works out-of-the-box for these topics:

### **Quantum Computing**
- `"Quantum Computing Algorithms and Error Correction"`
- `"Quantum Supremacy and Computational Advantage"`
- `"Quantum Machine Learning Applications"`
- `"Superconducting Quantum Computing"`
- `"Ion Trap Quantum Computing"`

### **Quantum Information**
- `"Quantum Entanglement and Non-locality"`
- `"Quantum Cryptography and Quantum Key Distribution"`
- `"Quantum Teleportation and Quantum Communication"`

### **Quantum Foundations**
- `"Foundations of Quantum Mechanics and Interpretations"`
- `"Quantum Decoherence and Environmental Interactions"`

### **Applications**
- `"Quantum Sensors and Metrology"`
- `"Quantum Optics and Photonics"`
- `"Quantum Materials and Topological Phases"`
- `"Quantum Simulation of Physical Systems"`

---

## 🛠️ Advanced Customization

### **1. Domain-Specific Prompts**

If you want more physics-specific analysis, modify the agent prompts:

**Edit `src/agents/summary_agent.py`** (line ~85):

```python
# Add physics-specific instructions
if depth == "comprehensive":
    prompt = f"""
    {base_info}
    
    Provide a COMPREHENSIVE analysis for this QUANTUM PHYSICS paper:
    
    1. Executive Summary (3-4 sentences)
    2. Physical System/Phenomenon Studied
    3. Theoretical Framework (Hamiltonians, formalisms used)
    4. Experimental Setup (if applicable)
    5. Key Results (with quantitative metrics: fidelities, rates, etc.)
    6. Implications for quantum technology
    7. Open questions
    
    Format as JSON with appropriate keys.
    """
```

### **2. Physics-Specific Cross-Reference Questions**

**Edit `src/agents/cross_reference_agent.py`** (line ~50):

```python
prompt = f"""
You are analyzing QUANTUM PHYSICS papers.

Analyze these papers focusing on:

1. THEORETICAL APPROACHES:
   - What formalisms are used (density matrix, path integral, etc.)?
   - Are approaches complementary or competing?

2. EXPERIMENTAL TECHNIQUES:
   - What measurement methods are used?
   - Can techniques be combined?

3. PHYSICAL SYSTEMS:
   - What quantum systems are studied (atoms, photons, qubits)?
   - Are there universal principles?

4. QUANTUM METRICS:
   - Fidelity, coherence times, error rates
   - How do results compare quantitatively?

5. TECHNOLOGY READINESS:
   - Which approaches are closer to applications?
   - What are the scalability challenges?
"""
```

### **3. Add arXiv Category Filtering**

**Edit `src/agents/retrieval_agent.py`** (line ~90):

```python
async def _search_arxiv(
    self,
    query: str,
    max_results: int,
    category: str = "quant-ph"  # Add category parameter
) -> List[Dict[str, Any]]:
    """
    Search arXiv for papers in specific category
    
    arXiv categories for physics:
    - quant-ph: Quantum Physics
    - cond-mat: Condensed Matter
    - hep-th: High Energy Physics - Theory
    - physics.atom-ph: Atomic Physics
    - physics.optics: Optics
    """
    # Modify search to include category
    search = arxiv.Search(
        query=f"cat:{category} AND {query}",  # Category filter
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    # Rest of the code...
```

---

## 🔍 Example Queries for Quantum Physics

### **Good Topics (Specific)**
✅ `"Topological quantum error correction codes"`
✅ `"Superconducting qubit coherence times"`
✅ `"Quantum advantage in optimization problems"`
✅ `"Photonic quantum computing with squeezed light"`

### **Too Broad (Avoid)**
❌ `"Quantum mechanics"`
❌ `"Quantum physics"`
❌ `"Physics"`

### **Multi-Aspect Analysis**
```python
# Compare different quantum computing platforms
topics = [
    "Superconducting quantum computing coherence",
    "Ion trap quantum computing fidelity",
    "Photonic quantum computing scalability"
]

for topic in topics:
    result = await orchestrator.analyze_topic(topic, num_papers=5)
```

---

## 📊 Domain-Specific Q&A Questions

After analysis, ask physics-specific questions:

```python
qa_agent = orchestrator.get_qa_agent()

# Theoretical questions
await qa_agent.ask("What Hamiltonian formulations are used?")
await qa_agent.ask("What approximations are made in the theory?")

# Experimental questions
await qa_agent.ask("What are the typical coherence times achieved?")
await qa_agent.ask("What measurement techniques are employed?")

# Application questions
await qa_agent.ask("What are the near-term quantum computing applications?")
await qa_agent.ask("What are the main scalability challenges?")

# Comparison questions
await qa_agent.ask("How do different qubit platforms compare?")
await qa_agent.ask("Which approach has the highest gate fidelity?")
```

---

## 🎨 Custom Output Formatting

### **Add Physics Notation Support**

**Edit `src/agents/synthesis_agent.py`** to format LaTeX equations:

```python
def _format_physics_report(self, synthesis: Dict) -> str:
    """Format report with physics notation"""
    
    report = f"""
# Quantum Physics Research Synthesis

## Key Physical Quantities

| Quantity | Value | Paper |
|----------|-------|-------|
| Coherence Time (T₂) | ... | ... |
| Gate Fidelity | ... | ... |
| Error Rate | ... | ... |

## Theoretical Frameworks

- **Hamiltonian Formulation**: H = ...
- **Density Matrix Evolution**: ρ(t) = ...

## Experimental Setups

...
    """
    return report
```

---

## 🚀 Running Physics-Specific Analysis

### **Method 1: Use Main Script**
```bash
cd /Users/thegde/learning/sai-kumar-projects/research-paper-analyzer-agent
python src/main.py
```

### **Method 2: Use Quantum Analyzer**
```bash
python quantum_physics_analyzer.py
```

### **Method 3: Custom Script**
```python
import asyncio
from agents.orchestrator import ResearchOrchestrator

async def analyze():
    orchestrator = ResearchOrchestrator()
    
    # Analyze quantum topic
    result = await orchestrator.analyze_topic(
        topic="Quantum error correction with surface codes",
        num_papers=15,
        depth="comprehensive"
    )
    
    # Domain-specific questions
    qa = orchestrator.get_qa_agent()
    
    answer1 = await qa.ask("What logical error rates are achieved?")
    answer2 = await qa.ask("What physical qubit requirements are needed?")
    answer3 = await qa.ask("How does this compare to other error correction codes?")

asyncio.run(analyze())
```

---

## 📝 Tips for Quantum Physics Research

### **1. Be Specific with Subfields**
- Instead of "quantum computing", use "superconducting transmon qubits"
- Instead of "quantum cryptography", use "BB84 protocol security proofs"

### **2. Include Physical Quantities**
- "Quantum entanglement with fidelity > 0.99"
- "Photon pair generation rates in SPDC"
- "Decoherence times in trapped ions"

### **3. Specify Theoretical/Experimental**
- "Theoretical approaches to..." or "Experimental demonstrations of..."
- This helps the retrieval agent find relevant papers

### **4. Use Standard Physics Terminology**
- Use terms like: Hamiltonian, unitary, density matrix, coherence, fidelity
- The system will find papers using these terms

### **5. Combine Methods and Applications**
- "Variational quantum eigensolver for molecular simulation"
- "Quantum annealing for optimization problems"

---

## 🔧 Troubleshooting

### **Too Few Papers Found**
- Broaden the topic slightly
- Increase `num_papers` parameter
- Remove overly specific constraints

### **Irrelevant Papers Returned**
- Make topic more specific
- Add domain keywords: "quantum", "coherence", "fidelity"
- Specify the arxiv category (see customization above)

### **Analysis Too Generic**
- Customize prompts (see Advanced Customization)
- Use "comprehensive" depth
- Ask more specific follow-up questions

---

## ✅ You're Ready!

The system now works for quantum physics! Just run:

```bash
# Standard analysis
python src/main.py

# Or quantum-specific
python quantum_physics_analyzer.py
```

**Your current configuration:**
- ✅ Model: gemini-2.0-flash-exp
- ✅ Topic: Quantum Entanglement and Non-locality
- ✅ Papers: 10
- ✅ Depth: comprehensive

**Happy quantum research! 🔬⚛️**

