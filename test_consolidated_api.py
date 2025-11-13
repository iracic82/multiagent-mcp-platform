#!/usr/bin/env python3
"""Test NIOSXaaS consolidated configure API with API key"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("INFOBLOX_API_KEY")
base_url = "https://csp.infoblox.com"

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}

print("Testing NIOSXaaS Consolidated Configure API with API Key...\n")

# Test: Create minimal VPN infrastructure with consolidated API
url = f"{base_url}/api/universalinfra/v1/consolidated/configure"

payload = {
    "universal_service": {
        "operation": "CREATE",
        "name": "Test-API-Key-VPN",
        "capabilities": [{"type": "dns"}],
        "tags": {"test": "api_key_auth"}
    },
    "credentials": {
        "create": [{
            "id": "ref_cred_test",
            "type": "psk",
            "name": "test-api-key-cred",
            "value": "InfobloxLab.2025",
            "cred_data": {}
        }],
        "update": []
    },
    "endpoints": {"create": [], "update": [], "delete": []},
    "access_locations": {"create": [], "update": [], "delete": []},
    "locations": {"create": [], "update": []}
}

print(f"Calling: {url}")
print(f"Payload: {payload}\n")

r = requests.post(url, headers=headers, json=payload)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:1000]}\n")

if r.status_code == 200 or r.status_code == 201:
    print("✅ SUCCESS! Consolidated API works with API key!")
    print("   Credentials can be created as part of consolidated configure!")
else:
    print(f"❌ Status {r.status_code}")
    if r.status_code == 501:
        print("   501 Not Implemented - API key auth not supported for this endpoint")
    elif r.status_code == 401:
        print("   401 Unauthorized - API key invalid")
    elif r.status_code == 409:
        print("   409 Conflict - Resource might already exist or operation in progress")
