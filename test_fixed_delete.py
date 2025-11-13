import os
from services.infoblox_client import InfobloxClient

print("Testing DELETE with fixed InfobloxClient")
print("=" * 70)

client = InfobloxClient()

# Get a record to test with
try:
    records_resp = client._request("GET", "/api/ddi/v1/dns/record?_filter=type=='A'&_limit=1")
    records = records_resp.get('results', [])
    
    if records:
        record = records[0]
        record_id = record['id']
        record_name = record.get('name_in_zone', '@')
        
        print(f"Testing with record: {record_id}")
        print(f"Name: {record_name}")
        print()
        
        # Try to delete it
        print("Attempting DELETE...")
        try:
            result = client.delete_dns_record(record_id)
            print(f"✅ DELETE SUCCESSFUL!")
            print(f"Result: {result}")
            print()
            print("🎉 The fix works! Content-Type header was the problem!")
        except Exception as e:
            print(f"❌ DELETE FAILED")
            print(f"Error: {str(e)}")
            if "501" in str(e):
                print("\n🚨 Still getting HTTP 501")
                print("The issue is something else")
    else:
        print("No records found to test")
except Exception as e:
    print(f"Error: {e}")
