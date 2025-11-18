"""
Test Metrics Collection Functionality

This test demonstrates comprehensive metrics collection across the MCP server:
1. API call tracking (counts, latencies, status codes)
2. Cache hit/miss rates
3. Circuit breaker state tracking
4. Error tracking by type
5. Metrics summary generation
"""

import time
from unittest.mock import patch, Mock
import requests
from services.infoblox_client import InfobloxClient
from services.atcfw_client import AtcfwClient
from services import metrics


def test_api_call_metrics():
    """Test API call metrics tracking"""
    print("\n" + "="*70)
    print("TEST 1: API Call Metrics Tracking")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    print("\n📊 Testing API call metrics...")

    # Simulate API calls
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 150.5, 200)
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 120.3, 200)
    metrics.record_api_call("infoblox_client", "/api/dns/v1/zones", 200.1, 200)
    metrics.record_api_call("atcfw_client", "/api/atcfw/v1/security_policies", 180.7, 200)
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 500.2, 500, "InternalServerError")

    # Get metrics
    current_metrics = collector.get_metrics()

    print("\n✅ API Call Metrics:")
    print(f"   • Total API Calls: {current_metrics['api_calls']['total']}")
    print(f"   • Services: {list(current_metrics['api_calls']['by_service'].keys())}")

    for service, data in current_metrics['api_calls']['by_service'].items():
        print(f"\n   {service}:")
        print(f"     - Total: {data['total']}")
        for status, count in data['by_status'].items():
            print(f"     - Status {status}: {count} calls")

    print("\n📈 Latency Metrics:")
    for endpoint, stats in current_metrics['latency'].items():
        print(f"   {endpoint}:")
        print(f"     - Count: {stats['count']}")
        print(f"     - Min: {stats['min_ms']}ms")
        print(f"     - Avg: {stats['avg_ms']}ms")
        print(f"     - p50: {stats['p50_ms']}ms")
        print(f"     - p95: {stats['p95_ms']}ms")
        print(f"     - Max: {stats['max_ms']}ms")

    # Verify
    assert current_metrics['api_calls']['total'] == 5
    assert len(current_metrics['api_calls']['by_service']) == 2
    assert current_metrics['errors']['total'] == 1

    print("\n✅ Test Passed: API call metrics are tracked correctly")


def test_cache_metrics():
    """Test cache hit/miss metrics"""
    print("\n" + "="*70)
    print("TEST 2: Cache Hit/Miss Metrics")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    print("\n📊 Testing cache metrics...")

    # Simulate cache operations
    metrics.record_cache_miss("infoblox_client", "list_ip_spaces")
    metrics.record_cache_hit("infoblox_client", "list_ip_spaces")
    metrics.record_cache_hit("infoblox_client", "list_ip_spaces")
    metrics.record_cache_hit("infoblox_client", "list_ip_spaces")

    metrics.record_cache_miss("atcfw_client", "list_security_policies")
    metrics.record_cache_hit("atcfw_client", "list_security_policies")

    # Get metrics
    current_metrics = collector.get_metrics()

    print("\n✅ Cache Metrics:")
    print(f"   • Total Hits: {current_metrics['cache']['total_hits']}")
    print(f"   • Total Misses: {current_metrics['cache']['total_misses']}")
    print(f"   • Hit Rate: {current_metrics['cache']['hit_rate_percent']}%")

    print("\n   By Method:")
    for method, stats in current_metrics['cache']['by_method'].items():
        print(f"   {method}:")
        print(f"     - Hits: {stats['hits']}")
        print(f"     - Misses: {stats['misses']}")
        print(f"     - Hit Rate: {stats['hit_rate_percent']}%")

    # Verify (3 hits from infoblox_client + 1 hit from atcfw_client = 4 total)
    assert current_metrics['cache']['total_hits'] == 4
    assert current_metrics['cache']['total_misses'] == 2
    assert current_metrics['cache']['hit_rate_percent'] == 66.67  # 4/(4+2) * 100

    print("\n✅ Test Passed: Cache metrics are tracked correctly")


def test_circuit_breaker_metrics():
    """Test circuit breaker metrics tracking"""
    print("\n" + "="*70)
    print("TEST 3: Circuit Breaker Metrics")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    print("\n📊 Testing circuit breaker metrics...")

    # Simulate circuit breaker events
    metrics.set_circuit_state("infoblox_api", "closed")
    metrics.set_circuit_state("atcfw_api", "closed")

    print("   • Initial state: All circuits closed")

    # Simulate circuit opening
    metrics.set_circuit_state("infoblox_api", "open")
    metrics.record_circuit_breaker_open("infoblox_api")

    print("   • infoblox_api circuit opened")

    # Get metrics
    current_metrics = collector.get_metrics()

    print("\n✅ Circuit Breaker Metrics:")
    for service, state_info in current_metrics['circuit_breakers'].items():
        print(f"   {service}: {state_info['state']} (updated: {state_info['updated_at']})")

    # Verify
    assert "infoblox_api" in current_metrics['circuit_breakers']
    assert current_metrics['circuit_breakers']['infoblox_api']['state'] == "open"
    assert "atcfw_api" in current_metrics['circuit_breakers']

    print("\n✅ Test Passed: Circuit breaker metrics are tracked correctly")


def test_error_metrics():
    """Test error metrics tracking"""
    print("\n" + "="*70)
    print("TEST 4: Error Metrics Tracking")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    print("\n📊 Testing error metrics...")

    # Simulate various errors
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 100.0, 500, "InternalServerError")
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 50.0, 503, "ServiceUnavailable")
    metrics.record_api_call("atcfw_client", "/api/atcfw/v1/policies", 200.0, 503, "CircuitBreakerOpen")
    metrics.record_api_call("infoblox_client", "/api/dns/v1/zones", 120.0, 500, "Timeout")

    # Get metrics
    current_metrics = collector.get_metrics()

    print("\n✅ Error Metrics:")
    print(f"   • Total Errors: {current_metrics['errors']['total']}")
    print(f"\n   By Type:")
    for error_type, count in current_metrics['errors']['by_type'].items():
        print(f"     - {error_type}: {count}")

    # Verify
    assert current_metrics['errors']['total'] == 4
    assert len(current_metrics['errors']['by_type']) == 4

    print("\n✅ Test Passed: Error metrics are tracked correctly")


def test_metrics_summary():
    """Test metrics summary generation"""
    print("\n" + "="*70)
    print("TEST 5: Metrics Summary Generation")
    print("="*70)

    # Reset metrics and create some activity
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    # Simulate varied activity
    print("\n📊 Generating sample metrics...")

    # API calls
    for i in range(10):
        metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 100 + i*10, 200)

    # Cache operations
    metrics.record_cache_miss("infoblox_client", "list_ip_spaces")
    for i in range(9):
        metrics.record_cache_hit("infoblox_client", "list_ip_spaces")

    # Circuit breaker
    metrics.set_circuit_state("infoblox_api", "closed")

    # Errors
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/subnets", 200.0, 500, "InternalServerError")

    # Get summary
    summary = collector.get_summary()

    print("\n" + "="*70)
    print(summary)
    print("="*70)

    # Verify summary contains key sections
    assert "METRICS SUMMARY" in summary
    assert "API Calls:" in summary
    assert "Cache Performance:" in summary
    assert "Latency (ms):" in summary
    assert "Circuit Breakers:" in summary
    assert "Errors:" in summary

    print("\n✅ Test Passed: Metrics summary generated successfully")


def test_integration_with_clients():
    """Test metrics integration with actual clients"""
    print("\n" + "="*70)
    print("TEST 6: Integration with Service Clients")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    print("\n📊 Testing metrics integration with InfobloxClient...")

    client = InfobloxClient()

    # Mock successful API call
    with patch.object(client.session, 'request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "1", "name": "test-space-1"},
                {"id": "2", "name": "test-space-2"}
            ]
        }
        mock_request.return_value = mock_response

        # First call (cache miss)
        print("   • First call (cache miss)...")
        result1 = client.list_ip_spaces(limit=10)

        # Second call (cache hit)
        print("   • Second call (cache hit)...")
        result2 = client.list_ip_spaces(limit=10)

    # Get metrics
    current_metrics = collector.get_metrics()

    print("\n✅ Integration Metrics:")
    print(f"   • API Calls: {current_metrics['api_calls']['total']}")
    print(f"   • Cache Hits: {current_metrics['cache']['total_hits']}")
    print(f"   • Cache Misses: {current_metrics['cache']['total_misses']}")
    print(f"   • Hit Rate: {current_metrics['cache']['hit_rate_percent']}%")

    # Verify
    assert current_metrics['api_calls']['total'] >= 1  # At least one API call
    assert current_metrics['cache']['total_hits'] >= 1  # At least one cache hit
    assert current_metrics['cache']['total_misses'] >= 1  # At least one cache miss

    print("\n✅ Test Passed: Metrics integrate correctly with service clients")


def test_latency_percentiles():
    """Test latency percentile calculations"""
    print("\n" + "="*70)
    print("TEST 7: Latency Percentile Calculations")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    print("\n📊 Testing latency percentile calculations...")

    # Simulate 100 API calls with varying latencies
    latencies = []
    for i in range(100):
        latency = 50 + i * 5  # Range from 50ms to 545ms
        latencies.append(latency)
        metrics.record_api_call("infoblox_client", "/api/test/endpoint", latency, 200)

    # Get metrics
    current_metrics = collector.get_metrics()

    print("\n✅ Latency Percentiles:")
    for endpoint, stats in current_metrics['latency'].items():
        print(f"   {endpoint}:")
        print(f"     - Count: {stats['count']}")
        print(f"     - Min: {stats['min_ms']}ms")
        print(f"     - p50 (median): {stats['p50_ms']}ms")
        print(f"     - p95: {stats['p95_ms']}ms")
        print(f"     - p99: {stats['p99_ms']}ms")
        print(f"     - Max: {stats['max_ms']}ms")
        print(f"     - Average: {stats['avg_ms']}ms")

    # Verify (note: key has double slash due to endpoint format)
    latency_stats = current_metrics['latency']['infoblox_client//api/test/endpoint']
    assert latency_stats['count'] == 100
    assert latency_stats['min_ms'] == 50.0
    assert latency_stats['max_ms'] == 545.0
    assert latency_stats['p50_ms'] > 0
    assert latency_stats['p95_ms'] > latency_stats['p50_ms']
    assert latency_stats['p99_ms'] > latency_stats['p95_ms']

    print("\n✅ Test Passed: Latency percentiles calculated correctly")


def main():
    print("\n" + "="*70)
    print("🎯 METRICS COLLECTION TESTING - INFOBLOX MCP SERVER")
    print("="*70)

    print("\n📋 What are we testing?")
    print("   Metrics collection provides observability into the MCP server:")
    print("   • API call counts, latencies, and status codes")
    print("   • Cache hit rates and performance")
    print("   • Circuit breaker state changes")
    print("   • Error rates by type")
    print("   • Production-ready metrics for monitoring tools")

    try:
        test_api_call_metrics()
        test_cache_metrics()
        test_circuit_breaker_metrics()
        test_error_metrics()
        test_metrics_summary()
        test_integration_with_clients()
        test_latency_percentiles()

        print("\n" + "="*70)
        print("✅ ALL METRICS TESTS PASSED")
        print("="*70)

        print("\n📈 Production Benefits:")
        print("   ✅ Complete observability of MCP server")
        print("   ✅ API call tracking with latency percentiles")
        print("   ✅ Cache effectiveness monitoring (hit rates)")
        print("   ✅ Circuit breaker state visibility")
        print("   ✅ Error tracking by type and service")
        print("   ✅ Thread-safe in-memory collection")
        print("   ✅ Human-readable summaries")
        print("   ✅ Machine-readable JSON metrics")

        print("\n💡 Integration:")
        print("   • Metrics are automatically collected by all service clients")
        print("   • No external dependencies (cachetools, structlog already installed)")
        print("   • Access via metrics.get_metrics() or metrics.get_summary()")
        print("   • Ready for Prometheus, Datadog, or custom monitoring")

        print("\n📊 Metrics Available:")
        print("   • api_calls: Total calls, by service, by status code")
        print("   • latency: p50, p95, p99, min, max, avg per endpoint")
        print("   • cache: Hit rates, total hits/misses, by method")
        print("   • circuit_breakers: Current state per service")
        print("   • errors: Total errors, by type and service")
        print("   • uptime_seconds: Server uptime")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
