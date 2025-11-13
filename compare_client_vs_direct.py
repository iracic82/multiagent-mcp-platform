import os
import requests
from services.infoblox_client import InfobloxClient

api_key = os.getenv('INFOBLOX_API_KEY')

# Get a record that still exists
response = requests.get(
    "https://csp.infoblox.com/api/ddi/v1/dns/record?_filter=name_in_zone~'app'&_limit=1",
    headers={"Authorization": f"Token {api_key}"}
)

if response.status_code == 200:
    records = response.json().get('results', [])
    if records:
        record = records[0]
        record_id = record['id']
        record_name = record.get('name_in_zone', '@')
        
        print(f"Testing with record: {record_id}")
        print(f"Name: {record_name}")
        print("=" * 70)
        
        # Test 1: Direct API call (what we know works)
        print("\n1️⃣  Direct API call:")
        url1 = f"https://csp.infoblox.com/api/ddi/v1/{record_id}"
        headers1 = {"Authorization": f"Token {api_key}"}
        resp1 = requests.delete(url1, headers=headers1)
        print(f"   Status: {resp1.status_code}")
        print(f"   Response: {resp1.text}")
        
        if resp1.status_code == 200:
            print("   ✅ Direct DELETE worked!")
            
            # Now create the record again for the next test
            print("\n   Recreating record for next test...")
            # Skip recreation for now, just test with client
        
        # Test 2: InfobloxClient (what's failing)
        print("\n2️⃣  InfobloxClient:")
        client = InfobloxClient()
        
        # Check the exact URL it's building
        expected_url = f"{client.base_url}/api/ddi/v1/{record_id}"
        print(f"   Expected URL: {expected_url}")
        print(f"   Session headers: {dict(client.session.headers)}")
        
        # Make the raw session call to see what happens
        resp2 = client.session.delete(expected_url)
        print(f"   Raw session DELETE status: {resp2.status_code}")
        print(f"   Raw session DELETE response: {resp2.text[:200]}")
        
        if resp2.status_code != 200:
            print(f"\n❌ Session DELETE failed with {resp2.status_code}")
            print("   There's something wrong with how the session is configured")
        
    else:
        print("No records found")
