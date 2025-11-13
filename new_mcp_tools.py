# NEW MCP TOOLS TO ADD TO mcp_infoblox.py
# This file contains all the new tool definitions
# Copy and paste these into the appropriate sections of mcp_infoblox.py

# ==================== IPAM Host Tools (5 tools) ====================
# Add after list_ip_addresses tool

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


# ==================== DNS Record Tools - Additional Types (6 tools) ====================
# Add after existing create_txt_record tool

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
