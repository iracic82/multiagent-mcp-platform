import re

with open('mcp_infoblox.py', 'r') as f:
    content = f.read()

# Find all @mcp.tool() declarations
tools = re.findall(r'@mcp\.tool\(\)\s*\ndef (\w+)\(', content)

# Categorize tools
categories = {
    'IP Spaces': [],
    'Subnets': [],
    'IP Addresses': [],
    'IPAM Hosts': [],
    'DNS Zones': [],
    'DNS Views': [],
    'DNS Records': [],
    'Federation': [],
    'SOC Insights': [],
    'NIOSXaaS': [],
    'DNS Security': [],
    'DHCP': [],
    'IPAM CRUD': []
}

for tool in tools:
    if 'ip_space' in tool or tool == 'list_ip_spaces':
        categories['IP Spaces'].append(tool)
    elif 'subnet' in tool and 'address' not in tool:
        categories['Subnets'].append(tool)
    elif 'ip_address' in tool and 'ipam_host' not in tool:
        categories['IP Addresses'].append(tool)
    elif 'ipam_host' in tool:
        categories['IPAM Hosts'].append(tool)
    elif 'dns_zone' in tool or tool in ['list_dns_zones', 'create_dns_zone', 'get_dns_zone', 'update_dns_zone', 'delete_dns_zone']:
        categories['DNS Zones'].append(tool)
    elif 'dns_view' in tool or tool in ['list_dns_views', 'create_dns_view', 'get_dns_view', 'update_dns_view', 'delete_dns_view']:
        categories['DNS Views'].append(tool)
    elif any(x in tool for x in ['_record', 'create_a_', 'create_cname', 'create_mx', 'create_txt', 'create_aaaa', 'create_ptr', 'create_srv', 'create_ns', 'create_caa', 'create_naptr']):
        categories['DNS Records'].append(tool)
    elif 'federated' in tool:
        categories['Federation'].append(tool)
    elif 'insight' in tool.lower() or 'security' in tool:
        categories['SOC Insights'].append(tool)
    elif 'nios' in tool.lower() or 'anycast' in tool or 'onprem' in tool:
        categories['NIOSXaaS'].append(tool)
    elif 'policy' in tool or 'ruleset' in tool or 'threat' in tool or 'network_list' in tool:
        categories['DNS Security'].append(tool)
    elif any(x in tool for x in ['dhcp', 'hardware', 'ha_group', 'option_code', 'option_filter', 'hardware_filter']):
        categories['DHCP'].append(tool)
    elif any(x in tool for x in ['range', 'address_block', 'fixed_address']):
        categories['IPAM CRUD'].append(tool)

print("📊 Infoblox MCP Tools Breakdown (82 total):\n")
print("=" * 60)
total = 0
for category, tools_list in categories.items():
    if tools_list:
        print(f"\n{category}: {len(tools_list)}")
        for tool in sorted(tools_list):
            print(f"  • {tool}")
        total += len(tools_list)

print("\n" + "=" * 60)
print(f"✅ Total verified tools: {total}")
