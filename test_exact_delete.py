import os
import requests
from services.infoblox_client import InfobloxClient

# The exact record ID from your screenshot
record_id = "dns/record/b907f303-7a3f-4ccd-a397-2de93ed919a8"

print("Testing DELETE on app99 record...")
print("=" * 70)

# Method 1: Using InfobloxClient (what failed in the agent)
print("\n1️⃣  Using InfobloxClient (agent's method):")
client = InfobloxClient()
print(f"   Session headers: {dict(client.session.headers)}")

try:
    result = client.delete_dns_record(record_id)
    print(f"   ✅ SUCCESS: {result}")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    error_str = str(e)
    if "501" in error_str:
        print("   🚨 Got HTTP 501 - Same error as agent!")
    elif "404" in error_str or "not found" in error_str.lower():
        print("   ℹ️  Record already deleted by UI")

# Method 2: Direct API call (simulating what UI does)
print("\n2️⃣  Direct API call (UI method):")
api_key = os.getenv('INFOBLOX_API_KEY')
headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
url = f"https://csp.infoblox.com/api/ddi/v1/{record_id}"
print(f"   URL: {url}")
print(f"   Headers: {headers}")

response = requests.delete(url, headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text}")

if response.status_code == 200:
    print("   ✅ Direct DELETE worked!")
elif response.status_code == 404:
    print("   ℹ️  Record not found (may have been deleted already)")
