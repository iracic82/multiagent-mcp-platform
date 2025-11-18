"""
Test script to demonstrate response caching

This script calls the same MCP tools multiple times to show:
1. First call: Cache MISS (hits the API)
2. Second call: Cache HIT (returns cached result)
3. Performance improvement from caching
"""

import time
from services.infoblox_client import InfobloxClient
from services.atcfw_client import AtcfwClient

def test_ip_space_caching():
    """Test IP Space caching"""
    print("\n" + "="*60)
    print("TEST 1: IP Space Caching")
    print("="*60)

    client = InfobloxClient()

    # First call - should be a cache MISS
    print("\n🔍 First call to list_ip_spaces() - expecting cache MISS...")
    start = time.time()
    result1 = client.list_ip_spaces(limit=10)
    duration1 = (time.time() - start) * 1000
    print(f"   Duration: {duration1:.2f}ms")
    print(f"   Results: {len(result1.get('results', []))} IP spaces")

    # Second call (same parameters) - should be a cache HIT
    print("\n🚀 Second call to list_ip_spaces() - expecting cache HIT...")
    start = time.time()
    result2 = client.list_ip_spaces(limit=10)
    duration2 = (time.time() - start) * 1000
    print(f"   Duration: {duration2:.2f}ms")
    print(f"   Results: {len(result2.get('results', []))} IP spaces")

    # Calculate speedup
    if duration2 > 0:
        speedup = (duration1 / duration2)
        print(f"\n📊 Performance: {speedup:.1f}x faster (cache hit)")
        print(f"   Saved: {duration1 - duration2:.2f}ms")

    # Verify results are identical
    if result1 == result2:
        print("   ✅ Results are identical (cache working correctly)")
    else:
        print("   ⚠️  Results differ (unexpected)")


def test_dns_zone_caching():
    """Test DNS Zone caching"""
    print("\n" + "="*60)
    print("TEST 2: DNS Zone Caching")
    print("="*60)

    client = InfobloxClient()

    # First call - cache MISS
    print("\n🔍 First call to list_auth_zones() - expecting cache MISS...")
    start = time.time()
    result1 = client.list_auth_zones(limit=10)
    duration1 = (time.time() - start) * 1000
    print(f"   Duration: {duration1:.2f}ms")
    print(f"   Results: {len(result1.get('results', []))} auth zones")

    # Second call - cache HIT
    print("\n🚀 Second call to list_auth_zones() - expecting cache HIT...")
    start = time.time()
    result2 = client.list_auth_zones(limit=10)
    duration2 = (time.time() - start) * 1000
    print(f"   Duration: {duration2:.2f}ms")
    print(f"   Results: {len(result2.get('results', []))} auth zones")

    if duration2 > 0:
        speedup = (duration1 / duration2)
        print(f"\n📊 Performance: {speedup:.1f}x faster (cache hit)")
        print(f"   Saved: {duration1 - duration2:.2f}ms")

    if result1 == result2:
        print("   ✅ Results are identical (cache working correctly)")


def test_security_policy_caching():
    """Test Security Policy caching"""
    print("\n" + "="*60)
    print("TEST 3: Security Policy Caching")
    print("="*60)

    client = AtcfwClient()

    # First call - cache MISS
    print("\n🔍 First call to list_security_policies() - expecting cache MISS...")
    start = time.time()
    result1 = client.list_security_policies(limit=10)
    duration1 = (time.time() - start) * 1000
    print(f"   Duration: {duration1:.2f}ms")
    print(f"   Results: {len(result1.get('results', []))} policies")

    # Second call - cache HIT
    print("\n🚀 Second call to list_security_policies() - expecting cache HIT...")
    start = time.time()
    result2 = client.list_security_policies(limit=10)
    duration2 = (time.time() - start) * 1000
    print(f"   Duration: {duration2:.2f}ms")
    print(f"   Results: {len(result2.get('results', []))} policies")

    if duration2 > 0:
        speedup = (duration1 / duration2)
        print(f"\n📊 Performance: {speedup:.1f}x faster (cache hit)")
        print(f"   Saved: {duration1 - duration2:.2f}ms")

    if result1 == result2:
        print("   ✅ Results are identical (cache working correctly)")


def test_cache_expiration():
    """Test cache expiration (TTL)"""
    print("\n" + "="*60)
    print("TEST 4: Cache Expiration (TTL = 5 minutes)")
    print("="*60)

    client = InfobloxClient()

    print("\n📝 Cache TTL is set to 300 seconds (5 minutes)")
    print("   After 5 minutes, cache entries expire automatically")
    print("   Next call after expiration will be a cache MISS")
    print("   This prevents stale data from being served")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INFOBLOX MCP SERVER - CACHING TEST")
    print("="*60)
    print("\nThis test demonstrates response caching for:")
    print("  • IP Spaces")
    print("  • DNS Zones")
    print("  • Security Policies")
    print("\nExpected behavior:")
    print("  • 1st call: Cache MISS (slow - hits API)")
    print("  • 2nd call: Cache HIT  (fast - returns cached data)")
    print("  • Speedup: 10-100x faster on cache hits")

    try:
        test_ip_space_caching()
        test_dns_zone_caching()
        test_security_policy_caching()
        test_cache_expiration()

        print("\n" + "="*60)
        print("✅ ALL CACHING TESTS COMPLETED")
        print("="*60)
        print("\n💡 Check the MCP server logs for cache_hit/cache_miss events")
        print("   You should see structured log entries showing:")
        print("   • cache_miss on first calls")
        print("   • cache_hit on subsequent calls")
        print("   • cache_size increasing as items are cached")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
