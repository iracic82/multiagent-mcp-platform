import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
headers = {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}

# Get an A record to test
response = requests.get("https://csp.infoblox.com/api/ddi/v1/dns/record?_filter=type=='A'&_limit=1", headers=headers)
if response.status_code == 200:
    records = response.json().get('results', [])
    if records:
        test_record = records[0]
        record_id = test_record['id']
        print(f"Testing DELETE on A record: {record_id}")
        print(f"Name: {test_record.get('name_in_zone', '@')}")
        print(f"IP: {test_record.get('rdata', {}).get('address')}")
        print("=" * 70)
        
        # First, let me just check what the actual error was with the MCP tool
        # by testing the exact same way the client does it
        from services.infoblox_client import InfobloxClient
        
        client = InfobloxClient()
        try:
            result = client.delete_dns_record(record_id)
            print(f"\n✅ Client delete_dns_record() succeeded!")
            print(f"Result: {result}")
        except Exception as e:
            print(f"\n❌ Client delete_dns_record() failed!")
            print(f"Error: {str(e)}")
            
            # Check if it's the 501 error
            if "501" in str(e):
                print("\n🔍 GOT HTTP 501 ERROR!")
                print("This is the same error the agent saw!")
    else:
        print("No A records found")
