# Detailed Architecture Documentation

## System Overview

The Research Paper Analyzer is a sophisticated multi-agent system designed to automatically analyze research papers, extract key insights, identify connections between papers, and provide interactive Q&A capabilities.

## Multi-Agent Architecture

### Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│                   (Coordination Layer)                       │
│  - Workflow management                                       │
│  - Agent coordination                                        │
│  - State management                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    [Session]         [Memory]
         │                 │
    ┌────┴────┐      ┌─────┴──────┐
    │         │      │            │
    ▼         ▼      ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Execution Layer                            │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Retrieval  │  │   Summary   │  │Cross-Refer. │         │
│  │   Agent     │  │Agent (Pool) │  │   Agent     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ Synthesis   │  │     Q&A     │                          │
│  │   Agent     │  │   Agent     │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    [Tools]          [Observability]
```

## Agent Details

### 1. Orchestrator Agent

**Responsibility:** Main coordination and workflow management

**Key Features:**
- Manages the entire analysis pipeline
- Coordinates sub-agents
- Handles session state
- Implements pause/resume for long-running operations
- Manages memory and context

**Workflow:**
```
1. Initialize session
2. Delegate to Retrieval Agent
3. Create pool of Summary Agents (parallel)
4. Delegate to Cross-Reference Agent
5. Delegate to Synthesis Agent
6. Store in Memory Bank
7. Initialize Q&A Agent
```

### 2. Retrieval Agent

**Responsibility:** Finding and fetching research papers

**Tools Used:**
- arXiv API
- Google Search (optional)
- Custom PDF downloader

**Process:**
1. Receive search query
2. Refine query using LLM
3. Search arXiv
4. Fetch paper metadata
5. Enrich with additional information
6. Return paper list

**Key Features:**
- Intelligent query refinement
- Multi-source search
- Metadata enrichment

### 3. Summary Agent (Pool)

**Responsibility:** Extracting key information from papers

**Parallel Execution:**
- Multiple instances run simultaneously
- Configured max parallel: 5 (default)
- Load balanced by orchestrator

**Extraction Tasks:**
- Executive summary
- Key contributions
- Methodology overview
- Main results
- Limitations
- Future work

**Output Format:**
```json
{
  "paper_id": "arxiv_id",
  "title": "...",
  "executive_summary": "...",
  "contributions": [...],
  "methodology": "...",
  "results": "...",
  "limitations": "..."
}
```

### 4. Cross-Reference Agent

**Responsibility:** Finding connections between papers

**Analysis Types:**
1. **Connections:** Papers that build on each other
2. **Contradictions:** Conflicting findings
3. **Research Gaps:** Unanswered questions
4. **Citation Network:** Reference relationships
5. **Temporal Evolution:** How field has evolved

**Output Structure:**
```json
{
  "connections": [
    {
      "paper_ids": ["id1", "id2"],
      "description": "...",
      "significance": "..."
    }
  ],
  "contradictions": [...],
  "research_gaps": [...],
  "citation_network": {...}
}
```

### 5. Synthesis Agent

**Responsibility:** Creating comprehensive knowledge synthesis

**Synthesis Components:**
1. Executive summary of field
2. Key findings synthesis
3. Methodological landscape
4. Results & evidence
5. Debates & disagreements
6. Research gaps & opportunities
7. Practical implications
8. Future directions
9. Notable citations
10. Conclusion

**Output:** Markdown-formatted comprehensive report

### 6. Q&A Agent

**Responsibility:** Interactive question answering

**Features:**
- Context-aware responses
- Citation support
- Memory-backed answers
- Confidence scoring

**Process:**
1. Receive question
2. Retrieve relevant context from Memory Bank
3. Generate answer with LLM
4. Include citations
5. Return response

## Data Flow

```
User Query
    │
    ▼
Orchestrator
    │
    ├─► Retrieval Agent ──► Papers
    │                          │
    │                          ▼
    ├─► Summary Agents (Parallel) ──► Summaries
    │                                     │
    │                                     ▼
    ├─► Cross-Reference Agent ──► Analysis
    │                                     │
    │                                     ▼
    ├─► Synthesis Agent ──► Report
    │                          │
    │                          ▼
    └─► Memory Bank ──► Q&A Agent ──► Answers
```

## Memory & Session Management

### Session Manager

**Purpose:** Manages user sessions with state persistence

**Features:**
- Session creation/resume
- State management (active, paused, ended)
- Data storage per session
- Session cleanup

**Implementation:** InMemorySessionService pattern

### Memory Bank

**Purpose:** Long-term storage for analyzed papers

**Features:**
- Stores papers, summaries, analyses
- Semantic search (simplified in this implementation)
- Cross-session access
- Context retrieval for Q&A

**Storage Structure:**
```
{
  "session_id": {
    "topic": "...",
    "papers": [...],
    "summaries": [...],
    "cross_references": {...},
    "synthesis": {...}
  }
}
```

## Observability

### Logging

- **Format:** JSON (structured) or Standard (colored)
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output:** Console + File (optional)

### Tracing

- **Style:** OpenTelemetry-inspired
- **Tracks:** Operation flow, timing, dependencies
- **Components:** Traces, Spans, Attributes

**Example Trace:**
```
trace_id: abc123
  span_id: span1 [orchestrator.analyze_topic]
    span_id: span2 [retrieval_agent.search_papers]
    span_id: span3 [summary_agent.summarize] (parallel)
    span_id: span4 [summary_agent.summarize] (parallel)
```

### Metrics

- **Style:** Prometheus-compatible
- **Types:** Counter, Gauge, Histogram
- **Export:** JSON, Prometheus format

**Key Metrics:**
- `agent_operations_total`: Counter
- `papers_retrieved_total`: Counter
- `agent_operation_duration_seconds`: Histogram
- `active_sessions`: Gauge
- `memory_size_mb`: Gauge

## Evaluation Framework

### Quality Metrics

1. **Summary Quality (0-1)**
   - Accuracy
   - Completeness
   - Clarity
   - Conciseness

2. **Citation Accuracy (0-1)**
   - Papers cited correctly
   - Attribution accuracy

3. **Response Time**
   - Total duration
   - Time per paper
   - Target: < 60s per paper

4. **Cost Efficiency**
   - Tokens used
   - Cost per paper
   - Target: < $0.20 per paper

### Evaluation Process

```python
evaluator = AgentEvaluator()
results = await evaluator.comprehensive_evaluation(
    analysis_result,
    start_time,
    end_time,
    model
)
```

## Configuration Management

### Config Structure

```python
AppConfig
├── LLMConfig
│   ├── model: "gemini-2.5-flash-lite"
│   ├── temperature: 0.7
│   └── api_key: "..."
├── AgentConfig
│   ├── max_parallel_agents: 5
│   └── max_papers_per_query: 20
├── MemoryConfig
│   ├── backend: "in_memory"
│   └── cache_ttl_hours: 24
├── ObservabilityConfig
│   ├── log_level: "INFO"
│   └── enable_tracing: true
└── EvaluationConfig
    └── enable_evaluation: true
```

### Environment Variables

All configuration can be overridden via environment variables (see `.env.example`).

## Scaling Considerations

### Current Limitations (In-Memory)

- Memory stored in RAM
- Sessions lost on restart
- Single instance only

### Production Recommendations

1. **Memory:** Replace with ChromaDB/Pinecone for vector storage
2. **Session:** Use Redis for distributed sessions
3. **Caching:** Implement PDF caching layer
4. **Queue:** Add task queue (Celery) for parallel processing
5. **API:** Add FastAPI layer for REST API access

## Security Considerations

1. **API Keys:** Never commit to repo
2. **Rate Limiting:** Implement per-user limits
3. **Input Validation:** Sanitize user queries
4. **Output Filtering:** Prevent prompt injection
5. **Access Control:** Add authentication layer

## Extension Points

### Adding New Agents

```python
class MyCustomAgent:
    def __init__(self, model):
        self.model = model
    
    async def process(self, data):
        # Your logic here
        pass
```

### Adding New Tools

```python
# src/tools/my_tool.py
class MyTool:
    def execute(self, params):
        # Tool implementation
        pass
```

### Adding New Metrics

```python
from src.observability.metrics import record_metric

record_metric("my_metric", value, metric_type="counter")
```

## Performance Benchmarks

### Target Metrics

- **Throughput:** 5-7 papers/minute
- **Latency:** < 60s per paper
- **Cost:** < $0.20 per paper
- **Quality:** > 85% accuracy

### Optimization Strategies

1. **Parallel Processing:** Use async/await extensively
2. **Caching:** Cache paper metadata and summaries
3. **Batching:** Group LLM calls where possible
4. **Context Optimization:** Use context compaction for long papers
5. **Model Selection:** Use appropriate model size for task

## Deployment Architecture

### Recommended Stack

```
┌─────────────────────────────────────┐
│         Load Balancer               │
└─────────────┬───────────────────────┘
              │
      ┌───────┴───────┐
      │               │
┌─────▼─────┐   ┌────▼──────┐
│  Agent    │   │  Agent    │
│ Instance  │   │ Instance  │
└─────┬─────┘   └────┬──────┘
      │               │
      └───────┬───────┘
              │
      ┌───────┴──────────┐
      │                  │
┌─────▼─────┐    ┌──────▼──────┐
│   Redis   │    │  ChromaDB   │
│(Sessions) │    │  (Memory)   │
└───────────┘    └─────────────┘
```

## Conclusion

This architecture provides:
- ✅ Scalable multi-agent design
- ✅ Clear separation of concerns
- ✅ Comprehensive observability
- ✅ Flexible configuration
- ✅ Production-ready patterns
- ✅ Extension points for growth

