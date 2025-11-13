import os
import requests
from services.infoblox_client import InfobloxClient

api_key = os.getenv('INFOBLOX_API_KEY')

# Get a record
resp = requests.get(
    "https://csp.infoblox.com/api/ddi/v1/dns/record?_filter=type=='A'&_limit=1",
    headers={"Authorization": f"Token {api_key}"}
)

if resp.status_code == 200:
    records = resp.json().get('results', [])
    if records:
        record_id = records[0]['id']
        
        print(f"Testing record: {record_id}")
        print("=" * 70)
        
        # Monkey-patch the session.request to see what's actually sent
        client = InfobloxClient()
        original_request = client.session.request
        
        def debug_request(method, url, **kwargs):
            print(f"\n🔍 Actual request being made:")
            print(f"   Method: {method}")
            print(f"   URL: {url}")
            print(f"   Headers: {kwargs.get('headers', 'Using session headers')}")
            if 'headers' in kwargs:
                print(f"   Explicit headers: {kwargs['headers']}")
            else:
                print(f"   Session headers: {dict(client.session.headers)}")
            
            return original_request(method, url, **kwargs)
        
        client.session.request = debug_request
        
        try:
            result = client.delete_dns_record(record_id)
            print(f"\n✅ Success: {result}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
