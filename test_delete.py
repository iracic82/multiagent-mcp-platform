import os
import requests

# Get API key
api_key = os.getenv('INFOBLOX_API_KEY')
if not api_key:
    print("❌ INFOBLOX_API_KEY not set")
    exit(1)

# The record ID from your screenshot
record_id = "dns/record/7736a138-fc77-4a18-b7ab-5b8248c80d6d"

# Base URL
base_url = "https://csp.infoblox.com"
url = f"{base_url}/api/ddi/v1/{record_id}"

print(f"Testing DELETE to: {url}")
print(f"Using API key: {api_key[:20]}...")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Try DELETE
response = requests.delete(url, headers=headers)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\n✅ Delete successful!")
elif response.status_code == 501:
    print("\n❌ 501 Not Implemented - API doesn't support this operation")
    print("This might be a permissions issue or API version problem")
elif response.status_code == 403:
    print("\n❌ 403 Forbidden - API key doesn't have delete permissions")
elif response.status_code == 404:
    print("\n❌ 404 Not Found - Record doesn't exist or wrong endpoint")
else:
    print(f"\n❌ Unexpected error: {response.status_code}")
