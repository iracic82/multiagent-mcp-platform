import os
import requests
from services.infoblox_client import InfobloxClient

api_key = os.getenv('INFOBLOX_API_KEY')

print("Comparing Session vs Direct request...")
print("=" * 70)

# Get a record to test with
url_list = "https://csp.infoblox.com/api/ddi/v1/dns/record?_filter=type=='A'&_limit=1"
headers = {"Authorization": f"Token {api_key}"}

response = requests.get(url_list, headers=headers)
if response.status_code == 200:
    records = response.json().get('results', [])
    if records:
        record = records[0]
        record_id = record['id']
        
        print(f"Testing with record: {record_id}")
        print(f"Name: {record.get('name_in_zone', '@')}")
        print("=" * 70)
        
        # Test 1: Session object
        print("\n🔍 Inspecting InfobloxClient session...")
        client = InfobloxClient()
        print(f"Session type: {type(client.session)}")
        print(f"Session headers: {dict(client.session.headers)}")
        print(f"Session cookies: {client.session.cookies}")
        
        # Check if there are any adapters or hooks
        print(f"Session adapters: {list(client.session.adapters.keys())}")
        print(f"Session hooks: {client.session.hooks}")
        
        # Try making a GET request first with the session
        print("\n📥 Testing GET with session...")
        get_url = f"{client.base_url}/api/ddi/v1/{record_id}"
        get_resp = client.session.get(get_url)
        print(f"GET Status: {get_resp.status_code}")
        
        # Now try DELETE with session
        print(f"\n🗑️  Testing DELETE with session...")
        del_resp = client.session.delete(get_url)
        print(f"DELETE Status: {del_resp.status_code}")
        print(f"DELETE Response: {del_resp.text[:200]}")
        
        if del_resp.status_code == 501:
            print("\n🚨 GOT HTTP 501 with Session!")
            print("This confirms the issue is with requests.Session()")
