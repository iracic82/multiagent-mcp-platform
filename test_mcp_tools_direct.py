#!/usr/bin/env python3
"""Direct test of MCP tools without agent"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the MCP server module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if API key is loaded
api_key = os.getenv("INFOBLOX_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key (first 20 chars): {api_key[:20]}...")

# Now import and test
from services.niosxaas_client import NIOSXaaSClient

try:
    print("\nInitializing NIOSXaaSClient...")
    client = NIOSXaaSClient()
    print("✅ Client initialized successfully!")

    print("\nTesting list_universal_services...")
    result = client.list_universal_services(limit=5)
    print(f"✅ API call successful!")
    print(f"Found {len(result.get('results', []))} services")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
