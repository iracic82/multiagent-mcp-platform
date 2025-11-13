import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
record_id = "dns/record/8da7b69d-e26c-460a-9457-171027ff5b34"

print("Comparing DELETE methods...")
print("=" * 70)

# Method 1: Direct requests (like my successful test)
print("\n1️⃣  Direct requests.delete():")
headers1 = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}
url1 = f"https://csp.infoblox.com/api/ddi/v1/{record_id}"
response1 = requests.delete(url1, headers=headers1)
print(f"   URL: {url1}")
print(f"   Headers: {headers1}")
print(f"   Status: {response1.status_code}")
print(f"   Response: {response1.text}")

# Method 2: Using InfobloxClient (like the agent)
print("\n2️⃣  InfobloxClient (what the agent uses):")
from services.infoblox_client import InfobloxClient
client = InfobloxClient()

# Check what headers the session has
print(f"   Session headers: {dict(client.session.headers)}")
print(f"   Base URL: {client.base_url}")

# Make the request manually to see what happens
url2 = f"{client.base_url}/api/ddi/v1/{record_id}"
print(f"   Full URL: {url2}")

response2 = client.session.delete(url2)
print(f"   Status: {response2.status_code}")
print(f"   Response: {response2.text}")

print("\n" + "=" * 70)
if response1.status_code != response2.status_code:
    print("❌ DIFFERENT status codes!")
    print(f"   Direct: {response1.status_code} vs Client: {response2.status_code}")
else:
    print("✅ Same status codes")
