#!/usr/bin/env python3
"""
AWS MCP Server - Query AWS resources (VPC, VGW, VPN, etc.) via boto3 (HTTP Transport)

Provides tools to dynamically discover AWS resources instead of hardcoding them.

** This is the spec-compliant HTTP version **
** Original SSE version runs on port 3003 as backup **
"""

import os
import json
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("AWS Tools")

# AWS region - can be overridden via env
DEFAULT_REGION = os.getenv("AWS_REGION", "eu-west-2")


def get_ec2_client(region: Optional[str] = None):
    """Get boto3 EC2 client for specified region"""
    return boto3.client("ec2", region_name=region or DEFAULT_REGION)


@mcp.tool()
def list_vpcs(region: Optional[str] = None) -> Dict[str, Any]:
    """
    List all VPCs in AWS region

    Args:
        region: AWS region (default: eu-west-2)

    Returns:
        Dictionary with VPCs list

    Example:
        list_vpcs()
        list_vpcs(region="us-east-1")

    IMPORTANT - Use Before Creating VPN Infrastructure:
    Before creating VPN infrastructure with create_vpc() or create_vpn_gateway(),
    ALWAYS call this function first to check for existing VPCs that can be reused.

    Present available VPCs to the user and ask if they want to:
    1. Use an existing VPC (provide VpcId for selection)
    2. Create a new VPC

    This prevents unnecessary resource creation and reduces costs.
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_vpcs()

        vpcs = []
        for vpc in response.get("Vpcs", []):
            name = next(
                (tag["Value"] for tag in vpc.get("Tags", []) if tag["Key"] == "Name"),
                "Unnamed"
            )
            vpcs.append({
                "VpcId": vpc["VpcId"],
                "Name": name,
                "CidrBlock": vpc["CidrBlock"],
                "State": vpc["State"],
                "IsDefault": vpc.get("IsDefault", False)
            })

        return {
            "success": True,
            "region": region or DEFAULT_REGION,
            "count": len(vpcs),
            "vpcs": vpcs
        }
    except NoCredentialsError:
        return {"success": False, "error": "AWS credentials not configured"}
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def find_vpc_by_tag(tag_key: str, tag_value: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Find VPC by tag

    Args:
        tag_key: Tag key to search (e.g., "Name")
        tag_value: Tag value to search (e.g., "Production-VPC")
        region: AWS region

    Returns:
        VPC details or error

    Example:
        find_vpc_by_tag("Name", "Production-VPC")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_vpcs(
            Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_value]}]
        )

        vpcs = response.get("Vpcs", [])
        if not vpcs:
            return {
                "success": False,
                "error": f"No VPC found with tag {tag_key}={tag_value}"
            }

        vpc = vpcs[0]
        return {
            "success": True,
            "vpc_id": vpc["VpcId"],
            "cidr_block": vpc["CidrBlock"],
            "state": vpc["State"],
            "is_default": vpc.get("IsDefault", False)
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_vpn_gateways(region: Optional[str] = None) -> Dict[str, Any]:
    """
    List all VPN Gateways (VGWs)

    Args:
        region: AWS region

    Returns:
        List of VPN gateways with details

    Example:
        list_vpn_gateways()

    IMPORTANT - Use Before Creating VPN Infrastructure:
    Before creating VPN infrastructure with create_vpn_gateway(),
    ALWAYS call this function first to check for existing VPN Gateways that can be reused.

    Present available VPN Gateways to the user with their current state and VPC attachments.
    Ask if they want to:
    1. Use an existing VPN Gateway (if state is 'available' or already attached to target VPC)
    2. Create a new VPN Gateway

    Using existing VPN Gateways can:
    - Reduce costs (avoid multiple VGW charges)
    - Reuse existing routing configurations
    - Consolidate VPN connections to the same gateway

    NOTE: A VPN Gateway can only be attached to one VPC at a time.
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_vpn_gateways()

        gateways = []
        for vgw in response.get("VpnGateways", []):
            name = next(
                (tag["Value"] for tag in vgw.get("Tags", []) if tag["Key"] == "Name"),
                "Unnamed"
            )

            attachments = []
            for att in vgw.get("VpcAttachments", []):
                attachments.append({
                    "VpcId": att["VpcId"],
                    "State": att["State"]
                })

            gateways.append({
                "VpnGatewayId": vgw["VpnGatewayId"],
                "Name": name,
                "State": vgw["State"],
                "Type": vgw["Type"],
                "VpcAttachments": attachments
            })

        return {
            "success": True,
            "region": region or DEFAULT_REGION,
            "count": len(gateways),
            "gateways": gateways
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def find_vgw_by_tag(tag_key: str, tag_value: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Find VPN Gateway by tag

    Args:
        tag_key: Tag key (e.g., "Name")
        tag_value: Tag value (e.g., "VGW-Lab")
        region: AWS region

    Returns:
        VGW details

    Example:
        find_vgw_by_tag("Name", "VGW-Lab")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_vpn_gateways(
            Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_value]}]
        )

        gateways = response.get("VpnGateways", [])
        if not gateways:
            return {
                "success": False,
                "error": f"No VGW found with tag {tag_key}={tag_value}"
            }

        vgw = gateways[0]
        return {
            "success": True,
            "vpn_gateway_id": vgw["VpnGatewayId"],
            "state": vgw["State"],
            "type": vgw["Type"],
            "vpc_attachments": vgw.get("VpcAttachments", [])
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_vpn_connections(region: Optional[str] = None) -> Dict[str, Any]:
    """
    List all VPN connections

    Args:
        region: AWS region

    Returns:
        List of VPN connections with tunnel details

    Example:
        list_vpn_connections()
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_vpn_connections()

        connections = []
        for vpn in response.get("VpnConnections", []):
            name = next(
                (tag["Value"] for tag in vpn.get("Tags", []) if tag["Key"] == "Name"),
                vpn["VpnConnectionId"]
            )

            tunnels = []
            for idx, tunnel_opt in enumerate(vpn.get("Options", {}).get("TunnelOptions", []), 1):
                tunnels.append({
                    "tunnel_number": idx,
                    "outside_ip": tunnel_opt.get("OutsideIpAddress"),
                    "inside_cidr": tunnel_opt.get("TunnelInsideCidr"),
                    "preshared_key": tunnel_opt.get("PreSharedKey", "***")
                })

            connections.append({
                "VpnConnectionId": vpn["VpnConnectionId"],
                "Name": name,
                "State": vpn["State"],
                "Type": vpn["Type"],
                "CustomerGatewayId": vpn["CustomerGatewayId"],
                "VpnGatewayId": vpn.get("VpnGatewayId"),
                "Tunnels": tunnels
            })

        return {
            "success": True,
            "region": region or DEFAULT_REGION,
            "count": len(connections),
            "connections": connections
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_vpn_tunnel_ips(vpn_connection_id: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Get VPN tunnel outside IP addresses (for configuring Infoblox)

    Args:
        vpn_connection_id: Specific VPN connection ID (optional - returns all if not specified)
        region: AWS region

    Returns:
        List of tunnel IPs

    Example:
        get_vpn_tunnel_ips()
        get_vpn_tunnel_ips("vpn-12345abcde")
    """
    try:
        ec2 = get_ec2_client(region)

        if vpn_connection_id:
            response = ec2.describe_vpn_connections(VpnConnectionIds=[vpn_connection_id])
        else:
            response = ec2.describe_vpn_connections()

        tunnel_ips = []
        for vpn in response.get("VpnConnections", []):
            vpn_id = vpn["VpnConnectionId"]
            name = next(
                (tag["Value"] for tag in vpn.get("Tags", []) if tag["Key"] == "Name"),
                vpn_id
            )

            for idx, tunnel in enumerate(vpn.get("Options", {}).get("TunnelOptions", []), 1):
                outside_ip = tunnel.get("OutsideIpAddress")
                if outside_ip:
                    tunnel_ips.append({
                        "vpn_connection_id": vpn_id,
                        "vpn_name": name,
                        "tunnel_number": idx,
                        "outside_ip": outside_ip,
                        "inside_cidr": tunnel.get("TunnelInsideCidr")
                    })

        return {
            "success": True,
            "count": len(tunnel_ips),
            "tunnel_ips": tunnel_ips
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_customer_gateways(region: Optional[str] = None) -> Dict[str, Any]:
    """
    List all Customer Gateways

    Args:
        region: AWS region

    Returns:
        List of customer gateways

    Example:
        list_customer_gateways()
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.describe_customer_gateways()

        gateways = []
        for cgw in response.get("CustomerGateways", []):
            name = next(
                (tag["Value"] for tag in cgw.get("Tags", []) if tag["Key"] == "Name"),
                "Unnamed"
            )

            gateways.append({
                "CustomerGatewayId": cgw["CustomerGatewayId"],
                "Name": name,
                "State": cgw["State"],
                "Type": cgw["Type"],
                "IpAddress": cgw["IpAddress"],
                "BgpAsn": cgw["BgpAsn"]
            })

        return {
            "success": True,
            "region": region or DEFAULT_REGION,
            "count": len(gateways),
            "gateways": gateways
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_regions() -> Dict[str, Any]:
    """
    List all available AWS regions

    Returns:
        List of AWS regions

    Example:
        list_regions()
    """
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        response = ec2.describe_regions()

        regions = [
            {
                "RegionName": region["RegionName"],
                "Endpoint": region["Endpoint"]
            }
            for region in response.get("Regions", [])
        ]

        return {
            "success": True,
            "count": len(regions),
            "regions": regions
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


# ========== CREATE/WRITE OPERATIONS ==========

@mcp.tool()
def create_vpc(cidr_block: str, name: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new VPC

    Args:
        cidr_block: CIDR block for VPC (e.g., "10.0.0.0/16")
        name: Name tag for VPC (optional)
        region: AWS region

    Returns:
        VPC details

    Example:
        create_vpc("10.0.0.0/16", "Production-VPC")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.create_vpc(CidrBlock=cidr_block)
        vpc = response["Vpc"]
        vpc_id = vpc["VpcId"]

        # Add name tag if provided
        if name:
            ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": name}])

        return {
            "success": True,
            "vpc_id": vpc_id,
            "cidr_block": vpc["CidrBlock"],
            "state": vpc["State"],
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_subnet(vpc_id: str, cidr_block: str, availability_zone: Optional[str] = None,
                  name: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a subnet in VPC

    Args:
        vpc_id: VPC ID
        cidr_block: Subnet CIDR (e.g., "10.0.1.0/24")
        availability_zone: AZ (e.g., "eu-west-2a") - optional
        name: Name tag (optional)
        region: AWS region

    Returns:
        Subnet details

    Example:
        create_subnet("vpc-123", "10.0.1.0/24", "eu-west-2a", "Public-Subnet")
    """
    try:
        ec2 = get_ec2_client(region)
        params = {"VpcId": vpc_id, "CidrBlock": cidr_block}
        if availability_zone:
            params["AvailabilityZone"] = availability_zone

        response = ec2.create_subnet(**params)
        subnet = response["Subnet"]
        subnet_id = subnet["SubnetId"]

        if name:
            ec2.create_tags(Resources=[subnet_id], Tags=[{"Key": "Name", "Value": name}])

        return {
            "success": True,
            "subnet_id": subnet_id,
            "vpc_id": vpc_id,
            "cidr_block": subnet["CidrBlock"],
            "availability_zone": subnet["AvailabilityZone"],
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_internet_gateway(name: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an Internet Gateway

    Args:
        name: Name tag (optional)
        region: AWS region

    Returns:
        IGW details

    Example:
        create_internet_gateway("Production-IGW")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.create_internet_gateway()
        igw = response["InternetGateway"]
        igw_id = igw["InternetGatewayId"]

        if name:
            ec2.create_tags(Resources=[igw_id], Tags=[{"Key": "Name", "Value": name}])

        return {
            "success": True,
            "internet_gateway_id": igw_id,
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def attach_internet_gateway(igw_id: str, vpc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Attach Internet Gateway to VPC

    Args:
        igw_id: Internet Gateway ID
        vpc_id: VPC ID
        region: AWS region

    Returns:
        Attachment status

    Example:
        attach_internet_gateway("igw-123", "vpc-456")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

        return {
            "success": True,
            "internet_gateway_id": igw_id,
            "vpc_id": vpc_id,
            "message": "IGW attached to VPC successfully"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_route_table(vpc_id: str, name: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a route table

    Args:
        vpc_id: VPC ID
        name: Name tag (optional)
        region: AWS region

    Returns:
        Route table details

    Example:
        create_route_table("vpc-123", "Public-RT")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.create_route_table(VpcId=vpc_id)
        rt = response["RouteTable"]
        rt_id = rt["RouteTableId"]

        if name:
            ec2.create_tags(Resources=[rt_id], Tags=[{"Key": "Name", "Value": name}])

        return {
            "success": True,
            "route_table_id": rt_id,
            "vpc_id": vpc_id,
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_route(route_table_id: str, destination_cidr: str, gateway_id: Optional[str] = None,
                nat_gateway_id: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a route in route table

    Args:
        route_table_id: Route table ID
        destination_cidr: Destination CIDR (e.g., "0.0.0.0/0" for internet)
        gateway_id: Internet Gateway ID (for internet routes)
        nat_gateway_id: NAT Gateway ID (for private subnets)
        region: AWS region

    Returns:
        Route creation status

    Example:
        create_route("rtb-123", "0.0.0.0/0", gateway_id="igw-456")
    """
    try:
        ec2 = get_ec2_client(region)
        params = {"RouteTableId": route_table_id, "DestinationCidrBlock": destination_cidr}

        if gateway_id:
            params["GatewayId"] = gateway_id
        elif nat_gateway_id:
            params["NatGatewayId"] = nat_gateway_id
        else:
            return {"success": False, "error": "Must provide either gateway_id or nat_gateway_id"}

        ec2.create_route(**params)

        return {
            "success": True,
            "route_table_id": route_table_id,
            "destination_cidr": destination_cidr,
            "gateway_id": gateway_id or nat_gateway_id
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def associate_route_table(route_table_id: str, subnet_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Associate route table with subnet

    Args:
        route_table_id: Route table ID
        subnet_id: Subnet ID
        region: AWS region

    Returns:
        Association details

    Example:
        associate_route_table("rtb-123", "subnet-456")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.associate_route_table(RouteTableId=route_table_id, SubnetId=subnet_id)

        return {
            "success": True,
            "association_id": response["AssociationId"],
            "route_table_id": route_table_id,
            "subnet_id": subnet_id
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_vpn_gateway(name: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a VPN Gateway (VGW)

    Args:
        name: Name tag (optional)
        region: AWS region

    Returns:
        VGW details

    Example:
        create_vpn_gateway("VGW-Lab")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.create_vpn_gateway(Type="ipsec.1")
        vgw = response["VpnGateway"]
        vgw_id = vgw["VpnGatewayId"]

        if name:
            ec2.create_tags(Resources=[vgw_id], Tags=[{"Key": "Name", "Value": name}])

        return {
            "success": True,
            "vpn_gateway_id": vgw_id,
            "state": vgw["State"],
            "type": vgw["Type"],
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def attach_vpn_gateway(vgw_id: str, vpc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Attach VPN Gateway to VPC

    Args:
        vgw_id: VPN Gateway ID
        vpc_id: VPC ID
        region: AWS region

    Returns:
        Attachment details

    Example:
        attach_vpn_gateway("vgw-123", "vpc-456")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.attach_vpn_gateway(VpnGatewayId=vgw_id, VpcId=vpc_id)

        return {
            "success": True,
            "vpn_gateway_id": vgw_id,
            "vpc_id": vpc_id,
            "state": response["VpcAttachment"]["State"]
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_customer_gateway(ip_address: str, bgp_asn: int = 65000, name: Optional[str] = None,
                            region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a Customer Gateway (CGW)

    Args:
        ip_address: Public IP of customer gateway
        bgp_asn: BGP ASN number (default: 65000)
        name: Name tag (optional)
        region: AWS region

    Returns:
        CGW details

    Example:
        create_customer_gateway("203.0.113.12", 65000, "CGW-Office")
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.create_customer_gateway(
            BgpAsn=bgp_asn,
            PublicIp=ip_address,
            Type="ipsec.1"
        )
        cgw = response["CustomerGateway"]
        cgw_id = cgw["CustomerGatewayId"]

        if name:
            ec2.create_tags(Resources=[cgw_id], Tags=[{"Key": "Name", "Value": name}])

        return {
            "success": True,
            "customer_gateway_id": cgw_id,
            "state": cgw["State"],
            "ip_address": cgw["IpAddress"],
            "bgp_asn": cgw["BgpAsn"],
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_vpn_connection(cgw_id: str, vgw_id: str, preshared_key: str,
                         tunnel_inside_cidr: str, name: Optional[str] = None,
                         region: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a VPN Connection

    Args:
        cgw_id: Customer Gateway ID
        vgw_id: VPN Gateway ID
        preshared_key: Pre-shared key for VPN
        tunnel_inside_cidr: Inside CIDR for tunnel (e.g., "169.254.21.0/30")
        name: Name tag (optional)
        region: AWS region

    Returns:
        VPN connection details with tunnel IPs

    Example:
        create_vpn_connection("cgw-123", "vgw-456", "MySecretKey123", "169.254.21.0/30", "VPN-Primary")

    🚨 CRITICAL - AFTER ALL VPN CONNECTIONS ARE CREATED:
    After you create ALL VPN connections (typically 2: primary and secondary), you MUST:

    1. Extract the tunnel outside IPs from each VPN connection
    2. Update the Infoblox access location with these AWS tunnel IPs

    Tell the user:
    "🔗 FINAL STEP - Update Infoblox with AWS Tunnel IPs:
    I've created the AWS VPN connections. Now I need to update your Infoblox access location
    with the AWS tunnel outside IPs so the tunnels can establish connections.

    AWS Tunnel IPs to configure:
    - Primary: [list IPs]
    - Secondary: [list IPs]

    Would you like me to update the Infoblox configuration now?"

    Then use the Infoblox configure_vpn_infrastructure tool with UPDATE operation to update
    the access_location physical_tunnels with the AWS tunnel outside IPs.
    """
    try:
        ec2 = get_ec2_client(region)
        response = ec2.create_vpn_connection(
            CustomerGatewayId=cgw_id,
            Type="ipsec.1",
            VpnGatewayId=vgw_id,
            Options={
                "StaticRoutesOnly": False,
                "TunnelOptions": [{
                    "TunnelInsideCidr": tunnel_inside_cidr,
                    "PreSharedKey": preshared_key,
                    "StartupAction": "start"
                }]
            }
        )
        vpn = response["VpnConnection"]
        vpn_id = vpn["VpnConnectionId"]

        if name:
            ec2.create_tags(Resources=[vpn_id], Tags=[{"Key": "Name", "Value": name}])

        # Extract tunnel info
        tunnels = []
        for idx, tunnel_opt in enumerate(vpn.get("Options", {}).get("TunnelOptions", []), 1):
            tunnels.append({
                "tunnel_number": idx,
                "outside_ip": tunnel_opt.get("OutsideIpAddress"),
                "inside_cidr": tunnel_opt.get("TunnelInsideCidr")
            })

        return {
            "success": True,
            "vpn_connection_id": vpn_id,
            "state": vpn["State"],
            "customer_gateway_id": cgw_id,
            "vpn_gateway_id": vgw_id,
            "tunnels": tunnels,
            "name": name or "Unnamed"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def enable_vgw_route_propagation(route_table_id: str, vgw_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Enable VPN Gateway route propagation on route table

    Args:
        route_table_id: Route table ID
        vgw_id: VPN Gateway ID
        region: AWS region

    Returns:
        Status

    Example:
        enable_vgw_route_propagation("rtb-123", "vgw-456")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.enable_vgw_route_propagation(RouteTableId=route_table_id, GatewayId=vgw_id)

        return {
            "success": True,
            "route_table_id": route_table_id,
            "vpn_gateway_id": vgw_id,
            "message": "VGW route propagation enabled"
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def detach_internet_gateway(igw_id: str, vpc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Detach an Internet Gateway from a VPC

    Args:
        igw_id: Internet Gateway ID (e.g., "igw-123")
        vpc_id: VPC ID (e.g., "vpc-456")
        region: AWS region

    Returns:
        Detachment confirmation

    Example:
        detach_internet_gateway("igw-035c7f1eca9a7662e", "vpc-02b11bdb691778d2b", "eu-central-1")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

        return {
            "success": True,
            "igw_id": igw_id,
            "vpc_id": vpc_id,
            "message": f"IGW {igw_id} detached from VPC {vpc_id}",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def detach_vpn_gateway(vgw_id: str, vpc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Detach a VPN Gateway from a VPC

    Args:
        vgw_id: VPN Gateway ID (e.g., "vgw-123")
        vpc_id: VPC ID (e.g., "vpc-456")
        region: AWS region

    Returns:
        Detachment confirmation

    Example:
        detach_vpn_gateway("vgw-0c876eabba0726d1c", "vpc-02b11bdb691778d2b", "eu-central-1")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.detach_vpn_gateway(VpnGatewayId=vgw_id, VpcId=vpc_id)

        return {
            "success": True,
            "vgw_id": vgw_id,
            "vpc_id": vpc_id,
            "message": f"VGW {vgw_id} detached from VPC {vpc_id}",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def disassociate_route_table(association_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Disassociate a route table from a subnet

    Args:
        association_id: Route table association ID (e.g., "rtbassoc-123")
        region: AWS region

    Returns:
        Disassociation confirmation

    Example:
        disassociate_route_table("rtbassoc-0abcdef1234567890")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.disassociate_route_table(AssociationId=association_id)

        return {
            "success": True,
            "association_id": association_id,
            "message": f"Route table association {association_id} removed",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_subnet(subnet_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a subnet

    Args:
        subnet_id: Subnet ID (e.g., "subnet-123")
        region: AWS region

    Returns:
        Deletion confirmation

    Example:
        delete_subnet("subnet-034ebc526c3be61fc", "eu-central-1")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.delete_subnet(SubnetId=subnet_id)

        return {
            "success": True,
            "subnet_id": subnet_id,
            "message": f"Subnet {subnet_id} deleted",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_internet_gateway(igw_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete an Internet Gateway (must be detached first)

    Args:
        igw_id: Internet Gateway ID (e.g., "igw-123")
        region: AWS region

    Returns:
        Deletion confirmation

    Example:
        delete_internet_gateway("igw-035c7f1eca9a7662e", "eu-central-1")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)

        return {
            "success": True,
            "igw_id": igw_id,
            "message": f"Internet Gateway {igw_id} deleted",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_route_table(route_table_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a route table (cannot delete main route table)

    Args:
        route_table_id: Route table ID (e.g., "rtb-123")
        region: AWS region

    Returns:
        Deletion confirmation

    Example:
        delete_route_table("rtb-07809f4979c52424d", "eu-central-1")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.delete_route_table(RouteTableId=route_table_id)

        return {
            "success": True,
            "route_table_id": route_table_id,
            "message": f"Route table {route_table_id} deleted",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_vpc(vpc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a VPC (all dependencies must be removed first)

    Args:
        vpc_id: VPC ID (e.g., "vpc-123")
        region: AWS region

    Returns:
        Deletion confirmation

    Example:
        delete_vpc("vpc-02b11bdb691778d2b", "eu-central-1")
    """
    try:
        ec2 = get_ec2_client(region)
        ec2.delete_vpc(VpcId=vpc_id)

        return {
            "success": True,
            "vpc_id": vpc_id,
            "message": f"VPC {vpc_id} deleted successfully",
            "region": region or DEFAULT_REGION
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run the MCP server with HTTP transport (spec-compliant)
    print("🚀 Starting AWS Tools MCP Server (HTTP Transport)")
    print("📍 Endpoint: http://127.0.0.1:4003/mcp")
    print("✅ Spec-compliant streamable HTTP transport")
    print("🔄 Backup SSE version still running on port 3003")
    print("🛠️  27 tools for VPC, VGW, VPN, Subnets, and Security Groups")

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=4003,
        path="/mcp"
    )
