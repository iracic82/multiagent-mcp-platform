"""
MCP Server for Subnet Calculator
This server exposes subnet calculation functionality via the Model Context Protocol.
"""

from fastmcp import FastMCP
from services.subnet_calc import calculate_subnet

# Initialize FastMCP server
mcp = FastMCP("Subnet Calculator")


@mcp.tool()
def calculate_subnet_info(cidr: str) -> dict:
    """
    Calculate subnet information from CIDR notation.

    Args:
        cidr: Network address in CIDR notation (e.g., "192.168.1.0/24")

    Returns:
        Dictionary containing:
        - network: Network address
        - broadcast: Broadcast address
        - netmask: Subnet mask
        - first_host: First usable host IP
        - last_host: Last usable host IP
        - usable_hosts: Number of usable host addresses

    Examples:
        - "192.168.1.0/24" -> 254 usable hosts
        - "10.0.0.0/8" -> ~16 million usable hosts
        - "172.16.0.0/16" -> ~65k usable hosts
    """
    result = calculate_subnet(cidr)
    return result


@mcp.tool()
def validate_cidr(cidr: str) -> dict:
    """
    Validate if a string is valid CIDR notation.

    Args:
        cidr: String to validate as CIDR notation

    Returns:
        Dictionary with:
        - valid: Boolean indicating if CIDR is valid
        - message: Description of validation result
    """
    result = calculate_subnet(cidr)

    if "error" in result:
        return {
            "valid": False,
            "message": f"Invalid CIDR: {result['error']}"
        }

    return {
        "valid": True,
        "message": "Valid CIDR notation"
    }


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    mcp.run(transport="sse", port=3002)
