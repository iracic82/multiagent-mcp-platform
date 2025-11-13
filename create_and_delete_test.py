import os
from services.infoblox_client import InfobloxClient

# Create a test record
client = InfobloxClient()

print("Creating test DNS record...")
try:
    # First, get a zone
    zones = client.list_dns_zones(limit=1)
    if zones.get('results'):
        zone_id = zones['results'][0]['id']
        zone_name = zones['results'][0]['fqdn']
        print(f"Using zone: {zone_name} ({zone_id})")
        
        # Create an A record
        result = client.create_dns_record(
            name_in_zone="test-delete-me",
            zone=zone_id,
            type="A",
            rdata={"address": "192.168.99.99"},
            view=None,
            ttl=3600,
            comment="Test record for delete testing"
        )
        
        record_id = result['result']['id']
        print(f"✅ Created record: {record_id}")
        print(f"   Name: test-delete-me.{zone_name}")
        print(f"   IP: 192.168.99.99")
        
        # Now try to delete it
        print(f"\nAttempting to delete: {record_id}")
        try:
            delete_result = client.delete_dns_record(record_id)
            print(f"✅ DELETE SUCCESSFUL!")
            print(f"Result: {delete_result}")
        except Exception as e:
            print(f"❌ DELETE FAILED")
            print(f"Error: {str(e)}")
            if "501" in str(e):
                print("\n🚨 HTTP 501 'Not Implemented' error!")
                print("This is a real API limitation/configuration issue")
    else:
        print("No DNS zones found")
except Exception as e:
    print(f"Error: {e}")
