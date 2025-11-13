import os
import requests

api_key = os.getenv('INFOBLOX_API_KEY')
headers = {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}

# Try to delete a record that definitely exists
response = requests.get("https://csp.infoblox.com/api/ddi/v1/dns/record?_limit=1", headers=headers)
if response.status_code == 200:
    records = response.json().get('results', [])
    if records:
        test_record = records[0]
        record_id = test_record['id']
        print(f"Testing DELETE on: {record_id}")
        print(f"Record: {test_record.get('name_in_zone', '@')}")
        print("=" * 70)
        
        # Attempt delete
        del_response = requests.delete(f"https://csp.infoblox.com/api/ddi/v1/{record_id}", headers=headers)
        print(f"Status Code: {del_response.status_code}")
        print(f"Response Headers: {dict(del_response.headers)}")
        print(f"Response Body: '{del_response.text}'")
        print(f"Response Length: {len(del_response.text)} bytes")
        
        if del_response.status_code == 200:
            if len(del_response.text) == 0:
                print("\n✅ DELETE successful - Empty response body")
            elif del_response.text == "{}":
                print("\n✅ DELETE successful - Empty JSON object")
            else:
                try:
                    data = del_response.json()
                    print(f"\n✅ DELETE successful - JSON: {data}")
                except:
                    print(f"\n⚠️  DELETE returned non-JSON: {del_response.text}")
    else:
        print("No records found to test")
