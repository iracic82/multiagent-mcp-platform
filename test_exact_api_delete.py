import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')

# The exact record from your screenshot
record_id = "dns/record/0d762f21-e06a-4722-b49c-266c3864c3bc"

print("Testing EXACT API call as specified in OpenAPI docs")
print("=" * 70)
print(f"Record: application100.infolab.com (10.10.8.8)")
print(f"Record ID: {record_id}")
print("=" * 70)

# Exact API call matching OpenAPI spec
url = f"https://csp.infoblox.com/api/ddi/v1/{record_id}"
headers = {
    "Authorization": f"Token {api_key}"
}

print(f"\nDELETE {url}")
print(f"Headers: {headers}")
print()

response = requests.delete(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Body: '{response.text}'")
print()

if response.status_code == 200:
    print("✅ DELETE SUCCESSFUL!")
    print("   The API DELETE endpoint works perfectly!")
    print("   This means our code is calling it incorrectly.")
elif response.status_code == 501:
    print("❌ HTTP 501 - Not Implemented")
    print("   The API itself is returning this error")
    print("   This is an Infoblox configuration/limitation issue")
elif response.status_code == 404:
    print("ℹ️  HTTP 404 - Record not found")
    print("   Record may have been already deleted")
else:
    print(f"❌ Unexpected response: {response.status_code}")
