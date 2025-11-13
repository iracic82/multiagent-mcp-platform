import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
base_url = "https://csp.infoblox.com/api/ddi/v1"

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
}

# Test the exact record IDs from the screenshot
record_ids = [
    "dns/record/f736b419-fc77-4a19-b76a-3b60246c969d",  # Record 1
    "dns/record/45064c4e-15db-4a58-85a3-50336e1e1377"   # Record 2
]

for record_id in record_ids:
    print(f"\nTesting DELETE: {record_id}")
    print("=" * 70)
    
    # First, try to GET the record to see if it exists
    get_response = requests.get(f"{base_url}/{record_id}", headers=headers)
    print(f"GET Status: {get_response.status_code}")
    
    if get_response.status_code == 200:
        record = get_response.json().get('result', {})
        print(f"  Record exists: {record.get('name_in_zone', 'N/A')}.{record.get('zone', 'N/A')}")
        print(f"  IP: {record.get('rdata', {}).get('address', 'N/A')}")
        
        # Now try DELETE
        print(f"\nAttempting DELETE...")
        delete_response = requests.delete(f"{base_url}/{record_id}", headers=headers)
        print(f"DELETE Status: {delete_response.status_code}")
        print(f"DELETE Response: {delete_response.text[:300]}")
        
        if delete_response.status_code == 501:
            print("\n❌ CONFIRMED: HTTP 501 Not Implemented")
            print("   This means DNS record deletion is DISABLED in your")
            print("   Infoblox BloxOne DDI deployment configuration.")
    else:
        print(f"  Record doesn't exist or can't be accessed")
        print(f"  Response: {get_response.text[:200]}")
