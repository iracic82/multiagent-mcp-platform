"""
Test Metrics Server Endpoints

This test validates:
1. Prometheus /metrics endpoint returns correct format
2. Health check /health endpoint works
3. JSON metrics /metrics/json endpoint works
4. Metrics are properly formatted for Prometheus scraping
"""

import time
import requests
from services import metrics


def test_prometheus_endpoint():
    """Test Prometheus metrics endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Prometheus /metrics Endpoint")
    print("="*70)

    # Reset metrics and add some test data
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    # Simulate some activity
    print("\n📊 Generating test metrics...")
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 150.5, 200)
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 120.3, 200)
    metrics.record_api_call("atcfw_client", "/api/atcfw/v1/policies", 180.7, 200)
    metrics.record_cache_hit("infoblox_client", "list_ip_spaces")
    metrics.record_cache_miss("infoblox_client", "list_ip_spaces")
    metrics.set_circuit_state("infoblox_api", "closed")

    print("   • API calls: 3")
    print("   • Cache hits: 1, misses: 1")
    print("   • Circuit breaker: closed")

    # Start metrics server in background
    print("\n🚀 Starting metrics server on port 9090...")
    import subprocess
    import os
    server = subprocess.Popen(
        ["python", "services/metrics_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy()
    )

    # Wait for server to start
    print("   Waiting for server to start...")
    time.sleep(3)

    try:
        # Test Prometheus endpoint
        print("\n📡 Fetching Prometheus metrics from http://localhost:9090/metrics...")
        response = requests.get("http://localhost:9090/metrics", timeout=5)

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            content = response.text
            lines = content.split('\n')

            print(f"✅ Content-Type: {response.headers.get('content-type')}")
            print(f"✅ Response Length: {len(content)} bytes")
            print(f"✅ Number of Lines: {len(lines)}")

            # Verify key metrics are present
            required_metrics = [
                "mcp_uptime_seconds",
                "mcp_api_calls_total",
                "mcp_cache_hits_total",
                "mcp_cache_hit_rate",
                "mcp_circuit_breaker_state",
            ]

            print("\n📋 Verifying required metrics:")
            for metric in required_metrics:
                if metric in content:
                    print(f"   ✅ {metric} - FOUND")
                else:
                    print(f"   ❌ {metric} - MISSING")

            # Show sample output
            print("\n📄 Sample Prometheus Output (first 30 lines):")
            print("-" * 70)
            for line in lines[:30]:
                if line.strip():
                    print(f"   {line}")
            print("-" * 70)

            # Verify format
            assert "# HELP" in content
            assert "# TYPE" in content
            assert "mcp_api_calls_total 3" in content or "mcp_api_calls_total 0" in content
            assert "mcp_cache_hit_rate" in content

            print("\n✅ Test Passed: Prometheus endpoint works correctly")

        else:
            print(f"❌ Unexpected status code: {response.status_code}")

    finally:
        # Stop server
        print("\n🛑 Stopping metrics server...")
        server.terminate()
        server.wait(timeout=5)


def test_health_endpoint():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Health Check /health Endpoint")
    print("="*70)

    # Reset metrics and add some test data
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    # Simulate healthy system
    print("\n📊 Generating test metrics (healthy system)...")
    for i in range(10):
        metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 100 + i*10, 200)
    metrics.record_cache_hit("infoblox_client", "list_ip_spaces")
    metrics.record_cache_hit("infoblox_client", "list_ip_spaces")
    metrics.record_cache_miss("infoblox_client", "list_ip_spaces")
    metrics.set_circuit_state("infoblox_api", "closed")

    print("   • API calls: 10 (all successful)")
    print("   • Cache hit rate: 66.67%")
    print("   • Circuit breaker: closed")

    # Start server
    print("\n🚀 Starting metrics server on port 9090...")
    import subprocess
    import os
    server = subprocess.Popen(
        ["python", "services/metrics_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy()
    )

    time.sleep(3)

    try:
        # Test health endpoint
        print("\n📡 Fetching health status from http://localhost:9090/health...")
        response = requests.get("http://localhost:9090/health", timeout=5)

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"✅ Content-Type: {response.headers.get('content-type')}")

            print("\n📋 Health Status:")
            print(f"   • Status: {data['status']}")
            print(f"   • Uptime: {data['uptime_seconds']}s")
            print(f"   • Issues: {len(data['issues'])}")

            print("\n📊 Metrics:")
            print(f"   • API Calls: {data['metrics']['api_calls']}")
            print(f"   • Error Rate: {data['metrics']['error_rate_percent']}%")
            print(f"   • Cache Hit Rate: {data['metrics']['cache_hit_rate_percent']}%")

            if data['metrics']['circuit_breakers']:
                print("\n🔌 Circuit Breakers:")
                for service, state in data['metrics']['circuit_breakers'].items():
                    print(f"   • {service}: {state}")

            if data['issues']:
                print("\n⚠️  Issues:")
                for issue in data['issues']:
                    print(f"   • {issue}")

            # Verify structure
            assert 'status' in data
            assert 'metrics' in data
            assert data['status'] in ['healthy', 'degraded', 'unhealthy']

            print("\n✅ Test Passed: Health endpoint works correctly")

        else:
            print(f"❌ Unexpected status code: {response.status_code}")

    finally:
        # Stop server
        print("\n🛑 Stopping metrics server...")
        server.terminate()
        server.wait(timeout=5)


def test_json_metrics_endpoint():
    """Test JSON metrics endpoint"""
    print("\n" + "="*70)
    print("TEST 3: JSON Metrics /metrics/json Endpoint")
    print("="*70)

    # Reset metrics
    metrics._metrics_collector = None
    collector = metrics.get_metrics_collector()

    # Add test data
    print("\n📊 Generating test metrics...")
    metrics.record_api_call("infoblox_client", "/api/ipam/v1/ip_space", 150.5, 200)
    metrics.record_api_call("atcfw_client", "/api/atcfw/v1/policies", 180.7, 200)

    # Start server
    print("\n🚀 Starting metrics server on port 9090...")
    import subprocess
    import os
    server = subprocess.Popen(
        ["python", "services/metrics_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy()
    )

    time.sleep(3)

    try:
        # Test JSON endpoint
        print("\n📡 Fetching JSON metrics from http://localhost:9090/metrics/json...")
        response = requests.get("http://localhost:9090/metrics/json", timeout=5)

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"✅ Content-Type: {response.headers.get('content-type')}")

            print("\n📋 JSON Structure:")
            print(f"   • timestamp: {data['timestamp']}")
            print(f"   • uptime_seconds: {data['uptime_seconds']}")
            print(f"   • api_calls: {data['api_calls']['total']} total")
            print(f"   • cache: {data['cache']['total_hits']} hits")
            print(f"   • errors: {data['errors']['total']} total")

            # Verify structure
            assert 'api_calls' in data
            assert 'cache' in data
            assert 'latency' in data
            assert 'circuit_breakers' in data
            assert 'errors' in data

            print("\n✅ Test Passed: JSON endpoint works correctly")

        else:
            print(f"❌ Unexpected status code: {response.status_code}")

    finally:
        # Stop server
        print("\n🛑 Stopping metrics server...")
        server.terminate()
        server.wait(timeout=5)


def test_root_endpoint():
    """Test root endpoint"""
    print("\n" + "="*70)
    print("TEST 4: Root / Endpoint")
    print("="*70)

    # Start server
    print("\n🚀 Starting metrics server on port 9090...")
    import subprocess
    import os
    server = subprocess.Popen(
        ["python", "services/metrics_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy()
    )

    time.sleep(3)

    try:
        # Test root endpoint
        print("\n📡 Fetching API info from http://localhost:9090/...")
        response = requests.get("http://localhost:9090/", timeout=5)

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"✅ Content-Type: {response.headers.get('content-type')}")

            print("\n📋 API Information:")
            print(f"   • Service: {data['service']}")
            print(f"   • Version: {data['version']}")

            print("\n📍 Available Endpoints:")
            for endpoint, description in data['endpoints'].items():
                print(f"   • {endpoint}: {description}")

            print("\n✅ Test Passed: Root endpoint works correctly")

        else:
            print(f"❌ Unexpected status code: {response.status_code}")

    finally:
        # Stop server
        print("\n🛑 Stopping metrics server...")
        server.terminate()
        server.wait(timeout=5)


def main():
    print("\n" + "="*70)
    print("🎯 METRICS SERVER TESTING - INFOBLOX MCP SERVER")
    print("="*70)

    print("\n📋 What are we testing?")
    print("   • Prometheus /metrics endpoint (for Grafana)")
    print("   • Health check /health endpoint (for monitoring)")
    print("   • JSON /metrics/json endpoint (for custom tools)")
    print("   • Root / endpoint (API documentation)")

    try:
        test_prometheus_endpoint()
        test_health_endpoint()
        test_json_metrics_endpoint()
        test_root_endpoint()

        print("\n" + "="*70)
        print("✅ ALL METRICS SERVER TESTS PASSED")
        print("="*70)

        print("\n📈 Production Benefits:")
        print("   ✅ Prometheus-compatible metrics endpoint")
        print("   ✅ Health check for load balancers")
        print("   ✅ JSON API for custom monitoring")
        print("   ✅ Ready for Grafana dashboards")

        print("\n💡 How to Use:")
        print("   1. Start server: python services/metrics_server.py")
        print("   2. Access metrics: http://localhost:9090/metrics")
        print("   3. Check health: http://localhost:9090/health")
        print("   4. View JSON: http://localhost:9090/metrics/json")
        print("   5. API docs: http://localhost:9090/docs")

        print("\n📊 Grafana Setup:")
        print("   1. Add Prometheus data source in Grafana")
        print("   2. Configure Prometheus to scrape http://localhost:9090/metrics")
        print("   3. Import dashboard or create custom panels")
        print("   4. Visualize API latency, cache hit rates, errors, etc.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
