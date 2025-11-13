"""
Simple test script to verify MCP server functionality without running the full server.
This directly tests the core calculation logic.
"""

from services.subnet_calc import calculate_subnet


def test_calculate_subnet_info():
    """Test subnet calculation"""
    print("Testing calculate_subnet...")

    # Test case 1: /24 network
    result = calculate_subnet("192.168.1.0/24")
    print(f"\nTest 1 - 192.168.1.0/24:")
    print(f"  Network: {result.get('network')}")
    print(f"  Broadcast: {result.get('broadcast')}")
    print(f"  Netmask: {result.get('netmask')}")
    print(f"  First host: {result.get('first_host')}")
    print(f"  Last host: {result.get('last_host')}")
    print(f"  Usable hosts: {result.get('usable_hosts')}")

    # Test case 2: /16 network
    result = calculate_subnet("10.0.0.0/16")
    print(f"\nTest 2 - 10.0.0.0/16:")
    print(f"  Usable hosts: {result.get('usable_hosts')}")

    # Test case 3: /8 network
    result = calculate_subnet("172.16.0.0/8")
    print(f"\nTest 3 - 172.16.0.0/8:")
    print(f"  Usable hosts: {result.get('usable_hosts')}")


def test_validate_cidr():
    """Test CIDR validation"""
    print("\n\nTesting CIDR validation...")

    # Valid CIDR
    result = calculate_subnet("192.168.1.0/24")
    is_valid = "error" not in result
    print(f"\nTest 1 - Valid CIDR '192.168.1.0/24':")
    print(f"  Valid: {is_valid}")
    print(f"  Result: {result if is_valid else result.get('error')}")

    # Invalid CIDR
    result = calculate_subnet("999.999.999.999/99")
    is_valid = "error" not in result
    print(f"\nTest 2 - Invalid CIDR '999.999.999.999/99':")
    print(f"  Valid: {is_valid}")
    print(f"  Error: {result.get('error')}")

    # Malformed input
    result = calculate_subnet("not-a-cidr")
    is_valid = "error" not in result
    print(f"\nTest 3 - Malformed input 'not-a-cidr':")
    print(f"  Valid: {is_valid}")
    print(f"  Error: {result.get('error')}")


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server Tool Tests")
    print("=" * 60)

    test_calculate_subnet_info()
    test_validate_cidr()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
