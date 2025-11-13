import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
base_url = "https://csp.infoblox.com/api/ddi/v1"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("Testing different operations...")
print("=" * 60)

# Test 1: List records (should work)
print("\n1. Testing GET /dns/record (list records)")
response = requests.get(f"{base_url}/dns/record?_limit=1", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ GET works")
else:
    print(f"   ❌ GET failed: {response.text[:100]}")

# Test 2: Get specific record
record_id = "dns/record/7736a138-fc77-4a18-b7ab-5b8248c80d6d"
print(f"\n2. Testing GET /{record_id}")
response = requests.get(f"{base_url}/{record_id}", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ GET specific record works")
    record = response.json()
    print(f"   Record: {record.get('result', {}).get('name_in_zone', 'N/A')}")
else:
    print(f"   ❌ Failed: {response.text[:100]}")

# Test 3: DELETE record
print(f"\n3. Testing DELETE /{record_id}")
response = requests.delete(f"{base_url}/{record_id}", headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ DELETE works!")
elif response.status_code == 501:
    print("   ❌ 501 Not Implemented")
elif response.status_code == 403:
    print("   ❌ 403 Forbidden - No delete permission")
elif response.status_code == 401:
    print("   ❌ 401 Unauthorized - Auth issue")
else:
    print(f"   ❌ Error {response.status_code}: {response.text[:200]}")

print("\n" + "=" * 60)
