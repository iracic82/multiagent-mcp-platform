import os
from services.infoblox_client import InfobloxClient

print("Full lifecycle test: Create → Delete")
print("=" * 70)

client = InfobloxClient()

# Get a zone
zones_resp = client._request("GET", "/api/ddi/v1/dns/auth_zone?_limit=1")
if zones_resp.get('results'):
    zone = zones_resp['results'][0]
    zone_id = zone['id']
    zone_fqdn = zone['fqdn']
    
    print(f"Using zone: {zone_fqdn} ({zone_id})")
    
    # Create a test record
    print("\n1️⃣  Creating test DNS A record...")
    try:
        create_result = client.create_dns_record(
            name_in_zone="test-lifecycle",
            zone=zone_id,
            type="A",
            rdata={"address": "192.168.100.100"},
            view=None,
            ttl=3600,
            comment="Testing delete immediately after create"
        )
        
        record_id = create_result['result']['id']
        print(f"   ✅ Created: {record_id}")
        print(f"   FQDN: test-lifecycle.{zone_fqdn}")
        
        # Immediately try to delete it
        print(f"\n2️⃣  Deleting the record we just created...")
        try:
            delete_result = client.delete_dns_record(record_id)
            print(f"   ✅ DELETE SUCCESS!")
            print(f"   Result: {delete_result}")
        except Exception as e:
            print(f"   ❌ DELETE FAILED!")
            print(f"   Error: {str(e)}")
            if "501" in str(e):
                print("\n   🚨 HTTP 501 - This record cannot be deleted!")
                print("   This suggests records created via this method have delete restrictions")
    except Exception as e:
        print(f"   ❌ CREATE FAILED: {e}")
else:
    print("No zones found")
