import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')

# Get a fresh record
response = requests.get(
    "https://csp.infoblox.com/api/ddi/v1/dns/record?_filter=type=='A'&_limit=1",
    headers={"Authorization": f"Token {api_key}"}
)

if response.status_code == 200:
    records = response.json().get('results', [])
    if records:
        record_id = records[0]['id']
        
        print(f"Testing Content-Type header impact")
        print(f"Record: {record_id}")
        print("=" * 70)
        
        url = f"https://csp.infoblox.com/api/ddi/v1/{record_id}"
        
        # Test 1: Without Content-Type (like direct calls)
        print("\n1️⃣  DELETE WITHOUT Content-Type header:")
        headers1 = {"Authorization": f"Token {api_key}"}
        resp1 = requests.delete(url, headers=headers1)
        print(f"   Status: {resp1.status_code}")
        print(f"   Response: {resp1.text}")
        
        if resp1.status_code == 200:
            print("   ✅ Works without Content-Type")
        elif resp1.status_code == 501:
            print("   ❌ HTTP 501 without Content-Type!")
        
        # Now test WITH Content-Type (if first test didn't delete it)
        if resp1.status_code != 200:
            print("\n2️⃣  DELETE WITH Content-Type: application/json:")
            headers2 = {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            }
            resp2 = requests.delete(url, headers=headers2)
            print(f"   Status: {resp2.status_code}")
            print(f"   Response: {resp2.text}")
            
            if resp2.status_code == 501:
                print("   🚨 HTTP 501 WITH Content-Type!")
                print("   This is the problem - Content-Type header breaks DELETE!")
