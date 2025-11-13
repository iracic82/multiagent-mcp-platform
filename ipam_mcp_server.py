"""
IPAM MCP Server - Exposes IPAM functionality via Model Context Protocol

This server provides tools for querying and managing IP addresses through
Infoblox Universal DDI / BloxOne IPAM systems.
"""

from fastmcp import FastMCP
from services.ipam_client import get_ipam_client
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("IPAM Management")


@mcp.tool()
async def list_subnets(space: Optional[str] = None, limit: int = 50) -> dict:
    """
    List IP subnets from IPAM system.

    Args:
        space: Optional IP space name to filter by
        limit: Maximum number of subnets to return (default: 50)

    Returns:
        Dictionary containing list of subnets with their details

    Examples:
        - list_subnets() - Get first 50 subnets
        - list_subnets(space="prod", limit=100) - Get prod subnets
    """
    try:
        ipam = get_ipam_client()
        subnets = await ipam.list_subnets(space=space, limit=limit)

        # Format for easier reading
        formatted = []
        for subnet in subnets:
            formatted.append({
                "id": subnet.get("id"),
                "address": subnet.get("address"),
                "space": subnet.get("space"),
                "name": subnet.get("name"),
                "comment": subnet.get("comment"),
                "utilization": subnet.get("utilization", {}).get("utilization", 0)
            })

        return {
            "count": len(formatted),
            "subnets": formatted
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_subnet_info(cidr: str) -> dict:
    """
    Get detailed information about a specific subnet from IPAM.

    Args:
        cidr: Subnet in CIDR notation (e.g., "192.168.1.0/24")

    Returns:
        Dictionary with subnet details, utilization, and allocation info

    Examples:
        - get_subnet_info("192.168.1.0/24")
        - get_subnet_info("10.0.0.0/16")
    """
    try:
        ipam = get_ipam_client()

        # Search for subnet
        subnets = await ipam.search_subnets(cidr=cidr)

        if not subnets:
            return {"error": f"Subnet {cidr} not found in IPAM"}

        subnet = subnets[0]

        return {
            "id": subnet.get("id"),
            "address": subnet.get("address"),
            "space": subnet.get("space"),
            "name": subnet.get("name", ""),
            "comment": subnet.get("comment", ""),
            "created_at": subnet.get("created_at"),
            "updated_at": subnet.get("updated_at"),
            "dhcp_config": subnet.get("dhcp_config", {}),
            "utilization": {
                "total_ips": subnet.get("utilization", {}).get("total", 0),
                "used_ips": subnet.get("utilization", {}).get("used", 0),
                "available_ips": subnet.get("utilization", {}).get("available", 0),
                "utilization_percent": subnet.get("utilization", {}).get("utilization", 0),
            },
            "tags": subnet.get("tags", {})
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def check_ip_address(ip_address: str) -> dict:
    """
    Check if an IP address is allocated and get its details.

    Args:
        ip_address: IP address to check (e.g., "192.168.1.10")

    Returns:
        Dictionary with IP address status, allocation info, and usage details

    Examples:
        - check_ip_address("192.168.1.10")
        - check_ip_address("10.0.5.100")
    """
    try:
        ipam = get_ipam_client()
        ip_info = await ipam.get_ip_address(ip_address)

        return {
            "address": ip_info.get("address", ip_address),
            "state": ip_info.get("state", "unknown"),
            "space": ip_info.get("space"),
            "names": ip_info.get("names", []),
            "usage": ip_info.get("usage", []),
            "comment": ip_info.get("comment", ""),
            "created_at": ip_info.get("created_at"),
            "parent_subnet": ip_info.get("parent")
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_utilization(cidr: str) -> dict:
    """
    Get subnet utilization statistics from IPAM.

    Args:
        cidr: Subnet in CIDR notation (e.g., "192.168.1.0/24")

    Returns:
        Dictionary with detailed utilization metrics

    Examples:
        - get_utilization("192.168.1.0/24")
        - get_utilization("10.0.0.0/16")
    """
    try:
        ipam = get_ipam_client()
        utilization = await ipam.get_subnet_utilization(cidr=cidr)

        return utilization

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def find_containing_subnet(ip_address: str) -> dict:
    """
    Find which subnet contains a given IP address.

    Args:
        ip_address: IP address to search for (e.g., "192.168.1.50")

    Returns:
        Dictionary with the containing subnet's information

    Examples:
        - find_containing_subnet("192.168.1.50")
        - find_containing_subnet("10.0.5.100")
    """
    try:
        ipam = get_ipam_client()

        # Search for subnets containing this IP
        subnets = await ipam.search_subnets(address=ip_address)

        if not subnets:
            return {"error": f"No subnet found containing IP {ip_address}"}

        # Return the most specific subnet (smallest CIDR)
        subnet = min(subnets, key=lambda s: int(s.get("address", "/32").split("/")[1]))

        return {
            "ip_address": ip_address,
            "subnet": subnet.get("address"),
            "subnet_name": subnet.get("name", ""),
            "space": subnet.get("space"),
            "utilization_percent": subnet.get("utilization", {}).get("utilization", 0)
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def list_ip_spaces() -> dict:
    """
    List all IP spaces (tenants/organizations) in IPAM.

    Returns:
        Dictionary containing list of IP spaces

    Examples:
        - list_ip_spaces()
    """
    try:
        ipam = get_ipam_client()
        spaces = await ipam.list_ip_spaces()

        formatted = []
        for space in spaces:
            formatted.append({
                "id": space.get("id"),
                "name": space.get("name"),
                "comment": space.get("comment", ""),
                "tags": space.get("tags", {})
            })

        return {
            "count": len(formatted),
            "spaces": formatted
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def find_available_subnets(size: int, space: Optional[str] = None) -> dict:
    """
    Find available subnets of a specific size (with low utilization).

    Args:
        size: Subnet prefix length (e.g., 24 for /24, 16 for /16)
        space: Optional IP space name to filter by

    Returns:
        Dictionary containing list of available subnets

    Examples:
        - find_available_subnets(24) - Find available /24 subnets
        - find_available_subnets(16, space="prod") - Find /16 in prod space
    """
    try:
        ipam = get_ipam_client()
        subnets = await ipam.search_available_subnets(size=size, space=space)

        formatted = []
        for subnet in subnets:
            formatted.append({
                "address": subnet.get("address"),
                "space": subnet.get("space"),
                "name": subnet.get("name", ""),
                "utilization_percent": subnet.get("utilization", {}).get("utilization", 0),
                "available_ips": subnet.get("utilization", {}).get("available", 0)
            })

        return {
            "size": f"/{size}",
            "count": len(formatted),
            "available_subnets": formatted
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def search_subnets(
    cidr: Optional[str] = None,
    tag: Optional[str] = None
) -> dict:
    """
    Search for subnets by various criteria.

    Args:
        cidr: Subnet CIDR to search for (e.g., "192.168.1.0/24")
        tag: Tag to filter by (e.g., "production", "dmz")

    Returns:
        Dictionary containing matching subnets

    Examples:
        - search_subnets(cidr="192.168.1.0/24")
        - search_subnets(tag="production")
    """
    try:
        if not cidr and not tag:
            return {"error": "At least one search criterion (cidr or tag) must be provided"}

        ipam = get_ipam_client()
        subnets = await ipam.search_subnets(cidr=cidr, tag=tag)

        formatted = []
        for subnet in subnets:
            formatted.append({
                "id": subnet.get("id"),
                "address": subnet.get("address"),
                "space": subnet.get("space"),
                "name": subnet.get("name", ""),
                "tags": subnet.get("tags", {}),
                "utilization_percent": subnet.get("utilization", {}).get("utilization", 0)
            })

        return {
            "count": len(formatted),
            "subnets": formatted
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Run the MCP server with HTTP/SSE transport
    mcp.run(transport="sse", port=3001)
