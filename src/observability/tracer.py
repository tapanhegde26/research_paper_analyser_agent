"""
Tracing Support

OpenTelemetry-style tracing for agent operations.
Tracks operation flow, timing, and dependencies.
"""

import time
import functools
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import json

from observability.logger import get_logger

logger = get_logger(__name__)


class Trace:
    """Represents a single trace/span"""
    
    def __init__(
        self,
        name: str,
        parent_trace: Optional['Trace'] = None
    ):
        self.name = name
        self.parent = parent_trace
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.attributes: Dict[str, Any] = {}
        self.status = "started"
        self.error: Optional[str] = None
        
        # Generate trace ID
        if parent_trace:
            self.trace_id = parent_trace.trace_id
            self.span_id = self._generate_span_id()
            self.parent_span_id = parent_trace.span_id
        else:
            self.trace_id = self._generate_trace_id()
            self.span_id = self._generate_span_id()
            self.parent_span_id = None
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        import uuid
        return str(uuid.uuid4())[:16]
    
    def _generate_span_id(self) -> str:
        """Generate unique span ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def add_attribute(self, key: str, value: Any):
        """Add attribute to trace"""
        self.attributes[key] = value
    
    def end(self, status: str = "completed", error: Optional[str] = None):
        """End the trace"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        self.error = error
        
        # Log trace completion
        self._log_trace()
    
    def _log_trace(self):
        """Log trace information"""
        trace_data = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "duration_ms": round(self.duration * 1000, 2) if self.duration else None,
            "status": self.status,
            "attributes": self.attributes
        }
        
        if self.error:
            trace_data["error"] = self.error
        
        if self.status == "completed":
            logger.info(f"Trace: {self.name}", extra={"extra_fields": trace_data})
        else:
            logger.error(f"Trace failed: {self.name}", extra={"extra_fields": trace_data})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status,
            "error": self.error,
            "attributes": self.attributes
        }


# Global trace context
_current_trace: Optional[Trace] = None


@contextmanager
def trace_context(name: str, **attributes):
    """
    Context manager for tracing operations
    
    Usage:
        with trace_context("operation_name", param1="value1"):
            # Your code here
            pass
    """
    global _current_trace
    
    parent_trace = _current_trace
    trace = Trace(name, parent_trace)
    
    # Add attributes
    for key, value in attributes.items():
        trace.add_attribute(key, value)
    
    # Set as current trace
    _current_trace = trace
    
    try:
        yield trace
        trace.end(status="completed")
    except Exception as e:
        trace.end(status="failed", error=str(e))
        raise
    finally:
        # Restore parent trace
        _current_trace = parent_trace


def trace_operation(operation_name: str) -> Callable:
    """
    Decorator for tracing operations
    
    Usage:
        @trace_operation("my_operation")
        async def my_function(arg1, arg2):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with trace_context(operation_name) as trace:
                # Add function args as attributes
                if args:
                    trace.add_attribute("args_count", len(args))
                if kwargs:
                    trace.add_attribute("kwargs_keys", list(kwargs.keys()))
                
                result = await func(*args, **kwargs)
                return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with trace_context(operation_name) as trace:
                # Add function args as attributes
                if args:
                    trace.add_attribute("args_count", len(args))
                if kwargs:
                    trace.add_attribute("kwargs_keys", list(kwargs.keys()))
                
                result = func(*args, **kwargs)
                return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class TraceCollector:
    """Collects and manages traces"""
    
    def __init__(self):
        self.traces: list = []
    
    def add_trace(self, trace: Trace):
        """Add a trace to collection"""
        self.traces.append(trace.to_dict())
    
    def get_traces(self) -> list:
        """Get all collected traces"""
        return self.traces
    
    def clear(self):
        """Clear all traces"""
        self.traces.clear()
    
    def export_json(self, filepath: str):
        """Export traces to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.traces, f, indent=2)


# Global trace collector
_trace_collector = TraceCollector()


def get_trace_collector() -> TraceCollector:
    """Get the global trace collector"""
    return _trace_collector

