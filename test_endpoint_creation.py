#!/usr/bin/env python3
"""
Test endpoint creation with consolidated configure API to see actual error
"""

import os
from dotenv import load_dotenv
from services.niosxaas_client import NIOSXaaSClient
import json

load_dotenv()

print("="*70)
print("TESTING ENDPOINT CREATION WITH CONSOLIDATED CONFIGURE")
print("="*70)

# Initialize client
client = NIOSXaaSClient()

# First, let's get the service ID that was just created
service_name = "Test-VPN-123"

print(f"\n1. Looking for service: {service_name}")
services = client.list_universal_services()
matching_services = [s for s in services.get('results', []) if service_name in s.get('name', '')]

if not matching_services:
    print(f"❌ Service '{service_name}' not found. Please create it first.")
    exit(1)

service = matching_services[0]
service_id = service['id']
print(f"✅ Found service ID: {service_id}")

# Get the credential ID
creds = client.list_credentials(name_filter="test-vpn-123-psk")
if not creds.get('results'):
    print("❌ No credentials found")
    exit(1)

credential_id = creds['results'][0]['id']
print(f"✅ Found credential ID: {credential_id}")

# Now try to add an endpoint using UPDATE operation
print("\n2. Testing endpoint creation with UPDATE operation...")

payload = {
    "universal_service": {
        "operation": "UPDATE",
        "id": service_id,
        "name": service_name
    },
    "credentials": {
        "create": [],
        "update": []
    },
    "endpoints": {
        "create": [{
            "name": "Test-VPN-123-Endpoint",
            "service_location": "AWS Europe (Frankfurt)",
            "service_ip": "10.10.10.3",
            "universal_service_id": service_id,
            "size": "S",
            "neighbour_ips": ["10.10.10.4"],
            "routing_type": "dynamic",
            "routing_config": {
                "bgp_config": {
                    "asn": "65500",
                    "hold_down": 90
                }
            },
            "preferred_provider": "AWS"
        }],
        "update": [],
        "delete": []
    },
    "access_locations": {
        "create": [],
        "update": [],
        "delete": []
    },
    "locations": {
        "create": [],
        "update": []
    }
}

print("\nPayload:")
print(json.dumps(payload, indent=2))

try:
    print("\n3. Sending request to consolidated configure API...")
    result = client.consolidated_configure(payload)
    print("\n✅ SUCCESS!")
    print(json.dumps(result, indent=2))

except Exception as e:
    print(f"\n❌ FAILED: {e}")
    print("\nError details:")
    if hasattr(e, 'response'):
        print(f"Status code: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
    import traceback
    traceback.print_exc()
