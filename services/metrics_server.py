"""
Metrics and Health Check HTTP Server

Provides HTTP endpoints for monitoring:
- /metrics - Prometheus-compatible metrics endpoint
- /health - Health check endpoint with system status
- /metrics/json - Raw JSON metrics

Usage:
    python services/metrics_server.py

Then access:
    http://localhost:9090/metrics    (Prometheus format)
    http://localhost:9090/health     (Health check)
    http://localhost:9090/metrics/json (Raw JSON)
"""

import os
import sys
import time
from typing import Dict, Any
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import uvicorn
import structlog

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import metrics

# Initialize structured logger
logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Infoblox MCP Metrics Server",
    description="Prometheus metrics and health check endpoints",
    version="1.0.0"
)


@app.get("/metrics")
def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint

    Returns metrics in Prometheus text format that can be scraped by Prometheus.
    Configure Prometheus to scrape this endpoint.

    Example prometheus.yml:
        scrape_configs:
          - job_name: 'infoblox_mcp'
            scrape_interval: 15s
            static_configs:
              - targets: ['localhost:9090']
    """
    data = metrics.get_metrics()

    output = []

    # Server uptime
    output.append("# HELP mcp_uptime_seconds Server uptime in seconds")
    output.append("# TYPE mcp_uptime_seconds counter")
    output.append(f"mcp_uptime_seconds {data['uptime_seconds']}")
    output.append("")

    # API calls total
    output.append("# HELP mcp_api_calls_total Total number of API calls")
    output.append("# TYPE mcp_api_calls_total counter")
    output.append(f"mcp_api_calls_total {data['api_calls']['total']}")
    output.append("")

    # API calls by service and status
    output.append("# HELP mcp_api_calls_by_service_total API calls by service and status code")
    output.append("# TYPE mcp_api_calls_by_service_total counter")
    for service, service_data in data['api_calls']['by_service'].items():
        for status, count in service_data['by_status'].items():
            output.append(f'mcp_api_calls_by_service_total{{service="{service}",status_code="{status}"}} {count}')
    output.append("")

    # Cache metrics
    output.append("# HELP mcp_cache_hits_total Total cache hits")
    output.append("# TYPE mcp_cache_hits_total counter")
    output.append(f"mcp_cache_hits_total {data['cache']['total_hits']}")
    output.append("")

    output.append("# HELP mcp_cache_misses_total Total cache misses")
    output.append("# TYPE mcp_cache_misses_total counter")
    output.append(f"mcp_cache_misses_total {data['cache']['total_misses']}")
    output.append("")

    output.append("# HELP mcp_cache_hit_rate Cache hit rate percentage")
    output.append("# TYPE mcp_cache_hit_rate gauge")
    output.append(f"mcp_cache_hit_rate {data['cache']['hit_rate_percent']}")
    output.append("")

    # Cache hit rate by method
    output.append("# HELP mcp_cache_hit_rate_by_method Cache hit rate by method")
    output.append("# TYPE mcp_cache_hit_rate_by_method gauge")
    for method, method_data in data['cache']['by_method'].items():
        # Replace dots with underscores for Prometheus label compatibility
        safe_method = method.replace('.', '_')
        output.append(f'mcp_cache_hit_rate_by_method{{method="{safe_method}"}} {method_data["hit_rate_percent"]}')
    output.append("")

    # Latency metrics (p50, p95, p99)
    if data['latency']:
        output.append("# HELP mcp_latency_p50_ms 50th percentile latency in milliseconds")
        output.append("# TYPE mcp_latency_p50_ms gauge")
        for endpoint, stats in data['latency'].items():
            safe_endpoint = endpoint.replace('/', '_').replace('.', '_')
            output.append(f'mcp_latency_p50_ms{{endpoint="{safe_endpoint}"}} {stats["p50_ms"]}')
        output.append("")

        output.append("# HELP mcp_latency_p95_ms 95th percentile latency in milliseconds")
        output.append("# TYPE mcp_latency_p95_ms gauge")
        for endpoint, stats in data['latency'].items():
            safe_endpoint = endpoint.replace('/', '_').replace('.', '_')
            output.append(f'mcp_latency_p95_ms{{endpoint="{safe_endpoint}"}} {stats["p95_ms"]}')
        output.append("")

        output.append("# HELP mcp_latency_p99_ms 99th percentile latency in milliseconds")
        output.append("# TYPE mcp_latency_p99_ms gauge")
        for endpoint, stats in data['latency'].items():
            safe_endpoint = endpoint.replace('/', '_').replace('.', '_')
            output.append(f'mcp_latency_p99_ms{{endpoint="{safe_endpoint}"}} {stats["p99_ms"]}')
        output.append("")

        output.append("# HELP mcp_latency_avg_ms Average latency in milliseconds")
        output.append("# TYPE mcp_latency_avg_ms gauge")
        for endpoint, stats in data['latency'].items():
            safe_endpoint = endpoint.replace('/', '_').replace('.', '_')
            output.append(f'mcp_latency_avg_ms{{endpoint="{safe_endpoint}"}} {stats["avg_ms"]}')
        output.append("")

    # Circuit breaker state (0 = closed, 1 = open, 0.5 = half-open)
    if data['circuit_breakers']:
        output.append("# HELP mcp_circuit_breaker_state Circuit breaker state (0=closed, 0.5=half-open, 1=open)")
        output.append("# TYPE mcp_circuit_breaker_state gauge")
        for service, state_info in data['circuit_breakers'].items():
            state = state_info['state'].lower()
            state_value = 1 if 'open' in state else (0.5 if 'half' in state else 0)
            output.append(f'mcp_circuit_breaker_state{{service="{service}"}} {state_value}')
        output.append("")

    # Error metrics
    output.append("# HELP mcp_errors_total Total number of errors")
    output.append("# TYPE mcp_errors_total counter")
    output.append(f"mcp_errors_total {data['errors']['total']}")
    output.append("")

    # Errors by type
    if data['errors']['by_type']:
        output.append("# HELP mcp_errors_by_type_total Errors by type")
        output.append("# TYPE mcp_errors_by_type_total counter")
        for error_type, count in data['errors']['by_type'].items():
            safe_error = error_type.replace('/', '_').replace('.', '_')
            output.append(f'mcp_errors_by_type_total{{error_type="{safe_error}"}} {count}')
        output.append("")

    logger.debug("prometheus_metrics_scraped", metric_count=len(output))

    return Response(content='\n'.join(output), media_type='text/plain')


@app.get("/health")
def health_check():
    """
    Health check endpoint

    Returns:
        - status: "healthy" or "degraded" or "unhealthy"
        - uptime_seconds: Server uptime
        - circuit_breakers: State of all circuit breakers
        - errors: Recent error count
        - api_calls: Total API calls
        - cache_hit_rate: Cache effectiveness

    Use this for:
        - Load balancer health checks
        - Kubernetes liveness/readiness probes
        - Monitoring alerts

    Example Kubernetes probe:
        livenessProbe:
          httpGet:
            path: /health
            port: 9090
          initialDelaySeconds: 10
          periodSeconds: 5
    """
    data = metrics.get_metrics()

    # Determine overall health status
    status = "healthy"
    issues = []

    # Check circuit breakers
    for service, state_info in data['circuit_breakers'].items():
        if 'open' in state_info['state'].lower():
            status = "degraded"
            issues.append(f"Circuit breaker {service} is OPEN")

    # Check error rate (if > 10% of requests are errors, mark as degraded)
    if data['api_calls']['total'] > 0:
        error_rate = (data['errors']['total'] / data['api_calls']['total']) * 100
        if error_rate > 10:
            status = "degraded"
            issues.append(f"High error rate: {error_rate:.1f}%")
        elif error_rate > 50:
            status = "unhealthy"

    # Check cache hit rate (if < 30%, mark as degraded)
    if data['cache']['total_hits'] + data['cache']['total_misses'] > 10:
        if data['cache']['hit_rate_percent'] < 30:
            status = "degraded"
            issues.append(f"Low cache hit rate: {data['cache']['hit_rate_percent']:.1f}%")

    response = {
        "status": status,
        "timestamp": data['timestamp'],
        "uptime_seconds": data['uptime_seconds'],
        "issues": issues,
        "metrics": {
            "api_calls": data['api_calls']['total'],
            "error_rate_percent": round((data['errors']['total'] / data['api_calls']['total'] * 100) if data['api_calls']['total'] > 0 else 0, 2),
            "cache_hit_rate_percent": data['cache']['hit_rate_percent'],
            "circuit_breakers": {
                service: state_info['state']
                for service, state_info in data['circuit_breakers'].items()
            }
        }
    }

    # Return appropriate HTTP status code
    http_status = 200 if status == "healthy" else (503 if status == "unhealthy" else 200)

    logger.info("health_check_requested", status=status, issues=issues)

    return JSONResponse(content=response, status_code=http_status)


@app.get("/metrics/json")
def json_metrics():
    """
    Raw JSON metrics endpoint

    Returns the complete metrics data structure as JSON.
    Useful for custom dashboards, debugging, or non-Prometheus monitoring tools.
    """
    data = metrics.get_metrics()
    logger.debug("json_metrics_requested")
    return JSONResponse(content=data)


@app.get("/")
def root():
    """
    Root endpoint with API documentation
    """
    return {
        "service": "Infoblox MCP Metrics Server",
        "version": "1.0.0",
        "endpoints": {
            "/metrics": "Prometheus-compatible metrics (text format)",
            "/health": "Health check endpoint",
            "/metrics/json": "Raw JSON metrics",
            "/docs": "Interactive API documentation (Swagger UI)"
        },
        "uptime_seconds": metrics.get_metrics()['uptime_seconds']
    }


def main():
    """Start the metrics server"""
    port = int(os.getenv("METRICS_PORT", "9090"))
    host = os.getenv("METRICS_HOST", "0.0.0.0")

    logger.info(
        "metrics_server_starting",
        host=host,
        port=port,
        prometheus_endpoint=f"http://{host}:{port}/metrics",
        health_endpoint=f"http://{host}:{port}/health"
    )

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
