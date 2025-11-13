#!/usr/bin/env python3
"""
Test simplified MCP server with only configure_vpn_infrastructure tool
"""

import os
from dotenv import load_dotenv
from services.niosxaas_client import NIOSXaaSClient

load_dotenv()

print("="*70)
print("TESTING SIMPLIFIED MCP CONFIGURATION")
print("Testing configure_vpn_infrastructure via consolidated API")
print("="*70)

# Initialize client
client = NIOSXaaSClient()

# Simple VPN payload - just create the service and credential
vpn_payload = {
    "universal_service": {
        "operation": "CREATE",
        "name": "SimplifiedTest-VPN",
        "capabilities": [{"type": "dns"}],
        "tags": {"test": "simplified"}
    },
    "credentials": {
        "create": [{
            "id": "ref_cred_simple",
            "type": "psk",
            "name": "simple-psk",
            "value": "InfobloxLab.2025",
            "cred_data": {}
        }],
        "update": []
    },
    "endpoints": {"create": [], "update": [], "delete": []},
    "access_locations": {"create": [], "update": [], "delete": []},
    "locations": {"create": [], "update": []}
}

try:
    print("\n📋 Testing Consolidated Configure API")
    print("-" * 70)
    print("Payload:")
    import json
    print(json.dumps(vpn_payload, indent=2))

    print("\n🚀 Sending request...")
    result = client.consolidated_configure(vpn_payload)

    print("\n✅ SUCCESS! VPN Infrastructure Created")
    print(json.dumps(result, indent=2))

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
