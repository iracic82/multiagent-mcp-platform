#!/usr/bin/env python3
"""Test NIOSXaaS credentials API with API key"""

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

print("Testing NIOSXaaS Credentials API with API Key...\n")

# Test 1: List credentials
print("1. Testing LIST credentials endpoint...")
url = f"{base_url}/api/universalinfra/v1/credentials"
r = requests.get(url, headers=headers)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:200]}\n")

# Test 2: Create credential
print("2. Testing CREATE credential endpoint...")
url = f"{base_url}/api/universalinfra/v1/credentials"
payload = {
    "name": "test-api-key-psk",
    "type": "psk",
    "value": "InfobloxLab.2025",
    "tags": {}
}
r = requests.post(url, headers=headers, json=payload)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:500]}\n")

if r.status_code == 200 or r.status_code == 201:
    print("✅ SUCCESS! API key works with credentials endpoint!")
    result = r.json()
    cred_id = result.get("result", {}).get("id") or result.get("id")
    if cred_id:
        print(f"   Credential ID: {cred_id}")

        # Test 3: Delete the test credential
        print("\n3. Cleaning up - deleting test credential...")
        url = f"{base_url}/api/universalinfra/v1/credentials/{cred_id}"
        r = requests.delete(url, headers=headers)
        print(f"   Delete Status: {r.status_code}")
else:
    print(f"❌ FAILED with status {r.status_code}")
    print(f"   Error: {r.text}")
