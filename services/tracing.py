"""
Distributed Tracing with OpenTelemetry

Provides end-to-end request tracing across all Infoblox API calls.
Traces are exported to Jaeger for visualization.

Usage:
    from services import tracing

    # Initialize tracing (call once at startup)
    tracing.initialize_tracing(service_name="infoblox_mcp")

    # Tracing is automatic for all API calls via instrumentation

    # Or manually create spans:
    with tracing.start_span("custom_operation") as span:
        span.set_attribute("key", "value")
        # ... your code ...
"""

import os
from typing import Optional
from contextlib import contextmanager
import structlog

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize structured logger
logger = structlog.get_logger(__name__)

# Global tracer
_tracer: Optional[trace.Tracer] = None
_initialized = False


def initialize_tracing(
    service_name: str = "infoblox_mcp_server",
    jaeger_host: str = None,
    jaeger_port: int = None,
    enabled: bool = None
):
    """
    Initialize OpenTelemetry distributed tracing

    Args:
        service_name: Name of this service in traces
        jaeger_host: Jaeger agent host (default: localhost or JAEGER_HOST env)
        jaeger_port: Jaeger agent port (default: 6831 or JAEGER_PORT env)
        enabled: Enable/disable tracing (default: True or TRACING_ENABLED env)
    """
    global _tracer, _initialized

    if _initialized:
        logger.warning("tracing_already_initialized")
        return

    # Check if tracing is enabled
    if enabled is None:
        enabled = os.getenv("TRACING_ENABLED", "true").lower() == "true"

    if not enabled:
        logger.info("tracing_disabled")
        _initialized = True
        return

    # Get Jaeger configuration
    jaeger_host = jaeger_host or os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = jaeger_port or int(os.getenv("JAEGER_PORT", "6831"))

    try:
        # Create resource with service name
        resource = Resource(attributes={
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development")
        })

        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Create Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )

        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        # Get tracer
        _tracer = trace.get_tracer(__name__)

        # Instrument requests library (auto-traces all HTTP calls)
        RequestsInstrumentor().instrument()

        _initialized = True

        logger.info(
            "tracing_initialized",
            service_name=service_name,
            jaeger_host=jaeger_host,
            jaeger_port=jaeger_port
        )

    except Exception as e:
        logger.error(
            "tracing_initialization_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        # Don't fail application if tracing fails
        _initialized = True


@contextmanager
def start_span(
    name: str,
    attributes: Optional[dict] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL
):
    """
    Create a new span for tracing

    Usage:
        with start_span("process_request", attributes={"user_id": "123"}):
            # ... your code ...

    Args:
        name: Span name
        attributes: Optional attributes to add to span
        kind: Span kind (INTERNAL, CLIENT, SERVER, PRODUCER, CONSUMER)

    Yields:
        Span object
    """
    if not _tracer:
        # Tracing not initialized, use no-op span
        yield trace.get_current_span()
        return

    with _tracer.start_as_current_span(name, kind=kind) as span:
        # Add attributes
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

        try:
            yield span
        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise


def get_tracer() -> Optional[trace.Tracer]:
    """Get the global tracer"""
    return _tracer


def is_initialized() -> bool:
    """Check if tracing is initialized"""
    return _initialized


def add_span_attribute(key: str, value: any):
    """
    Add attribute to current span

    Args:
        key: Attribute key
        value: Attribute value
    """
    span = trace.get_current_span()
    if span.is_recording():
        span.set_attribute(key, str(value))


def add_span_event(name: str, attributes: Optional[dict] = None):
    """
    Add event to current span

    Args:
        name: Event name
        attributes: Optional event attributes
    """
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(name, attributes=attributes or {})


# Convenience function for common operations
def trace_api_call(service: str, endpoint: str, method: str = "GET"):
    """
    Decorator for tracing API calls

    Usage:
        @trace_api_call("infoblox_client", "/api/ipam/v1/ip_space")
        def list_ip_spaces(self):
            # ... your code ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with start_span(
                f"{service}.{func.__name__}",
                attributes={
                    "service": service,
                    "endpoint": endpoint,
                    "method": method,
                    "function": func.__name__
                },
                kind=trace.SpanKind.CLIENT
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator
