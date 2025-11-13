import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
base_url = "https://csp.infoblox.com/api/ddi/v1"

# Use "Token" not "Bearer"!
headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}

record_id = "dns/record/7736a138-fc77-4a18-b7ab-5b8248c80d6d"

print("Testing DELETE with correct 'Token' auth header...")
print(f"DELETE {base_url}/{record_id}")
print("=" * 60)

response = requests.delete(f"{base_url}/{record_id}", headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    print("\n✅ DELETE SUCCESSFUL!")
elif response.status_code == 501:
    print("\n❌ 501 Not Implemented - API doesn't support delete")
    print("   But the docs show it should work!")
elif response.status_code == 403:
    print("\n❌ 403 Forbidden - API key lacks delete permission")
elif response.status_code == 404:
    print("\n❌ 404 Not Found - Record already deleted or doesn't exist")
else:
    print(f"\n❌ Unexpected error: {response.status_code}")
