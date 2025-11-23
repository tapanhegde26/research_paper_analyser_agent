"""
Configuration Management for Research Paper Analyzer Agent

This module handles all configuration settings for the multi-agent system.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMConfig(BaseModel):
    """Configuration for LLM models"""
    model: str = Field(default="gemini-2.0-flash-exp", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=8192, ge=1)
    api_key: str = Field(..., description="Google API Key")


class AgentConfig(BaseModel):
    """Configuration for agent behavior"""
    max_parallel_agents: int = Field(default=5, ge=1, le=20)
    max_papers_per_query: int = Field(default=20, ge=1, le=100)
    enable_context_compaction: bool = Field(default=True)
    arxiv_max_results: int = Field(default=50, ge=1, le=100)


class MemoryConfig(BaseModel):
    """Configuration for memory and storage"""
    backend: str = Field(default="in_memory", description="Memory backend type")
    chroma_persist_dir: str = Field(default="./data/chroma")
    chroma_collection_name: str = Field(default="research_papers")
    cache_dir: str = Field(default="./data/cache")
    cache_ttl_hours: int = Field(default=24, ge=1)
    enable_caching: bool = Field(default=True)


class ObservabilityConfig(BaseModel):
    """Configuration for logging, tracing, and metrics"""
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_file: str = Field(default="./logs/agent.log")
    enable_tracing: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)


class EvaluationConfig(BaseModel):
    """Configuration for agent evaluation"""
    enable_evaluation: bool = Field(default=True)
    output_dir: str = Field(default="./output/evaluation")


class OutputConfig(BaseModel):
    """Configuration for output generation"""
    output_dir: str = Field(default="./output")
    report_format: str = Field(default="markdown")


class AppConfig(BaseModel):
    """Main application configuration"""
    llm: LLMConfig
    agent: AgentConfig
    memory: MemoryConfig
    observability: ObservabilityConfig
    evaluation: EvaluationConfig
    output: OutputConfig
    
    debug_mode: bool = Field(default=False)
    enable_profiling: bool = Field(default=False)


def load_config() -> AppConfig:
    """
    Load configuration from environment variables and defaults
    
    Returns:
        AppConfig: Complete application configuration
    
    Raises:
        ValueError: If required configuration is missing
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is required. "
            "Get your key from https://ai.google.dev/"
        )
    
    return AppConfig(
        llm=LLMConfig(
            model=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192")),
            api_key=api_key
        ),
        agent=AgentConfig(
            max_parallel_agents=int(os.getenv("MAX_PARALLEL_AGENTS", "5")),
            max_papers_per_query=int(os.getenv("MAX_PAPERS_PER_QUERY", "20")),
            enable_context_compaction=os.getenv("ENABLE_CONTEXT_COMPACTION", "true").lower() == "true",
            arxiv_max_results=int(os.getenv("ARXIV_MAX_RESULTS", "50"))
        ),
        memory=MemoryConfig(
            backend=os.getenv("MEMORY_BACKEND", "in_memory"),
            chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"),
            chroma_collection_name=os.getenv("CHROMA_COLLECTION_NAME", "research_papers"),
            cache_dir=os.getenv("CACHE_DIR", "./data/cache"),
            cache_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true"
        ),
        observability=ObservabilityConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            log_file=os.getenv("LOG_FILE", "./logs/agent.log"),
            enable_tracing=os.getenv("ENABLE_TRACING", "true").lower() == "true",
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            metrics_port=int(os.getenv("METRICS_PORT", "9090"))
        ),
        evaluation=EvaluationConfig(
            enable_evaluation=os.getenv("ENABLE_EVALUATION", "true").lower() == "true",
            output_dir=os.getenv("EVALUATION_OUTPUT_DIR", "./output/evaluation")
        ),
        output=OutputConfig(
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            report_format=os.getenv("REPORT_FORMAT", "markdown")
        ),
        debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
        enable_profiling=os.getenv("ENABLE_PROFILING", "false").lower() == "true"
    )


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config

