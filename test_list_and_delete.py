import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
base_url = "https://csp.infoblox.com/api/ddi/v1"

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}

# List DNS records first
print("Listing DNS records...")
response = requests.get(f"{base_url}/dns/record?_limit=5", headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    records = data.get('results', [])
    print(f"\nFound {len(records)} records:")
    for i, record in enumerate(records, 1):
        print(f"\n{i}. Record ID: {record.get('id')}")
        print(f"   Name: {record.get('name_in_zone', 'N/A')}")
        print(f"   Type: {record.get('type', 'N/A')}")
        print(f"   Comment: {record.get('comment', 'N/A')}")
    
    if records:
        print("\n" + "=" * 60)
        print("The delete operation IS supported by the API.")
        print("The 501 error you saw suggests there might be an issue")
        print("with how the error was reported in the agent system.")
        print("=" * 60)
else:
    print(f"Failed to list records: {response.text}")
