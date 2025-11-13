"""
MCP Server for Infoblox BloxOne DDI
Provides tools for IPAM, DNS Data, and DNS Config management via Infoblox API
"""

from fastmcp import FastMCP
from services.infoblox_client import InfobloxClient
from services.niosxaas_client import NIOSXaaSClient
from services.atcfw_client import AtcfwClient
from services.insights_client import InsightsClient
from typing import Optional, List, Dict, Any

# Initialize FastMCP server
mcp = FastMCP("Infoblox BloxOne DDI")

# Initialize Infoblox client (will use env vars)
try:
    client = InfobloxClient()
except ValueError as e:
    print(f"Warning: {e}")
    print("Set INFOBLOX_API_KEY environment variable to use this server")
    client = None

# Initialize NIOSXaaS client (same API key as DDI)
try:
    niosxaas_client = NIOSXaaSClient()
except ValueError as e:
    print(f"Warning: {e}")
    print("Set INFOBLOX_API_KEY environment variable to use NIOSXaaS features")
    niosxaas_client = None

# Initialize Atcfw client (same API key as DDI)
try:
    atcfw_client = AtcfwClient()
except ValueError as e:
    print(f"Warning: {e}")
    print("Set INFOBLOX_API_KEY environment variable to use Atcfw/DFP features")
    atcfw_client = None

# Initialize Insights client (same API key as DDI)
try:
    insights_client = InsightsClient()
except ValueError as e:
    print(f"Warning: {e}")
    print("Set INFOBLOX_API_KEY environment variable to use SOC Insights features")
    insights_client = None


# ==================== IPAM Tools ====================

@mcp.tool()
def list_ip_spaces(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List IP spaces in Infoblox IPAM.

    Args:
        name_filter: Filter by name (e.g., "corp" to find names containing "corp")
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of IP spaces containing id, name, and other properties

    Examples:
        - list_ip_spaces() -> All IP spaces
        - list_ip_spaces(name_filter="production") -> Spaces with "production" in name
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"name~'{name_filter}'" if name_filter else None
        result = client.list_ip_spaces(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_subnets(
    space_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List subnets from Infoblox IPAM.

    Args:
        space_filter: Filter by IP space ID
        address_filter: Filter by address CIDR (e.g., "192.168.0.0/16")
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of subnets containing address, space, comment, and utilization

    Examples:
        - list_subnets() -> All subnets
        - list_subnets(address_filter="10.0.0.0/8") -> Subnets in 10.0.0.0/8 range
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filters = []
        if space_filter:
            filters.append(f"space=='{space_filter}'")
        if address_filter:
            filters.append(f"address=='{address_filter}'")

        filter_expr = " and ".join(filters) if filters else None
        result = client.list_subnets(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_subnet(
    address: str,
    space: str,
    comment: Optional[str] = None,
    dhcp_host: Optional[str] = None
) -> dict:
    """
    Create a new subnet in Infoblox IPAM.

    Args:
        address: Network address in CIDR notation (e.g., "192.168.1.0/24")
        space: IP space ID where subnet will be created
        comment: Optional description/comment for the subnet
        dhcp_host: Optional DHCP host ID to serve this subnet

    Returns:
        Dictionary with created subnet details including id, address, and space

    Examples:
        - create_subnet("10.20.30.0/24", "ipam/ip_space/abc123", "Marketing subnet")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        kwargs = {}
        if dhcp_host:
            kwargs["dhcp_host"] = dhcp_host

        result = client.create_subnet(
            address=address,
            space=space,
            comment=comment,
            **kwargs
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_ip_addresses(
    address_filter: Optional[str] = None,
    state_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List IP addresses from Infoblox IPAM.

    Args:
        address_filter: Filter by specific IP address
        state_filter: Filter by state (used, free)
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of IP addresses and their allocation state

    Examples:
        - list_ip_addresses(state_filter="free") -> Available IP addresses
        - list_ip_addresses(address_filter="192.168.1.100") -> Specific IP details
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filters = []
        if address_filter:
            filters.append(f"address=='{address_filter}'")
        if state_filter:
            filters.append(f"state=='{state_filter}'")

        filter_expr = " and ".join(filters) if filters else None
        result = client.list_addresses(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def reserve_fixed_address(
    address: str,
    space: str,
    comment: Optional[str] = None,
    name: Optional[str] = None
) -> dict:
    """
    Reserve a fixed IP address in Infoblox IPAM (DHCP reservation).

    Args:
        address: IP address to reserve (e.g., "192.168.1.10")
        space: IP space ID
        comment: Optional description
        name: Optional hostname for the reservation

    Returns:
        Dictionary with reservation details

    Examples:
        - reserve_fixed_address("10.0.1.100", "ipam/ip_space/xyz", "File server", "fileserver01")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        kwargs = {}
        if name:
            kwargs["name"] = name

        result = client.create_fixed_address(
            address=address,
            space=space,
            comment=comment,
            **kwargs
        )
        return result
    except Exception as e:
        return {"error": str(e)}


# ==================== IPAM Host Tools ====================

@mcp.tool()
def list_ipam_hosts(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List IPAM hosts (network equipment with IP addresses and DNS records).

    IPAM Host represents network connected equipment with one or more IP addresses.
    Combines DNS A/AAAA records with IP address management.

    Args:
        name_filter: Filter by hostname (e.g., "web" finds web01.example.com)
        limit: Maximum number of hosts to return (default: 100)

    Returns:
        Dict with IPAM hosts including names, IP addresses, and DNS associations

    Example:
        - list_ipam_hosts()
        - list_ipam_hosts(name_filter="server")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}

    try:
        filter_str = f"name~'{name_filter}'" if name_filter else None
        result = client.list_ipam_hosts(filter=filter_str, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_ipam_host(
    name: str,
    ip_address: str,
    space_id: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create IPAM host with IP address and DNS record.

    Creates a host entry that automatically manages both the IP address
    assignment and the corresponding DNS A/AAAA record.

    Args:
        name: Fully qualified domain name (e.g., "web01.example.com")
        ip_address: IPv4 or IPv6 address
        space_id: IP space ID (e.g., "ipam/ip_space/abc123")
        comment: Optional description

    Returns:
        Dict with created host details including ID

    Example:
        - create_ipam_host("web01.example.com", "192.168.1.10", "ipam/ip_space/default", "Web server")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}

    try:
        addresses = [{"address": ip_address, "space": space_id}]
        result = client.create_ipam_host(
            name=name,
            addresses=addresses,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_ipam_host(host_id: str) -> dict:
    """
    Get IPAM host details by ID.

    Args:
        host_id: Host ID (e.g., "ipam/host/abc123")

    Returns:
        Dict with complete host information including all IP addresses and DNS records

    Example:
        - get_ipam_host("ipam/host/abc123")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}

    try:
        result = client.get_ipam_host(host_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def update_ipam_host(
    host_id: str,
    name: Optional[str] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Update IPAM host properties.

    Args:
        host_id: Host ID (e.g., "ipam/host/abc123")
        name: New hostname (FQDN)
        comment: New description

    Returns:
        Dict with updated host details

    Example:
        - update_ipam_host("ipam/host/abc123", comment="Production web server")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}

    try:
        updates = {}
        if name:
            updates["name"] = name
        if comment is not None:
            updates["comment"] = comment

        result = client.update_ipam_host(host_id, updates)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def delete_ipam_host(host_id: str) -> dict:
    """
    Delete IPAM host (removes IP and DNS associations).

    Args:
        host_id: Host ID (e.g., "ipam/host/abc123")

    Returns:
        Dict with deletion confirmation

    Example:
        - delete_ipam_host("ipam/host/abc123")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}

    try:
        result = client.delete_ipam_host(host_id)
        return result
    except Exception as e:
        return {"error": str(e)}



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


# ==================== DNS Data Tools ====================

@mcp.tool()
def list_dns_records(
    zone_filter: Optional[str] = None,
    name_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List DNS records from Infoblox.

    Args:
        zone_filter: Filter by zone ID
        name_filter: Filter by record name (supports wildcards with ~)
        type_filter: Filter by record type (A, AAAA, CNAME, MX, TXT, PTR, SRV, etc.)
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of DNS records

    Examples:
        - list_dns_records(type_filter="A") -> All A records
        - list_dns_records(name_filter="www", type_filter="CNAME") -> CNAME records for "www"
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filters = []
        if zone_filter:
            filters.append(f"zone=='{zone_filter}'")
        if name_filter:
            filters.append(f"name_in_zone~'{name_filter}'")
        if type_filter:
            filters.append(f"type=='{type_filter}'")

        filter_expr = " and ".join(filters) if filters else None
        result = client.list_dns_records(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_a_record(
    name: str,
    zone: str,
    ip_address: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None,
    view: Optional[str] = None
) -> dict:
    """
    Create DNS A record (IPv4 address).

    Args:
        name: Record name within zone (e.g., "www" for www.example.com)
        zone: Zone ID (e.g., "dns/auth_zone/abc123")
        ip_address: IPv4 address (e.g., "192.168.1.100")
        ttl: Time to live in seconds (optional, inherits from zone if not set)
        comment: Optional description
        view: DNS view ID (optional)

    Returns:
        Dictionary with created record details

    Examples:
        - create_a_record("www", "dns/auth_zone/abc123", "192.168.1.100", ttl=3600)
        - create_a_record("mail", "dns/auth_zone/abc123", "10.0.1.50", comment="Mail server")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_dns_record(
            name_in_zone=name,
            zone=zone,
            record_type="A",
            rdata={"address": ip_address},
            view=view,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_cname_record(
    name: str,
    zone: str,
    target: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None,
    view: Optional[str] = None
) -> dict:
    """
    Create DNS CNAME record (alias).

    Args:
        name: Record name within zone (e.g., "blog" for blog.example.com)
        zone: Zone ID
        target: Target domain name (e.g., "www.example.com.")
        ttl: Time to live in seconds
        comment: Optional description
        view: DNS view ID

    Returns:
        Dictionary with created record details

    Examples:
        - create_cname_record("blog", "dns/auth_zone/abc123", "www.example.com.")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_dns_record(
            name_in_zone=name,
            zone=zone,
            record_type="CNAME",
            rdata={"cname": target},
            view=view,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_mx_record(
    name: str,
    zone: str,
    mail_server: str,
    priority: int,
    ttl: Optional[int] = None,
    comment: Optional[str] = None,
    view: Optional[str] = None
) -> dict:
    """
    Create DNS MX record (mail exchanger).

    Args:
        name: Record name within zone (often "@" for zone apex)
        zone: Zone ID
        mail_server: Mail server domain name (e.g., "mail.example.com.")
        priority: Priority value (0-65535, lower is higher priority)
        ttl: Time to live in seconds
        comment: Optional description
        view: DNS view ID

    Returns:
        Dictionary with created record details

    Examples:
        - create_mx_record("@", "dns/auth_zone/abc123", "mail.example.com.", 10)
        - create_mx_record("@", "dns/auth_zone/abc123", "mail2.example.com.", 20)
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_dns_record(
            name_in_zone=name,
            zone=zone,
            record_type="MX",
            rdata={
                "exchange": mail_server,
                "preference": priority
            },
            view=view,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_txt_record(
    name: str,
    zone: str,
    text: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None,
    view: Optional[str] = None
) -> dict:
    """
    Create DNS TXT record (text record, often used for SPF, DKIM, verification).

    Args:
        name: Record name within zone (e.g., "@" for zone apex, "_dmarc" for DMARC)
        zone: Zone ID
        text: Text content (e.g., "v=spf1 include:_spf.google.com ~all")
        ttl: Time to live in seconds
        comment: Optional description
        view: DNS view ID

    Returns:
        Dictionary with created record details

    Examples:
        - create_txt_record("@", "dns/auth_zone/abc123", "v=spf1 include:_spf.google.com ~all")
        - create_txt_record("_dmarc", "dns/auth_zone/abc123", "v=DMARC1; p=quarantine;")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_dns_record(
            name_in_zone=name,
            zone=zone,
            record_type="TXT",
            rdata={"text": text},
            view=view,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def delete_dns_record(record_id: str) -> dict:
    """
    Delete a DNS record (moves to recycle bin).

    Args:
        record_id: Record ID to delete (e.g., "dns/record/abc123")

    Returns:
        Dictionary with deletion confirmation

    Examples:
        - delete_dns_record("dns/record/abc123")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.delete_dns_record(record_id)
        return {"success": True, "message": f"Record {record_id} deleted (moved to recycle bin)"}
    except Exception as e:
        return {"error": str(e)}



@mcp.tool()
def create_aaaa_record(
    name_in_zone: str,
    zone_id: str,
    ipv6_address: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Create AAAA record (IPv6 address).

    Args:
        name_in_zone: Record name (e.g., "web" for web.example.com)
        zone_id: DNS zone ID
        ipv6_address: IPv6 address (e.g., "2001:db8::1")
        ttl: Time to live in seconds
        comment: Optional description

    Returns:
        Dict with created AAAA record details

    Example:
        - create_aaaa_record("web", "dns/auth_zone/abc123", "2001:db8::1")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        result = client.create_aaaa_record(
            name_in_zone=name_in_zone,
            zone=zone_id,
            address=ipv6_address,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_ptr_record(
    name_in_zone: str,
    zone_id: str,
    domain_name: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Create PTR record (Reverse DNS).

    Args:
        name_in_zone: Reverse IP (e.g., "100" for 100.1.168.192.in-addr.arpa)
        zone_id: Reverse zone ID
        domain_name: Domain name to point to (e.g., "web.example.com")
        ttl: Time to live in seconds
        comment: Optional description

    Returns:
        Dict with created PTR record details

    Example:
        - create_ptr_record("100", "dns/auth_zone/reverse123", "web.example.com")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        result = client.create_ptr_record(
            name_in_zone=name_in_zone,
            zone=zone_id,
            dname=domain_name,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_srv_record(
    name_in_zone: str,
    zone_id: str,
    priority: int,
    weight: int,
    port: int,
    target: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Create SRV record (Service record for service discovery).

    Args:
        name_in_zone: Service name (e.g., "_sip._tcp")
        zone_id: DNS zone ID
        priority: Priority (lower is higher priority, 0-65535)
        weight: Load balancing weight (0-65535)
        port: Service port number
        target: Target hostname
        ttl: Time to live in seconds
        comment: Optional description

    Returns:
        Dict with created SRV record details

    Example:
        - create_srv_record("_sip._tcp", "dns/auth_zone/abc123", 10, 60, 5060, "sipserver.example.com")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        result = client.create_srv_record(
            name_in_zone=name_in_zone,
            zone=zone_id,
            priority=priority,
            weight=weight,
            port=port,
            target=target,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_ns_record(
    name_in_zone: str,
    zone_id: str,
    nameserver: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Create NS record (Name Server delegation).

    Args:
        name_in_zone: Subdomain or "@" for zone apex
        zone_id: DNS zone ID
        nameserver: Name server hostname (e.g., "ns1.example.com")
        ttl: Time to live in seconds
        comment: Optional description

    Returns:
        Dict with created NS record details

    Example:
        - create_ns_record("subdomain", "dns/auth_zone/abc123", "ns1.example.com")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        result = client.create_ns_record(
            name_in_zone=name_in_zone,
            zone=zone_id,
            dname=nameserver,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_caa_record(
    name_in_zone: str,
    zone_id: str,
    flags: int,
    tag: str,
    value: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Create CAA record (Certificate Authority Authorization).

    Args:
        name_in_zone: Record name or "@" for zone apex
        zone_id: DNS zone ID
        flags: Flags (0=non-critical, 128=critical)
        tag: Property tag ("issue", "issuewild", "iodef")
        value: CA domain or mailto URI
        ttl: Time to live in seconds
        comment: Optional description

    Returns:
        Dict with created CAA record details

    Example:
        - create_caa_record("@", "dns/auth_zone/abc123", 0, "issue", "letsencrypt.org")
        - create_caa_record("@", "dns/auth_zone/abc123", 0, "iodef", "mailto:security@example.com")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        result = client.create_caa_record(
            name_in_zone=name_in_zone,
            zone=zone_id,
            flags=flags,
            tag=tag,
            value=value,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_naptr_record(
    name_in_zone: str,
    zone_id: str,
    order: int,
    preference: int,
    flags: str,
    services: str,
    regexp: str,
    replacement: str,
    ttl: Optional[int] = None,
    comment: Optional[str] = None
) -> dict:
    """
    Create NAPTR record (Name Authority Pointer for ENUM/SIP).

    Args:
        name_in_zone: Record name
        zone_id: DNS zone ID
        order: Order of processing (0-65535)
        preference: Preference for same order (0-65535)
        flags: Flags ("S", "A", "U", "P")
        services: Service parameters (e.g., "E2U+sip")
        regexp: Regular expression for substitution
        replacement: Replacement pattern or domain
        ttl: Time to live in seconds
        comment: Optional description

    Returns:
        Dict with created NAPTR record details

    Example:
        - create_naptr_record("1234", "dns/auth_zone/abc123", 100, 10, "U", "E2U+sip", "!^.*$!sip:info@example.com!", ".")
    """
    if not client:
        return {"error": "Infoblox client not initialized."}
    try:
        result = client.create_naptr_record(
            name_in_zone=name_in_zone,
            zone=zone_id,
            order=order,
            preference=preference,
            flags=flags,
            services=services,
            regexp=regexp,
            replacement=replacement,
            ttl=ttl,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


# ==================== DNS Config Tools ====================

@mcp.tool()
def list_dns_zones(
    zone_type: str = "auth",
    name_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List DNS zones from Infoblox.

    Args:
        zone_type: Zone type - "auth" for authoritative or "forward" for forward zones
        name_filter: Filter by zone name (e.g., "example.com")
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of DNS zones

    Examples:
        - list_dns_zones() -> All authoritative zones
        - list_dns_zones(zone_type="forward") -> All forward zones
        - list_dns_zones(name_filter="example.com") -> Zones matching "example.com"
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"fqdn~'{name_filter}'" if name_filter else None

        if zone_type == "forward":
            result = client.list_forward_zones(filter=filter_expr, limit=limit)
        else:
            result = client.list_auth_zones(filter=filter_expr, limit=limit)

        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_dns_zone(
    domain: str,
    zone_type: str = "auth",
    comment: Optional[str] = None,
    view: Optional[str] = None
) -> dict:
    """
    Create a new DNS zone in Infoblox.

    Args:
        domain: Fully qualified domain name (e.g., "example.com")
        zone_type: Zone type - "auth" for authoritative or "forward" for forward zone
        comment: Optional description
        view: DNS view ID (optional)

    Returns:
        Dictionary with created zone details

    Examples:
        - create_dns_zone("example.com", comment="Production domain")
        - create_dns_zone("internal.local", zone_type="auth", comment="Internal zone")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        if zone_type == "forward":
            result = client.create_forward_zone(
                fqdn=domain,
                view=view,
                comment=comment
            )
        else:
            result = client.create_auth_zone(
                fqdn=domain,
                view=view,
                comment=comment
            )

        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_dns_views(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List DNS views from Infoblox.

    Args:
        name_filter: Filter by view name
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of DNS views

    Examples:
        - list_dns_views() -> All DNS views
        - list_dns_views(name_filter="internal") -> Views with "internal" in name
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"name~'{name_filter}'" if name_filter else None
        result = client.list_dns_views(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


# ==================== IPAM Federation Tools ====================

@mcp.tool()
def list_federated_realms(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List federated realms in Infoblox IPAM Federation.

    Args:
        name_filter: Filter by realm name (e.g., "global" to find names containing "global")
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of federated realms containing id, name, and properties

    Examples:
        - list_federated_realms() -> All federated realms
        - list_federated_realms(name_filter="production") -> Realms with "production" in name
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"name~'{name_filter}'" if name_filter else None
        result = client.list_federated_realms(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_federated_realm(
    name: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create a new federated realm in Infoblox IPAM Federation.

    Args:
        name: Realm name
        comment: Optional description/comment for the realm

    Returns:
        Dictionary with created realm details including id and name

    Examples:
        - create_federated_realm("global-realm", "Global federation realm")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_federated_realm(name=name, comment=comment)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_federated_blocks(
    realm_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List federated blocks from Infoblox IPAM Federation.

    Args:
        realm_filter: Filter by federated realm ID
        address_filter: Filter by address CIDR (e.g., "10.0.0.0/8")
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of federated blocks containing address, realm, and allocation info

    Examples:
        - list_federated_blocks() -> All federated blocks
        - list_federated_blocks(address_filter="10.0.0.0/8") -> Blocks in 10.0.0.0/8 range
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filters = []
        if realm_filter:
            filters.append(f"federated_realm=='{realm_filter}'")
        if address_filter:
            filters.append(f"address=='{address_filter}'")

        filter_expr = " and ".join(filters) if filters else None
        result = client.list_federated_blocks(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_federated_block(
    address: str,
    federated_realm: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create a new federated block in Infoblox IPAM Federation.

    Args:
        address: Network address in CIDR notation (e.g., "10.0.0.0/8")
        federated_realm: Federated realm ID where block will be created
        comment: Optional description/comment for the block

    Returns:
        Dictionary with created block details including id, address, and realm

    Examples:
        - create_federated_block("10.0.0.0/8", "federation/federated_realm/abc123", "Global block")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_federated_block(
            address=address,
            federated_realm=federated_realm,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def allocate_next_federated_block(
    federated_block_id: str,
    cidr: int,
    comment: Optional[str] = None
) -> dict:
    """
    Allocate next available federated block from a parent block.

    Args:
        federated_block_id: Parent federated block ID (e.g., "federation/federated_block/xyz")
        cidr: CIDR prefix length for the new block (e.g., 16 for /16)
        comment: Optional description for the allocated block

    Returns:
        Dictionary with allocated block details

    Examples:
        - allocate_next_federated_block("federation/federated_block/xyz", 16, "Regional block")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.allocate_next_available_federated_block(
            federated_block_id=federated_block_id,
            cidr=cidr,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_delegations(
    realm_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List delegations in Infoblox IPAM Federation.

    Args:
        realm_filter: Filter by federated realm ID
        address_filter: Filter by delegated address CIDR
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of delegations

    Examples:
        - list_delegations() -> All delegations
        - list_delegations(realm_filter="federation/federated_realm/abc") -> Delegations in specific realm
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filters = []
        if realm_filter:
            filters.append(f"federated_realm=='{realm_filter}'")
        if address_filter:
            filters.append(f"address=='{address_filter}'")

        filter_expr = " and ".join(filters) if filters else None
        result = client.list_delegations(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_delegation(
    address: str,
    federated_realm: str,
    delegated_to: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create a delegation in Infoblox IPAM Federation.

    Args:
        address: Network address in CIDR notation to delegate
        federated_realm: Federated realm ID
        delegated_to: Tenant/organization ID to delegate to
        comment: Optional description

    Returns:
        Dictionary with created delegation details

    Examples:
        - create_delegation("10.1.0.0/16", "federation/federated_realm/abc", "tenant-123", "Regional delegation")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_delegation(
            address=address,
            federated_realm=federated_realm,
            delegated_to=delegated_to,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_overlapping_blocks(
    realm_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List overlapping blocks in Infoblox IPAM Federation.

    Args:
        realm_filter: Filter by federated realm ID
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of overlapping blocks

    Examples:
        - list_overlapping_blocks() -> All overlapping blocks
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"federated_realm=='{realm_filter}'" if realm_filter else None
        result = client.list_overlapping_blocks(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_overlapping_block(
    address: str,
    federated_realm: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create an overlapping block in Infoblox IPAM Federation.

    Args:
        address: Network address in CIDR notation
        federated_realm: Federated realm ID
        comment: Optional description

    Returns:
        Dictionary with created overlapping block details

    Examples:
        - create_overlapping_block("192.168.0.0/16", "federation/federated_realm/abc", "Overlapping network")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_overlapping_block(
            address=address,
            federated_realm=federated_realm,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_reserved_blocks(
    realm_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List reserved blocks in Infoblox IPAM Federation.

    Args:
        realm_filter: Filter by federated realm ID
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of reserved blocks

    Examples:
        - list_reserved_blocks() -> All reserved blocks
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"federated_realm=='{realm_filter}'" if realm_filter else None
        result = client.list_reserved_blocks(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_reserved_block(
    address: str,
    federated_realm: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create a reserved block in Infoblox IPAM Federation.

    Args:
        address: Network address in CIDR notation
        federated_realm: Federated realm ID
        comment: Optional description

    Returns:
        Dictionary with created reserved block details

    Examples:
        - create_reserved_block("172.16.0.0/12", "federation/federated_realm/abc", "Reserved for future use")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_reserved_block(
            address=address,
            federated_realm=federated_realm,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_forward_delegations(
    realm_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List forward-looking delegations in Infoblox IPAM Federation.

    Args:
        realm_filter: Filter by federated realm ID
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of forward-looking delegations

    Examples:
        - list_forward_delegations() -> All forward-looking delegations
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filter_expr = f"federated_realm=='{realm_filter}'" if realm_filter else None
        result = client.list_forward_delegations(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_forward_delegation(
    address: str,
    federated_realm: str,
    delegated_to: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create a forward-looking delegation in Infoblox IPAM Federation.

    Args:
        address: Network address in CIDR notation to delegate
        federated_realm: Federated realm ID
        delegated_to: Tenant/organization ID to delegate to
        comment: Optional description

    Returns:
        Dictionary with created forward delegation details

    Examples:
        - create_forward_delegation("10.2.0.0/16", "federation/federated_realm/abc", "tenant-456", "Future delegation")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_forward_delegation(
            address=address,
            federated_realm=federated_realm,
            delegated_to=delegated_to,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_federated_pools(
    realm_filter: Optional[str] = None,
    name_filter: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List federated pools in Infoblox IPAM Federation.

    Args:
        realm_filter: Filter by federated realm ID
        name_filter: Filter by pool name
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of federated pools

    Examples:
        - list_federated_pools() -> All federated pools
        - list_federated_pools(name_filter="datacenter") -> Pools with "datacenter" in name
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        filters = []
        if realm_filter:
            filters.append(f"federated_realm=='{realm_filter}'")
        if name_filter:
            filters.append(f"name~'{name_filter}'")

        filter_expr = " and ".join(filters) if filters else None
        result = client.list_federated_pools(filter=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_federated_pool(
    name: str,
    federated_realm: str,
    comment: Optional[str] = None
) -> dict:
    """
    Create a federated pool in Infoblox IPAM Federation.

    Args:
        name: Pool name
        federated_realm: Federated realm ID
        comment: Optional description

    Returns:
        Dictionary with created pool details

    Examples:
        - create_federated_pool("datacenter-pool", "federation/federated_realm/abc", "Main datacenter pool")
    """
    if not client:
        return {"error": "Infoblox client not initialized. Check INFOBLOX_API_KEY."}

    try:
        result = client.create_federated_pool(
            name=name,
            federated_realm=federated_realm,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}



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


# ==================== NIOSXaaS (Universal Service / VPN) Tools ====================
# NOTE: Individual API tools commented out - use configure_vpn_infrastructure instead

# @mcp.tool()
# def list_universal_services(name_filter: Optional[str] = None, limit: int = 100) -> dict:
#     """
#     List Universal Services (VPN services).
#
#     Args:
#         name_filter: Filter by service name
#         limit: Maximum number of results (default: 100)
#
#     Returns:
#         Dictionary with list of universal services
#
#     Examples:
#         - list_universal_services() -> All services
#         - list_universal_services(name_filter="VPN") -> Services with "VPN" in name
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         filter_expr = f"name~'{name_filter}'" if name_filter else None
#         result = niosxaas_client.list_universal_services(filter_expr=filter_expr, limit=limit)
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def create_universal_service(
#     name: str,
#     description: str = "",
#     capabilities: Optional[List[dict]] = None,
#     tags: Optional[dict] = None
# ) -> dict:
#     """
#     ⚠️  DO NOT USE THIS FOR VPN CREATION! Use 'configure_vpn_infrastructure' instead!
#
#     This is a LOW-LEVEL tool for creating Universal Services WITHOUT credentials.
#     For VPN creation, ALWAYS use 'configure_vpn_infrastructure' which handles
#     the complete setup including credentials, endpoints, and access locations.
#
#     Only use this if you need to create a service without VPN credentials (rare).
#
#     Args:
#         name: Service name
#         description: Service description
#         capabilities: List of capabilities (e.g., [{"type": "dns"}])
#         tags: Optional tags
#
#     Returns:
#         Dictionary with created service details
#
#     ⚠️  FOR VPN CREATION: Use 'configure_vpn_infrastructure' instead!
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.create_universal_service(
#             name=name,
#             description=description,
#             capabilities=capabilities,
#             tags=tags
#         )
#         return result
#     except Exception as e:
#         return {"error": str(e)}


# @mcp.tool()
# def list_vpn_endpoints(name_filter: Optional[str] = None, limit: int = 100) -> dict:
#     """
#     List VPN endpoints.
#
#     Args:
#         name_filter: Filter by endpoint name
#         limit: Maximum number of results (default: 100)
#
#     Returns:
#         Dictionary with list of endpoints including CNAMEs
#
#     Examples:
#         - list_vpn_endpoints() -> All endpoints
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         filter_expr = f"name~'{name_filter}'" if name_filter else None
#         result = niosxaas_client.list_endpoints(filter_expr=filter_expr, limit=limit)
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def create_vpn_endpoint(
#     name: str,
#     service_location: str,
#     service_ip: str,
#     universal_service_id: str,
#     size: str,
#     neighbour_ips: List[str],
#     routing_config: dict,
#     preferred_provider: str = "AWS"
# ) -> dict:
#     """
#     Create a VPN endpoint.
#
#     Args:
#         name: Endpoint name
#         service_location: Service location (e.g., "AWS Europe (Frankfurt)")
#         service_ip: Service IP address
#         universal_service_id: Universal service ID
#         size: Endpoint size (S, M, L)
#         neighbour_ips: List of neighbor IP addresses
#         routing_config: Routing configuration with BGP settings
#         preferred_provider: Cloud provider (default: AWS)
#
#     Returns:
#         Dictionary with created endpoint details
#
#     Examples:
#         - create_vpn_endpoint("Endpoint-1", "AWS Europe (Frankfurt)", "10.10.10.3",
#                              "service-id", "S", ["10.10.10.4"],
#                              {"bgp_config": {"asn": "65500", "hold_down": 90}})
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.create_endpoint(
#             name=name,
#             service_location=service_location,
#             service_ip=service_ip,
#             universal_service_id=universal_service_id,
#             size=size,
#             neighbour_ips=neighbour_ips,
#             routing_config=routing_config,
#             preferred_provider=preferred_provider
#         )
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def list_access_locations(name_filter: Optional[str] = None, limit: int = 100) -> dict:
#     """
#     List access locations (VPN sites).
#
#     Args:
#         name_filter: Filter by location name
#         limit: Maximum number of results (default: 100)
#
#     Returns:
#         Dictionary with list of access locations
#
#     Examples:
#         - list_access_locations() -> All access locations
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         filter_expr = f"name~'{name_filter}'" if name_filter else None
#         result = niosxaas_client.list_access_locations(filter_expr=filter_expr, limit=limit)
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def create_access_location(
#     endpoint_id: str,
#     location_id: str,
#     credential_id: str,
#     wan_ip_addresses: List[str],
#     cloud_type: str = "AWS",
#     cloud_region: Optional[str] = None,
#     tunnel_configs: Optional[List[dict]] = None
# ) -> dict:
#     """
#     Create an access location (VPN site).
#
#     Args:
#         endpoint_id: Endpoint ID
#         location_id: Location ID
#         credential_id: Credential ID for VPN authentication
#         wan_ip_addresses: List of WAN IP addresses
#         cloud_type: Cloud type (default: AWS)
#         cloud_region: Cloud region (e.g., "eu-central-1")
#         tunnel_configs: Tunnel configurations with BGP settings
#
#     Returns:
#         Dictionary with created access location details
#
#     Examples:
#         - create_access_location("endpoint-id", "location-id", "cred-id", ["1.1.1.1"])
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.create_access_location(
#             endpoint_id=endpoint_id,
#             location_id=location_id,
#             credential_id=credential_id,
#             wan_ip_addresses=wan_ip_addresses,
#             cloud_type=cloud_type,
#             tunnel_configs=tunnel_configs
#         )
#         return result
#     except Exception as e:
#         return {"error": str(e)}


@mcp.tool()
def list_supported_sizes() -> dict:
    """
    List supported endpoint sizes.

    Returns:
        Dictionary with available sizes (S, M, L, etc.)

    Examples:
        - list_supported_sizes() -> All available endpoint sizes
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    try:
        result = niosxaas_client.list_supported_sizes()
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_cloud_regions(provider: str = "AWS") -> dict:
    """
    List available cloud provider regions.

    Args:
        provider: Cloud provider (default: AWS)

    Returns:
        Dictionary with available regions

    Examples:
        - list_cloud_regions("AWS") -> All AWS regions
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    try:
        result = niosxaas_client.list_cloud_provider_regions(provider=provider)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_service_capabilities() -> dict:
    """
    List available service capabilities (DNS, DFP, etc.).

    Returns:
        Dictionary with available capabilities

    Examples:
        - list_service_capabilities() -> All available capabilities
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    try:
        result = niosxaas_client.list_capabilities()
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def configure_vpn_infrastructure(vpn_payload: dict) -> dict:
    """
    *** PRIMARY TOOL FOR VPN CREATION ***
    Create complete VPN infrastructure from natural language requests.

    ⚠️  CRITICAL - DO NOT CREATE PARTIAL VPN DEPLOYMENTS:

    THIS TOOL REQUIRES **ALL** DETAILS FOR A COMPLETE VPN SETUP!
    If the user doesn't provide complete information, DO NOT call this tool!
    Instead, STOP and ask for ALL missing details.

    🚨 AWS CLOUD VPN MANDATE: DUAL TUNNELS REQUIRED!
    AWS Cloud VPN requires EXACTLY 2 tunnel_configs (Primary + Secondary) or the API will reject with:
    "2 connections are required for AWS Cloud VPN"

    You MUST create TWO tunnel_configs in access_locations:
    - Primary tunnel (path: "primary", name: "Pri")
    - Secondary tunnel (path: "secondary", name: "Sec")

    Each tunnel MUST have its own:
    - credential_id (ref_cred_pri and ref_cred_sec)
    - access_ip (Primary Access IP and Secondary Access IP from user)
    - bgp_configs with neighbour_ips (from Site BGP Neighbor IPs)

    REQUIRED INFORMATION FOR FULL VPN (ALL MANDATORY):
    1. VPN Service Name (e.g., "Production-VPN")
    2. PSK Password (e.g., "InfobloxLab.2025") - default to "InfobloxLab.2025" if not provided
    3. Endpoint BGP ASN (e.g., "65500") - REQUIRED
    4. Site BGP ASN (e.g., "64512") - REQUIRED
    5. Site BGP Neighbor IPs - MUST BE 2 IPs (e.g., ["169.254.21.1", "169.254.22.1"]) - REQUIRED FOR DUAL TUNNELS
    6. Service IP for endpoint (e.g., "10.10.10.3") - REQUIRED
    7. Endpoint Neighbor IPs (e.g., ["10.10.10.4", "10.10.10.5"]) - REQUIRED
    8. Service Location/Region (e.g., "AWS Europe (Frankfurt)" or "eu-central-1") - REQUIRED
    9. Primary Access IP (e.g., "1.1.1.1") - REQUIRED
    10. Secondary Access IP (e.g., "1.2.3.4") - REQUIRED
    11. Endpoint size: S, M, or L (default to "S" if not specified)

    ❌ NO PARTIAL DEPLOYMENTS ALLOWED!
    Do NOT create a VPN with just the service name and credentials.
    Do NOT create a VPN without endpoints.
    Do NOT create a VPN without access locations.

    AGENT INSTRUCTIONS - STRICT REQUIREMENTS:
    - If user says "Create a VPN called MyVPN" with NO BGP/endpoint details →
      DO NOT CALL THIS TOOL! Instead respond:
      "To create a complete VPN infrastructure, I need the following details:

       1. Endpoint BGP ASN (your cloud-side BGP ASN)
       2. Site BGP ASN (your on-premises BGP ASN)
       3. Site BGP Neighbor IPs (BGP neighbor addresses for primary and secondary tunnels)
       4. Service IP (endpoint service IP)
       5. Endpoint Neighbor IPs (BGP neighbor IPs for the endpoint)
       6. Region (AWS region like eu-central-1)
       7. Primary Access IP (your primary WAN IP)
       8. Secondary Access IP (your secondary WAN IP)

       Please provide all these details and I'll create the complete VPN setup for you.
       Note: I cannot create partial VPN deployments - all components must be configured together."

    - If user provides SOME but not ALL details → DO NOT CALL THIS TOOL!
      List the SPECIFIC missing items and ask for them:
      "I still need these details to create a complete VPN:
       - Missing item 1
       - Missing item 2
       Please provide the missing information."

    USE THIS TOOL when the user asks to:
    - "Create a VPN" / "Set up VPN infrastructure" / "Deploy a VPN service"
    - "Connect my AWS VPC to on-premises" / "Create site-to-site VPN"
    - "I need a VPN between AWS and my datacenter"

    HOW TO USE WITH NATURAL LANGUAGE:
    When user says: "Create a VPN called MyVPN with PSK 'SecureKey123'"

    You should build this JSON payload:
    {
        "universal_service": {
            "operation": "CREATE",
            "name": "MyVPN",  # <-- Use the name from user's request
            "capabilities": [{"type": "dns"}],  # Always include this
            "tags": {}  # Optional tags
        },
        "credentials": {
            "create": [{
                "id": "ref_cred_myvpn",  # Unique reference ID
                "type": "psk",  # Always "psk" for VPN
                "name": "myvpn-psk-<random>",  # Add random suffix to avoid duplicates
                "value": "SecureKey123",  # <-- PSK value from user
                "cred_data": {}
            }],
            "update": []
        },
        "endpoints": {"create": [], "update": [], "delete": []},
        "access_locations": {"create": [], "update": [], "delete": []},
        "locations": {"create": [], "update": []}
    }

    COMPLETE WORKING EXAMPLE - User says: "Create VPN for AWS region us-east-1":
    {
        "universal_service": {
            "operation": "CREATE",
            "name": "AWS-US-East-VPN",
            "capabilities": [{"type": "dns"}],
            "tags": {"region": "us-east-1", "cloud": "aws"}
        },
        "credentials": {
            "create": [{
                "id": "ref_cred_aws_us_east",
                "type": "psk",
                "name": "aws-us-east-psk-a1b2c3",  # Add random suffix
                "value": "InfobloxLab.2025",
                "cred_data": {}
            }],
            "update": []
        },
        "endpoints": {"create": [], "update": [], "delete": []},
        "access_locations": {"create": [], "update": [], "delete": []},
        "locations": {"create": [], "update": []}
    }

    COMPLETE WORKING EXAMPLE WITH ENDPOINTS + BGP + ACCESS LOCATIONS:
    User says: "Create VPN with endpoint in AWS eu-central-1, BGP ASN 65500 at endpoint and 64512 at site,
                neighbor IPs 169.254.21.1 and 169.254.22.1, access IPs 1.1.1.1 and 1.2.3.4, PSK InfobloxLab.2025"

    🚨 CRITICAL: This example shows DUAL TUNNELS (Primary + Secondary) which is MANDATORY for AWS Cloud VPN!
    Notice: 2 credentials, 2 tunnel_configs, 2 access IPs, 2 neighbor IPs

    {
        "universal_service": {
            "operation": "CREATE",
            "name": "AWS-EU-Central-VPN",
            "capabilities": [{"type": "dns"}],
            "tags": {}
        },
        "credentials": {
            "create": [
                {
                    "id": "ref_cred_pri",  # <-- PRIMARY credential for primary tunnel
                    "type": "psk",
                    "name": "pri-psk-a1b2c3",
                    "value": "InfobloxLab.2025",
                    "cred_data": {}
                },
                {
                    "id": "ref_cred_sec",  # <-- SECONDARY credential for secondary tunnel
                    "type": "psk",
                    "name": "sec-psk-d4e5f6",
                    "value": "InfobloxLab.2025",
                    "cred_data": {}
                }
            ],
            "update": []
        },
        "endpoints": {
            "create": [{
                "id": "ref_endpoint_Test",
                "name": "Test-Endpoint",
                "size": "S",
                "service_location": "AWS Europe (Frankfurt)",
                "service_ip": "10.10.10.3",
                "neighbour_ips": ["10.10.10.4", "10.10.10.5"],
                "preferred_provider": "AWS",
                "routing_type": "dynamic",
                "routing_config": {
                    "bgp_config": {
                        "asn": "65500",
                        "hold_down": 90,
                        "keep_alive": 30
                    }
                }
            }],
            "update": []
        },
        "access_locations": {
            "create": [{
                "endpoint_id": "ref_endpoint_Test",
                "id": "ref_accessLoc_SITE",
                "routing_type": "dynamic",
                "tunnel_configs": [
                    {
                        "name": "Pri",
                        "physical_tunnels": [{
                            "path": "primary",
                            "credential_id": "ref_cred_pri",
                            "index": 0,
                            "access_ip": "1.1.1.1",
                            "bgp_configs": [{
                                "asn": "64512",
                                "hop_limit": 2,
                                "neighbour_ips": ["169.254.21.1"]
                            }]
                        }]
                    },
                    {
                        "name": "Sec",
                        "physical_tunnels": [{
                            "path": "secondary",
                            "credential_id": "ref_cred_sec",
                            "index": 0,
                            "access_ip": "1.2.3.4",
                            "bgp_configs": [{
                                "asn": "64512",
                                "hop_limit": 2,
                                "neighbour_ips": ["169.254.22.1"]
                            }]
                        }]
                    }
                ],
                "type": "Cloud VPN",
                "name": "SITE",
                "cloud_type": "AWS",
                "cloud_region": "eu-central-1",
                "lan_subnets": []
            }],
            "update": [],
            "delete": []
        },
        "locations": {"create": [], "update": []}
    }

    IMPORTANT RULES FOR BUILDING JSON FROM NATURAL LANGUAGE:
    1. credential "id": Use pattern "ref_cred_<servicename>" (reference ID for linking)
    2. credential "name": MUST add random 6-char suffix (e.g., "-a1b2c3") to avoid duplicates
    3. credential "type": Always "psk" for VPN tunnels
    4. credential "value": PSK from user or default "InfobloxLab.2025"
    5. endpoint "service_location": Map region to full name (e.g., "eu-central-1" → "AWS Europe (Frankfurt)")
    6. endpoint "size": Default "S" if not specified
    7. endpoint "routing_config.bgp_config.asn": BGP ASN from user (string format)
    8. endpoint "routing_config.bgp_config.hold_down": Default 90
    9. endpoint "neighbour_ips": BGP neighbor IPs from user (array of strings)
    10. access_location "location_id": Use pattern "ref_loc_<servicename>"
    11. access_location "credential_id": MUST match credential "id" for linking
    12. access_location "wan_ip_addresses": Customer WAN IPs (array of strings)

    CREDENTIAL NAME GENERATION:
    - Base name: Use service name + "-psk"
    - Add suffix: Append "-" + random 6 hex chars
    - Example: "MyVPN" → credential name: "myvpn-psk-4f9a2e"

    🔧 UPDATE EXAMPLE - Update Access Location with AWS Tunnel IPs:
    When AWS VPN is created and returns tunnel outside IPs (e.g., "3.71.133.7", "3.65.225.91"),
    you need to UPDATE the Infoblox access location with these IPs.

    STEP 1: First, get the current endpoint and access location:
    - Call list_universal_services() or get_universal_service(service_id)
    - Call list_vpn_endpoints() or get_vpn_endpoint(endpoint_id)
    - Call list_vpn_access_locations() - get the access location details

    STEP 2: Build UPDATE payload with new AWS tunnel IPs:
    {
        "universal_service": {
            "operation": "UPDATE",  # <-- IMPORTANT: Use UPDATE not CREATE
            "id": "the-service-id-from-step1",  # Service ID without "infra/universal_service/" prefix
            "name": "Production-VPN"
        },
        "endpoints": {
            "create": [],
            "update": [/* Copy current endpoint config from step 1 */],
            "delete": []
        },
        "access_locations": {
            "create": [],
            "update": [{
                "endpoint_id": "endpoint-id-from-step1",
                "id": "access-location-id-from-step1",
                "routing_type": "dynamic",
                "type": "Cloud VPN",
                "name": "SITE",
                "cloud_type": "AWS",
                "cloud_region": "eu-central-1",
                "lan_subnets": [],
                "tunnel_configs": [
                    {
                        "id": "tunnel-config-id-from-step1",  # <-- CRITICAL: Must include existing ID
                        "name": "Pri",
                        "physical_tunnels": [{
                            "path": "primary",
                            "credential_id": "credential-id-from-step1",
                            "index": 0,
                            "access_ip": "3.71.133.7",  # <-- NEW AWS tunnel IP here!
                            "bgp_configs": [{
                                "id": "bgp-config-id-from-step1",  # <-- CRITICAL: Must include existing ID
                                "asn": "64512",
                                "hop_limit": 2,
                                "cloud_cidr": "169.254.21.0/30"
                            }]
                        }]
                    },
                    {
                        "id": "tunnel-config-id-2-from-step1",  # <-- CRITICAL: Must include existing ID
                        "name": "Sec",
                        "physical_tunnels": [{
                            "path": "secondary",
                            "credential_id": "credential-id-2-from-step1",
                            "index": 0,
                            "access_ip": "3.65.225.91",  # <-- NEW AWS tunnel IP here!
                            "bgp_configs": [{
                                "id": "bgp-config-id-2-from-step1",  # <-- CRITICAL: Must include existing ID
                                "asn": "64512",
                                "hop_limit": 2,
                                "cloud_cidr": "169.254.22.0/30"
                            }]
                        }]
                    }
                ]
            }],
            "delete": []
        },
        "credentials": {"create": [], "update": []},
        "locations": {"create": [], "update": []}
    }

    CRITICAL FOR UPDATES:
    - operation MUST be "UPDATE" not "CREATE"
    - Include existing "id" fields for tunnel_configs, bgp_configs, etc
    - Only change the "access_ip" fields with new AWS tunnel IPs
    - Keep all other fields from the current configuration

    WHAT THIS TOOL DOES:
    - Creates Universal Service (VPN service container)
    - Creates PSK credentials for tunnel authentication
    - Can create Endpoints (cloud connection points)
    - Can create Access Locations (on-prem/branch connections)
    - Atomic operation: All-or-nothing transaction
    - Auto-retry on conflicts (409/429 errors)

    Returns:
        Dictionary with created resource IDs and status

    IMPORTANT - AFTER SUCCESSFUL VPN CREATION:
    After this tool successfully creates a VPN, you MUST tell the user about the next step:

    "✅ VPN created successfully!

    🔍 NEXT STEP - Get CNAMEs for AWS Configuration:
    Before you can configure the AWS side of the VPN, you need to retrieve the endpoint CNAMEs.
    These CNAMEs are the public DNS addresses that AWS will use to connect to your Infoblox VPN endpoints.

    Would you like me to retrieve the CNAMEs for this endpoint now?"

    Then wait for user confirmation before calling get_vpn_endpoint_cnames().

    REMEMBER: Build the JSON from the user's natural language - DON'T ask the user to provide JSON!
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    # VALIDATION: Reject partial VPN deployments
    has_endpoints = vpn_payload.get("endpoints", {}).get("create", [])
    has_access_locations = vpn_payload.get("access_locations", {}).get("create", [])

    if not has_endpoints and not has_access_locations:
        return {
            "error": "PARTIAL_DEPLOYMENT_REJECTED",
            "message": """Cannot create partial VPN deployment with only service and credentials.

A complete VPN infrastructure requires ALL of the following:
1. Endpoint BGP ASN (cloud-side BGP ASN, e.g., "65500")
2. Site BGP ASN (on-premises BGP ASN, e.g., "64512")
3. Site BGP Neighbor IPs (BGP neighbors for tunnels, e.g., ["169.254.21.1", "169.254.22.1"])
4. Service IP (endpoint service IP, e.g., "10.10.10.3")
5. Endpoint Neighbor IPs (BGP neighbors for endpoint, e.g., ["10.10.10.4", "10.10.10.5"])
6. Region (AWS region like "eu-central-1" or "AWS Europe (Frankfurt)")
7. Primary Access IP (your primary WAN IP, e.g., "1.1.1.1")
8. Secondary Access IP (your secondary WAN IP, e.g., "1.2.3.4")
9. Endpoint size: S, M, or L (defaults to S)
10. PSK Password (defaults to "InfobloxLab.2025" if not specified)

Please provide ALL these details to create a complete, functional VPN infrastructure."""
        }

    try:
        import json
        print(f"\n🔍 DEBUG: Calling consolidated_configure with payload:")
        print(json.dumps(vpn_payload, indent=2))
        result = niosxaas_client.consolidated_configure(vpn_payload)
        print(f"✅ DEBUG: Success! Result: {result}")
        return result
    except Exception as e:
        print(f"❌ DEBUG: Exception caught: {type(e).__name__}: {str(e)}")
        if hasattr(e, 'response'):
            print(f"   Response status: {e.response.status_code}")
            print(f"   Response body: {e.response.text}")
        return {"error": str(e)}


@mcp.tool()
def get_vpn_endpoint_cnames(endpoint_id: Optional[str] = None) -> dict:
    """
    Get VPN endpoint with CNAME addresses (for AWS Customer Gateway creation).

    Args:
        endpoint_id: Optional endpoint ID to get specific endpoint, otherwise gets first endpoint

    Returns:
        Dictionary with endpoint details including CNAMEs array

    Examples:
        - get_vpn_endpoint_cnames() -> Get first endpoint with CNAMEs
        - get_vpn_endpoint_cnames("endpoint-id-123") -> Get specific endpoint

    IMPORTANT - AFTER RETRIEVING CNAMEs:
    After successfully retrieving CNAMEs, you MUST guide the user to the next step:

    "✅ CNAMEs retrieved successfully!

    📋 CNAMEs for AWS VPN Configuration:
    [List the CNAMEs from the response]

    🔧 NEXT STEP - Configure AWS VPN:
    Now you need to create the AWS side of the VPN connection. This includes:
    1. Customer Gateway (using the CNAMEs above)
    2. Virtual Private Gateway (or Transit Gateway)
    3. VPN Connection

    IMPORTANT - Check for Existing AWS Resources First:
    Before creating new AWS resources, check if the user wants to use existing VPCs and VPN Gateways:

    1. Call list_vpcs() to see available VPCs in the region
    2. Call list_vpn_gateways() to see available VPN Gateways
    3. Present the options to the user:

    Would you like me to help you create the AWS VPN infrastructure now?

    First, let me check what AWS resources are already available:
    - What AWS Region? (e.g., eu-central-1)

    Then I'll check for existing VPCs and VPN Gateways. You can either:
    - Use an existing VPC and VPN Gateway (recommended if available)
    - Create new resources

    I'll also need:
    - Customer Gateway BGP ASN (the Site BGP ASN from your Infoblox VPN)"

    Then wait for user to provide AWS details before proceeding with AWS VPN creation.

    🔗 FINAL STEP - After AWS VPN is created:
    After AWS creates the VPN connections and returns the tunnel outside IPs, you MUST update
    the Infoblox access location with those AWS tunnel IPs to complete the connection.

    Tell the user:
    "🔧 FINAL STEP - Update Infoblox with AWS Tunnel IPs:
    Now that AWS has created the VPN connections, I need to update your Infoblox access location
    with the AWS tunnel outside IPs so the tunnels can establish.

    Would you like me to update the Infoblox configuration with the AWS tunnel IPs now?"

    Then call configure_vpn_infrastructure with UPDATE operation to update the access_location
    with the AWS tunnel outside IPs in the physical_tunnels access_ip fields.
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    try:
        if endpoint_id:
            result = niosxaas_client.get_endpoint(endpoint_id)
        else:
            # Get first endpoint
            endpoints = niosxaas_client.list_endpoints(limit=1)
            if "results" in endpoints and len(endpoints["results"]) > 0:
                result = endpoints["results"][0]
            elif "result" in endpoints:
                result = endpoints["result"]
            else:
                return {"error": "No endpoints found"}

        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def delete_vpn_service(service_name: str, confirm: bool = False) -> dict:
    """
    Delete a VPN service (Universal Service) by name.

    Args:
        service_name: Name of the VPN service to delete (e.g., "Production-VPN", "Test-VPN")
        confirm: Safety confirmation - must be True to actually delete (default: False)

    Returns:
        Dictionary with deletion status

    Examples:
        - delete_vpn_service("Test-VPN", confirm=True) -> Deletes the Test-VPN service
        - delete_vpn_service("Production-VPN") -> Returns error (confirm=False, safety check)

    ⚠️ IMPORTANT - SAFETY WARNINGS:
    This tool PERMANENTLY DELETES the VPN service and ALL associated resources:
    - Universal Service
    - Endpoints
    - Access Locations
    - Tunnel Configurations
    - Credentials

    🛡️ SAFETY PROTOCOL - MANDATORY STEPS:

    STEP 1 - LIST AVAILABLE VPNS:
    When user says "delete VPN" or "delete a VPN service", you MUST:
    1. Call list_universal_services() first
    2. Show user ALL available VPN services with their names and IDs
    3. Ask: "Which VPN service would you like to delete? Please provide the exact service name."

    STEP 2 - CONFIRM DELETION:
    After user provides the service name:
    1. Show what will be deleted (service name, ID, endpoints, tunnels)
    2. Ask: "⚠️ WARNING: This will PERMANENTLY delete '{service_name}' and all configurations.
       This includes:
       - VPN service {service_name}
       - All endpoints and tunnels
       - All credentials and access locations

       This action CANNOT be undone. Are you absolutely sure you want to proceed? (yes/no)"

    STEP 3 - EXECUTE DELETION:
    Only after user explicitly confirms with "yes":
    1. Call delete_vpn_service(service_name, confirm=True)
    2. Report the result to user

    Example conversation:
    User: "Delete a VPN"
    Agent: "Let me show you the available VPN services..."
           [Calls list_universal_services()]
           "I found these VPN services:
            - Production-VPN (ID: abc123)
            - Test-VPN (ID: def456)

            Which VPN service would you like to delete? Please provide the exact name."
    User: "Test-VPN"
    Agent: "⚠️ WARNING: This will PERMANENTLY delete 'Test-VPN' and all configurations...
            Are you absolutely sure? (yes/no)"
    User: "yes"
    Agent: [Calls delete_vpn_service("Test-VPN", confirm=True)]

    NEVER delete production services without multiple confirmations!
    NEVER skip the list_universal_services() step!
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    if not confirm:
        return {
            "error": "SAFETY_CHECK_FAILED",
            "message": f"Deletion of '{service_name}' requires explicit confirmation. Set confirm=True to proceed.",
            "warning": "This operation is irreversible and will delete all associated VPN infrastructure."
        }

    try:
        # Step 1: Find the service by name (try exact match first, then case-insensitive)
        services = niosxaas_client.list_universal_services(filter_expr=f"name=='{service_name}'")
        results = services.get("results", [])

        # If exact match fails, try case-insensitive search
        if not results:
            all_services = niosxaas_client.list_universal_services()
            all_results = all_services.get("results", [])
            # Case-insensitive match
            results = [s for s in all_results if s.get("name", "").lower() == service_name.lower()]

            if results:
                actual_name = results[0].get("name")
                print(f"📝 Note: Found service with name '{actual_name}' (case-insensitive match for '{service_name}')")

        if not results:
            return {
                "error": "SERVICE_NOT_FOUND",
                "message": f"No VPN service found with name '{service_name}'",
                "suggestion": "Use list_universal_services() to see available services"
            }

        if len(results) > 1:
            return {
                "error": "MULTIPLE_MATCHES",
                "message": f"Found {len(results)} services matching '{service_name}'",
                "matches": [{"id": s.get("id"), "name": s.get("name")} for s in results],
                "suggestion": "Service name must be unique. Please check the exact name."
            }

        # Step 2: Extract service ID
        service = results[0]
        service_id = service.get("id", "").split("/")[-1]  # Extract UUID from "infra/universal_service/UUID"

        print(f"🗑️ Deleting VPN service '{service_name}' (ID: {service_id})...")

        # Step 3: Delete the service
        result = niosxaas_client.delete_universal_service(service_id)

        return {
            "success": True,
            "message": f"✅ Successfully deleted VPN service '{service_name}'",
            "deleted_service_id": service_id,
            "deleted_service_name": service_name,
            "warning": "All associated endpoints, tunnels, and credentials have been removed."
        }

    except Exception as e:
        print(f"❌ Deletion failed: {type(e).__name__}: {str(e)}")
        return {
            "error": "DELETION_FAILED",
            "message": str(e),
            "service_name": service_name
        }


# @mcp.tool()
# def list_vpn_credentials(name_filter: Optional[str] = None) -> dict:
#     """
#     List VPN credentials (PSK for tunnels) via IAM API.
#
#     Args:
#         name_filter: Optional partial name filter (e.g., "test" matches "test-123", "test-abc")
#
#     Returns:
#         Dictionary with 'results' containing list of credentials
#
#     Examples:
#         - list_vpn_credentials() -> List all credentials
#         - list_vpn_credentials(name_filter="test") -> Filter by name containing "test"
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.list_credentials(name_filter=name_filter)
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def create_vpn_credential(name: str, value: str, unique_suffix: bool = True) -> dict:
#     """
#     Create VPN PSK credential via IAM API. Automatically adds unique suffix to avoid name conflicts.
#
#     Args:
#         name: Base credential name (e.g., "vpn-psk", "test-credential")
#         value: Pre-shared key value (e.g., "InfobloxLab.2025")
#         unique_suffix: If True, adds 6-char UUID suffix to name (default: True, recommended)
#
#     Returns:
#         Dictionary with 'results' containing credential details including 'id'
#
#     Examples:
#         - create_vpn_credential("vpn-psk", "InfobloxLab.2025") -> Creates "vpn-psk-a1b2c3"
#         - create_vpn_credential("test-key", "MySecureKey123", unique_suffix=False) -> Creates "test-key"
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.create_credential(
#             name=name,
#             value=value,
#             unique_suffix=unique_suffix
#         )
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def get_vpn_credential(credential_id: str) -> dict:
#     """
#     Get VPN credential by ID via IAM API.
#
#     Args:
#         credential_id: Credential ID (UUID format, e.g., "6b6d8eaa-eef7-4193-994f-fae8ba22eec7")
#
#     Returns:
#         Dictionary with 'result' containing credential details
#
#     Examples:
#         - get_vpn_credential("6b6d8eaa-eef7-4193-994f-fae8ba22eec7")
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.get_credential(credential_id)
#         return result
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @mcp.tool()
# def delete_vpn_credential(credential_id: str) -> dict:
#     """
#     Delete VPN credential via IAM API.
#
#     Args:
#         credential_id: Credential ID to delete (UUID format)
#
#     Returns:
#         Dictionary with deletion status
#
#     Examples:
#         - delete_vpn_credential("6b6d8eaa-eef7-4193-994f-fae8ba22eec7")
#     """
#     if not niosxaas_client:
#         return {"error": "NIOSXaaS client not initialized."}
#
#     try:
#         result = niosxaas_client.delete_credential(credential_id)
#         return result
#     except Exception as e:
#         return {"error": str(e)}


@mcp.tool()
def update_vpn_access_location(
    location_id: str,
    tunnel_configs: Optional[List[dict]] = None,
    wan_ip_addresses: Optional[List[str]] = None
) -> dict:
    """
    Update VPN access location tunnel IPs after AWS VPN creation.

    This tool uses the Infoblox consolidated/configure API to properly update
    tunnel IPs. Provide the tunnel IP from AWS VPN connection to update the
    primary tunnel configuration.

    Args:
        location_id: Access location ID (short or full ID)
        tunnel_configs: Full tunnel configuration (for advanced updates)
        wan_ip_addresses: WAN IP address to update (first IP is used for primary tunnel)

    Returns:
        Dictionary with update result from Infoblox API

    Examples:
        - update_vpn_access_location("m7m2bbbtfctnlnvrndxhc2n5z5tqhrqj", wan_ip_addresses=["3.74.147.156"])
        - update_vpn_access_location("location-123", wan_ip_addresses=["52.1.2.3"])
    """
    if not niosxaas_client:
        return {"error": "NIOSXaaS client not initialized."}

    try:
        # Extract tunnel_ip from wan_ip_addresses if provided
        tunnel_ip = None
        if wan_ip_addresses and len(wan_ip_addresses) > 0:
            tunnel_ip = wan_ip_addresses[0]

        result = niosxaas_client.update_access_location(
            location_id=location_id,
            tunnel_ip=tunnel_ip,
            tunnel_configs=tunnel_configs
        )
        return result
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}


# ==================== Atcfw/DFP (DNS Security) Tools ====================

@mcp.tool()
def list_security_policies(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List DNS security policies (for DFP/threat protection).

    Args:
        name_filter: Filter by policy name
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of security policies

    Examples:
        - list_security_policies() -> All security policies
        - list_security_policies(name_filter="Default") -> Policies with "Default" in name
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        filter_expr = f"name~'{name_filter}'" if name_filter else None
        result = atcfw_client.list_security_policies(filter_expr=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_security_policy(policy_id: str) -> dict:
    """
    Get detailed security policy information.

    Args:
        policy_id: Security policy ID

    Returns:
        Dictionary with policy details including rules and settings

    Examples:
        - get_security_policy("12345") -> Get policy details
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        result = atcfw_client.get_security_policy(policy_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_threat_named_lists(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List custom threat intelligence named lists.

    Args:
        name_filter: Filter by list name
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of named lists

    Examples:
        - list_threat_named_lists() -> All custom threat lists
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        filter_expr = f"name~'{name_filter}'" if name_filter else None
        result = atcfw_client.list_named_lists(filter_expr=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_threat_named_list(
    name: str,
    list_type: str,
    items: Optional[List[str]] = None,
    description: str = ""
) -> dict:
    """
    Create a custom threat intelligence named list.

    Args:
        name: List name
        list_type: List type (e.g., "custom_list")
        items: List of threat indicators (domains, IPs, etc.)
        description: List description

    Returns:
        Dictionary with created list details

    Examples:
        - create_threat_named_list("Blocked Domains", "custom_list", ["malware.com", "phishing.net"])
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        result = atcfw_client.create_named_list(
            name=name,
            type=list_type,
            items=items,
            description=description
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_content_categories() -> dict:
    """
    List available content categories for filtering (Drugs, Pornography, Gambling, etc.).

    Returns:
        Dictionary with list of content categories

    Examples:
        - list_content_categories() -> All available content filter categories
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        result = atcfw_client.list_content_categories()
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_internal_domains(name_filter: Optional[str] = None, limit: int = 100) -> dict:
    """
    List internal domain lists (for internal DNS resolution).

    Args:
        name_filter: Filter by list name
        limit: Maximum number of results (default: 100)

    Returns:
        Dictionary with list of internal domain lists

    Examples:
        - list_internal_domains() -> All internal domain lists
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        filter_expr = f"name~'{name_filter}'" if name_filter else None
        result = atcfw_client.list_internal_domain_lists(filter_expr=filter_expr, limit=limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_internal_domain_list(
    name: str,
    internal_domains: List[str],
    description: str = ""
) -> dict:
    """
    Create an internal domain list.

    Args:
        name: List name
        internal_domains: List of internal domains/CIDRs/IPs
        description: List description

    Returns:
        Dictionary with created list details

    Examples:
        - create_internal_domain_list("Corporate Domains", ["corp.local", "10.0.0.0/8"])
    """
    if not atcfw_client:
        return {"error": "Atcfw client not initialized."}

    try:
        result = atcfw_client.create_internal_domain_list(
            name=name,
            internal_domains=internal_domains,
            description=description
        )
        return result
    except Exception as e:
        return {"error": str(e)}


# ==================== SOC Insights Tools ====================

@mcp.tool()
def list_security_insights(
    status: Optional[str] = None,
    threat_type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List security insights from SOC (Security Operations Center).

    Args:
        status: Filter by insight status - Options: 'OPEN', 'IN_PROGRESS', 'CLOSED', 'RESOLVED'
        threat_type: Filter by threat type - Options: 'malware', 'phishing', 'data_exfiltration', 'ransomware', 'botnet'
        priority: Filter by priority level - Options: 'critical', 'high', 'medium', 'low'
        limit: Maximum number of insights to return (default: 100)

    Returns:
        Dict with security insights including threat context, affected assets, and severity

    Example:
        - list_security_insights(status="OPEN", priority="critical")
        - list_security_insights(threat_type="malware")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.list_insights(
            status=status,
            threat_type=threat_type,
            priority=priority,
            limit=limit
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_security_insight_details(insight_id: str) -> dict:
    """
    Get detailed information for a specific security insight.

    Args:
        insight_id: The unique identifier for the security insight

    Returns:
        Dict with comprehensive insight details including:
        - Threat description and severity
        - Affected assets and indicators
        - Recommended actions
        - Timeline of events

    Example:
        - get_security_insight_details("insight-abc-123")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.get_insight(insight_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def update_security_insight_status(
    insight_ids: List[str],
    status: str,
    comment: Optional[str] = None
) -> dict:
    """
    Update the status of one or more security insights.

    Args:
        insight_ids: List of insight IDs to update (can be single ID in a list)
        status: New status - Options: 'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'FALSE_POSITIVE'
        comment: Optional comment explaining the status change

    Returns:
        Dict with update results and confirmation

    Example:
        - update_security_insight_status(["insight-123"], "RESOLVED", "Malware quarantined and cleaned")
        - update_security_insight_status(["insight-456", "insight-789"], "FALSE_POSITIVE", "Benign traffic")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.update_insight_status(
            insight_ids=insight_ids,
            status=status,
            comment=comment
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_insight_threat_indicators(
    insight_id: str,
    confidence: Optional[str] = None,
    limit: int = 1000
) -> dict:
    """
    Get threat indicators (IOCs - Indicators of Compromise) associated with a security insight.

    Args:
        insight_id: The security insight ID
        confidence: Filter by confidence level - Options: 'high', 'medium', 'low'
        limit: Maximum indicators to return (default: 1000, max: 5000)

    Returns:
        Dict with threat indicators including:
        - Malicious domains, IPs, URLs
        - File hashes (MD5, SHA256)
        - Threat actor information
        - Action taken (blocked/allowed)

    Example:
        - get_insight_threat_indicators("insight-123", confidence="high")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.get_insight_indicators(
            insight_id=insight_id,
            confidence=confidence,
            limit=limit
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_insight_security_events(
    insight_id: str,
    threat_level: Optional[str] = None,
    source_ip: Optional[str] = None,
    device_ip: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 1000
) -> dict:
    """
    Get security events associated with a security insight.

    Args:
        insight_id: The security insight ID
        threat_level: Filter by threat level - Options: 'critical', 'high', 'medium', 'low'
        source_ip: Filter by source IP address (e.g., "192.168.1.100")
        device_ip: Filter by device IP address
        start_time: Start time for event range (ISO 8601 format: "2024-01-01T00:00:00Z")
        end_time: End time for event range (ISO 8601 format)
        limit: Maximum events to return (default: 1000)

    Returns:
        Dict with security events including timestamps, sources, and actions taken

    Example:
        - get_insight_security_events("insight-123", threat_level="high")
        - get_insight_security_events("insight-123", source_ip="10.0.1.50", start_time="2024-01-01T00:00:00Z")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.get_insight_events(
            insight_id=insight_id,
            threat_level=threat_level,
            source_ip=source_ip,
            device_ip=device_ip,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_insight_affected_assets(
    insight_id: str,
    os_version: Optional[str] = None,
    user: Optional[str] = None,
    limit: int = 1000
) -> dict:
    """
    Get affected assets (devices, IPs, MAC addresses) for a security insight.

    Args:
        insight_id: The security insight ID
        os_version: Filter by OS version (e.g., "Windows 10", "macOS 14")
        user: Filter by username
        limit: Maximum assets to return (default: 1000)

    Returns:
        Dict with affected assets including:
        - Device names and IPs
        - MAC addresses
        - OS information
        - User accounts
        - Threat indicators per asset
        - Severity per asset

    Example:
        - get_insight_affected_assets("insight-123")
        - get_insight_affected_assets("insight-123", os_version="Windows 10")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.get_insight_assets(
            insight_id=insight_id,
            os_version=os_version,
            user=user,
            limit=limit
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_insight_comments_history(
    insight_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Get historical comments and status changes for a security insight.

    Args:
        insight_id: The security insight ID
        start_date: Start date for comment range (ISO 8601 format: "2024-01-01T00:00:00Z")
        end_date: End date for comment range (ISO 8601 format)

    Returns:
        Dict with comment history including:
        - User comments
        - Status transitions
        - Timestamps
        - Author information

    Example:
        - get_insight_comments_history("insight-123")
        - get_insight_comments_history("insight-123", start_date="2024-01-01T00:00:00Z")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.get_insight_comments(
            insight_id=insight_id,
            start_date=start_date,
            end_date=end_date
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_policy_analytics_insights(
    status: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List policy analytics insights for configuration compliance.

    Args:
        status: Filter by insight status - Options: 'OPEN', 'RESOLVED', 'CLOSED'
        limit: Maximum insights to return (default: 100)

    Returns:
        Dict with policy analytics insights showing configuration issues and recommendations

    Example:
        - list_policy_analytics_insights(status="OPEN")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.list_analytics_insights(
            status=status,
            limit=limit
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_policy_analytics_insight_details(analytic_insight_id: str) -> dict:
    """
    Get detailed information for a specific policy analytics insight.

    Args:
        analytic_insight_id: The analytics insight ID

    Returns:
        Dict with detailed analytics insight including:
        - Configuration issues
        - Policy violations
        - Recommended remediations
        - Impact analysis

    Example:
        - get_policy_analytics_insight_details("analytics-insight-123")
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.get_analytics_insight(analytic_insight_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_policy_compliance_insights(
    check_type: Optional[str] = None,
    limit: int = 100
) -> dict:
    """
    List policy compliance check insights for security and configuration validation.

    Args:
        check_type: Filter by configuration check type (e.g., "security", "performance", "best_practice")
        limit: Maximum insights to return (default: 100)

    Returns:
        Dict with policy compliance insights showing:
        - Configuration compliance status
        - Failed checks
        - Security vulnerabilities
        - Remediation guidance

    Example:
        - list_policy_compliance_insights(check_type="security")
        - list_policy_compliance_insights()
    """
    if not insights_client:
        return {"error": "Insights client not initialized. Set INFOBLOX_API_KEY."}

    try:
        result = insights_client.list_policy_check_insights(
            check_type=check_type,
            limit=limit
        )
        return result
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Run the MCP server with SSE transport on port 3001
    mcp.run(transport="sse", port=3001)
