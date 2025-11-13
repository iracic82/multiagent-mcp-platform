import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
base_url = "https://csp.infoblox.com/api/ddi/v1"

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}

deleted_ids = [
    "dns/record/f736b419-fc77-4a19-b76a-3b60246c969d",
    "dns/record/45064c4e-15db-4a58-85a3-50336e1e1377"
]

print("Verifying deletion...")
print("=" * 70)

for record_id in deleted_ids:
    response = requests.get(f"{base_url}/{record_id}", headers=headers)
    if response.status_code == 404:
        print(f"✅ {record_id}")
        print(f"   Status: DELETED (404 Not Found)")
    elif response.status_code == 200:
        print(f"⚠️  {record_id}")
        print(f"   Status: STILL EXISTS")
    else:
        print(f"❓ {record_id}")
        print(f"   Status: {response.status_code}")
    print()

print("=" * 70)
print("\nChecking if app11 records still exist...")
response = requests.get(f"{base_url}/dns/record?_filter=name_in_zone=='app11'", headers=headers)
if response.status_code == 200:
    records = response.json().get('results', [])
    print(f"Found {len(records)} app11 records")
    if len(records) == 0:
        print("✅ All app11 records successfully deleted!")
    else:
        for r in records:
            print(f"  - {r.get('id')}: {r.get('rdata', {}).get('address')}")
