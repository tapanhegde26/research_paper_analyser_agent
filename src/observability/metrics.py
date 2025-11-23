"""
Metrics Collection

Prometheus-style metrics for agent performance monitoring.
"""

from typing import Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
import json

from observability.logger import get_logger

logger = get_logger(__name__)


class MetricType:
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class Metric:
    """Base metric class"""
    
    def __init__(self, name: str, metric_type: str, description: str = ""):
        self.name = name
        self.type = metric_type
        self.description = description
        self.values: Dict[str, Any] = {}
        self.labels: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.created_at = datetime.now()


class Counter(Metric):
    """Counter metric (can only increase)"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, MetricType.COUNTER, description)
        self.count = 0.0
    
    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment counter"""
        self.count += value
        
        if labels:
            label_key = self._make_label_key(labels)
            if label_key not in self.labels:
                self.labels[label_key] = 0.0
            self.labels[label_key] += value
    
    def _make_label_key(self, labels: Dict[str, str]) -> str:
        """Create label key"""
        return json.dumps(labels, sort_keys=True)
    
    def get(self) -> float:
        """Get current value"""
        return self.count


class Gauge(Metric):
    """Gauge metric (can go up or down)"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, MetricType.GAUGE, description)
        self.value = 0.0
    
    def set(self, value: float):
        """Set gauge value"""
        self.value = value
    
    def inc(self, value: float = 1.0):
        """Increment gauge"""
        self.value += value
    
    def dec(self, value: float = 1.0):
        """Decrement gauge"""
        self.value -= value
    
    def get(self) -> float:
        """Get current value"""
        return self.value


class Histogram(Metric):
    """Histogram metric (for distributions)"""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, MetricType.HISTOGRAM, description)
        self.observations: list = []
    
    def observe(self, value: float):
        """Record observation"""
        self.observations.append(value)
    
    def get_stats(self) -> Dict[str, float]:
        """Get histogram statistics"""
        if not self.observations:
            return {
                "count": 0,
                "sum": 0.0,
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0
            }
        
        return {
            "count": len(self.observations),
            "sum": sum(self.observations),
            "min": min(self.observations),
            "max": max(self.observations),
            "mean": sum(self.observations) / len(self.observations)
        }


class MetricsRegistry:
    """Registry for all metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        logger.info("Metrics Registry initialized")
    
    def counter(self, name: str, description: str = "") -> Counter:
        """Get or create counter"""
        if name not in self.metrics:
            self.metrics[name] = Counter(name, description)
        return self.metrics[name]
    
    def gauge(self, name: str, description: str = "") -> Gauge:
        """Get or create gauge"""
        if name not in self.metrics:
            self.metrics[name] = Gauge(name, description)
        return self.metrics[name]
    
    def histogram(self, name: str, description: str = "") -> Histogram:
        """Get or create histogram"""
        if name not in self.metrics:
            self.metrics[name] = Histogram(name, description)
        return self.metrics[name]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary"""
        result = {}
        
        for name, metric in self.metrics.items():
            if isinstance(metric, Counter):
                result[name] = {
                    "type": "counter",
                    "value": metric.get(),
                    "labels": dict(metric.labels)
                }
            elif isinstance(metric, Gauge):
                result[name] = {
                    "type": "gauge",
                    "value": metric.get()
                }
            elif isinstance(metric, Histogram):
                result[name] = {
                    "type": "histogram",
                    "stats": metric.get_stats()
                }
        
        return result
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for name, metric in self.metrics.items():
            # Help line
            if metric.description:
                lines.append(f"# HELP {name} {metric.description}")
            lines.append(f"# TYPE {name} {metric.type}")
            
            if isinstance(metric, Counter):
                lines.append(f"{name} {metric.get()}")
            elif isinstance(metric, Gauge):
                lines.append(f"{name} {metric.get()}")
            elif isinstance(metric, Histogram):
                stats = metric.get_stats()
                lines.append(f"{name}_count {stats['count']}")
                lines.append(f"{name}_sum {stats['sum']}")
            
            lines.append("")  # Empty line between metrics
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all metrics"""
        self.metrics.clear()


# Global registry
_registry = MetricsRegistry()


def get_registry() -> MetricsRegistry:
    """Get global metrics registry"""
    return _registry


def record_metric(
    name: str,
    value: float,
    labels: Optional[Dict[str, str]] = None,
    metric_type: str = "counter"
):
    """
    Convenience function to record a metric
    
    Args:
        name: Metric name
        value: Metric value
        labels: Optional labels
        metric_type: Type of metric (counter, gauge, histogram)
    """
    registry = get_registry()
    
    if metric_type == "counter":
        metric = registry.counter(name)
        metric.inc(value, labels)
    elif metric_type == "gauge":
        metric = registry.gauge(name)
        metric.set(value)
    elif metric_type == "histogram":
        metric = registry.histogram(name)
        metric.observe(value)


# Common metrics for agent system
def init_common_metrics():
    """Initialize common metrics"""
    registry = get_registry()
    
    # Agent metrics
    registry.counter("agent_operations_total", "Total agent operations")
    registry.counter("agent_errors_total", "Total agent errors")
    registry.histogram("agent_operation_duration_seconds", "Agent operation duration")
    
    # Paper metrics
    registry.counter("papers_retrieved_total", "Total papers retrieved")
    registry.counter("papers_summarized_total", "Total papers summarized")
    registry.histogram("paper_processing_time_seconds", "Paper processing time")
    
    # Session metrics
    registry.gauge("active_sessions", "Number of active sessions")
    registry.counter("sessions_created_total", "Total sessions created")
    
    # Memory metrics
    registry.gauge("memory_entries", "Number of memory entries")
    registry.gauge("memory_size_mb", "Memory size in MB")
    
    logger.info("Common metrics initialized")


# Initialize on import
init_common_metrics()

