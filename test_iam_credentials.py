#!/usr/bin/env python3
"""Test IAM API credentials endpoints with API key"""

import os
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("INFOBLOX_API_KEY")
base_url = "https://csp.infoblox.com"

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}

print("Testing IAM API Credentials Endpoints with API Key...\n")

# Test 1: List credentials via IAM API
print("1. Testing LIST credentials via /api/iam/v2/keys...")
url = f"{base_url}/api/iam/v2/keys"
r = requests.get(url, headers=headers)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:500]}\n")

if r.status_code == 200:
    print("✅ IAM API LIST works with API key!")
else:
    print(f"❌ IAM API LIST failed with status {r.status_code}\n")

# Test 2: Create credential via IAM API
print("2. Testing CREATE credential via /api/iam/v2/keys...")
url = f"{base_url}/api/iam/v2/keys"
unique_name = f"test-iam-api-psk-{uuid.uuid4().hex[:6]}"
payload = {
    "name": unique_name,
    "source_id": "psk",
    "key_type": "psk",
    "key_data": {
        "psk": "InfobloxLab.2025"
    }
}
print(f"   Creating credential: {unique_name}")
r = requests.post(url, headers=headers, json=payload)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:500]}\n")

if r.status_code in (200, 201):
    print("✅ IAM API CREATE works with API key!")
    result = r.json()
    cred_id = result.get("results", {}).get("id") or result.get("id")

    if cred_id:
        print(f"   Credential ID: {cred_id}")

        # Test 3: Get credential via IAM API
        print("\n3. Testing GET credential via /api/iam/v2/keys/{id}...")
        url = f"{base_url}/api/iam/v2/keys/{cred_id}"
        r = requests.get(url, headers=headers)
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text[:500]}\n")

        # Test 4: Delete credential via IAM API
        print("4. Cleaning up - deleting test credential via /api/iam/v2/keys/{id}...")
        url = f"{base_url}/api/iam/v2/keys/{cred_id}"
        r = requests.delete(url, headers=headers)
        print(f"   Delete Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ IAM API DELETE works with API key!")
else:
    print(f"❌ IAM API CREATE failed with status {r.status_code}")
    print(f"   Error: {r.text}")

print("\n" + "="*60)
print("COMPARISON: UniversalInfra API vs IAM API")
print("="*60)
print("UniversalInfra API: /api/universalinfra/v1/credentials")
print("  - Returns: 501 Not Implemented with Token auth")
print("\nIAM API: /api/iam/v2/keys")
print("  - Testing results above...")
