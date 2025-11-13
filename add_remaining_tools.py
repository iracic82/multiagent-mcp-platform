#!/usr/bin/env python3
"""
Script to add remaining 35 IPAM and DHCP MCP tools to mcp_infoblox.py
This adds all the missing CRUD operations for ranges, blocks, fixed addresses, and DHCP resources
"""

# IPAM CRUD Tools (15 tools) - to add after IPAM section
IPAM_TOOLS = """
# IPAM Range Tools
@mcp.tool()
def list_ip_ranges(space_filter: Optional[str] = None, limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        filter_str = f"space=='{space_filter}'" if space_filter else None
        return client.list_ranges(filter=filter_str, limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_ip_range(start: str, end: str, space_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.create_range(start=start, end=end, space=space_id, comment=comment)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_ip_range(range_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_range(range_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_ip_range(range_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_range(range_id)
    except Exception as e:
        return {"error": str(e)}

# IPAM Address Block Tools
@mcp.tool()
def list_address_blocks(space_filter: Optional[str] = None, limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        filter_str = f"space=='{space_filter}'" if space_filter else None
        return client.list_address_blocks(filter=filter_str, limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_address_block(address: str, space_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.create_address_block(address=address, space=space_id, comment=comment)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_address_block(block_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_address_block(block_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_address_block(block_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_address_block(block_id)
    except Exception as e:
        return {"error": str(e)}

# Fixed Address CRUD Tools
@mcp.tool()
def get_fixed_address(address_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.get_fixed_address(address_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_fixed_address(address_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_fixed_address(address_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_fixed_address(address_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_fixed_address(address_id)
    except Exception as e:
        return {"error": str(e)}

# Subnet CRUD Tools
@mcp.tool()
def update_subnet(subnet_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_subnet(subnet_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_subnet(subnet_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_subnet(subnet_id)
    except Exception as e:
        return {"error": str(e)}

"""

# DHCP Tools (20 tools) - to add after Federation section
DHCP_TOOLS = """
# ==================== DHCP Management Tools ====================

# DHCP Host Tools
@mcp.tool()
def list_dhcp_hosts(limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.list_dhcp_hosts(limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_dhcp_host(host_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.get_dhcp_host(host_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_dhcp_host(host_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_dhcp_host(host_id, updates)
    except Exception as e:
        return {"error": str(e)}

# Hardware Tools
@mcp.tool()
def list_hardware(limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.list_hardware(limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_hardware(mac_address: str, name: Optional[str] = None, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.create_hardware(address=mac_address, name=name, comment=comment)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_hardware(hardware_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_hardware(hardware_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_hardware(hardware_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_hardware(hardware_id)
    except Exception as e:
        return {"error": str(e)}

# HA Group Tools
@mcp.tool()
def list_ha_groups(limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.list_ha_groups(limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_ha_group(group_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.get_ha_group(group_id)
    except Exception as e:
        return {"error": str(e)}

# DHCP Option Code Tools
@mcp.tool()
def list_option_codes(limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.list_option_codes(limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_option_code(code: int, name: str, type: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.create_option_code(code=code, name=name, type=type, comment=comment)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_option_code(code_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_option_code(code_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_option_code(code_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_option_code(code_id)
    except Exception as e:
        return {"error": str(e)}

# Hardware Filter Tools
@mcp.tool()
def list_hardware_filters(limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.list_hardware_filters(limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_hardware_filter(name: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.create_hardware_filter(name=name, comment=comment)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_hardware_filter(filter_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_hardware_filter(filter_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_hardware_filter(filter_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_hardware_filter(filter_id)
    except Exception as e:
        return {"error": str(e)}

# Option Filter Tools
@mcp.tool()
def list_option_filters(limit: int = 100) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.list_option_filters(limit=limit)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_option_filter(name: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.create_option_filter(name=name, comment=comment)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def update_option_filter(filter_id: str, comment: Optional[str] = None) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        updates = {}
        if comment is not None:
            updates["comment"] = comment
        return client.update_option_filter(filter_id, updates)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_option_filter(filter_id: str) -> dict:
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        return client.delete_option_filter(filter_id)
    except Exception as e:
        return {"error": str(e)}

"""

def insert_tools():
    """Insert all remaining tools into mcp_infoblox.py"""
    with open('mcp_infoblox.py', 'r') as f:
        content = f.read()

    # Insert IPAM tools after IPAM Host Tools section
    ipam_marker = "# ==================== DNS Data Tools ===================="
    content = content.replace(ipam_marker, IPAM_TOOLS + "\n" + ipam_marker)

    # Insert DHCP tools before NIOSXaaS section
    dhcp_marker = "# ==================== NIOSXaaS Tools ===================="
    content = content.replace(dhcp_marker, DHCP_TOOLS + "\n" + dhcp_marker)

    with open('mcp_infoblox.py', 'w') as f:
        f.write(content)

    print("✅ Added 35 remaining MCP tools (15 IPAM + 20 DHCP)")
    print("📊 Total new tools added: 46 (5 IPAM Host + 6 DNS + 15 IPAM CRUD + 20 DHCP)")

if __name__ == "__main__":
    insert_tools()
