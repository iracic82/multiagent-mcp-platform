"""
AWS CloudControl API MCP Server Wrapper (HTTP Transport)
Provides simplified AWS CloudControl API access via FastMCP
Uses boto3 cloudcontrol client directly for better integration

** This is the spec-compliant HTTP version **
** Original SSE version runs on port 3004 as backup **
"""

import os
import json
import boto3
from typing import Any, Dict, Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("AWS CloudControl API")

# Initialize boto3 CloudControl client
def get_cloudcontrol_client(region: Optional[str] = None):
    """
    Get boto3 CloudControl client with specified or default region

    Args:
        region: AWS region (e.g., 'eu-central-1', 'us-east-1').
                If None, uses AWS_REGION env var or defaults to 'eu-west-2'
    """
    if region is None:
        region = os.getenv("AWS_REGION", "eu-west-2")
    return boto3.client('cloudcontrol', region_name=region)


@mcp.tool()
def cloudcontrol_create_resource(
    resource_type: str,
    desired_state: str,
    client_token: Optional[str] = None,
    region: Optional[str] = None
) -> str:
    """
    Create an AWS resource using Cloud Control API.

    Args:
        resource_type: AWS resource type (e.g., "AWS::EC2::VPC", "AWS::EC2::Subnet")
        desired_state: JSON string with resource configuration
        client_token: Optional idempotency token
        region: AWS region (e.g., "eu-central-1", "us-east-1"). If None, uses default region.

    Returns:
        Resource creation result with identifier and progress token

    Examples:
        - VPC: resource_type="AWS::EC2::VPC", desired_state='{"CidrBlock": "10.0.0.0/16"}'
        - Subnet in specific region: resource_type="AWS::EC2::Subnet", desired_state='{"VpcId": "vpc-xxx", "CidrBlock": "10.0.1.0/24"}', region="eu-central-1"
    """
    try:
        client = get_cloudcontrol_client(region)
        params = {
            "TypeName": resource_type,
            "DesiredState": desired_state
        }
        if client_token:
            params["ClientToken"] = client_token

        response = client.create_resource(**params)
        return json.dumps({
            "identifier": response.get("ProgressEvent", {}).get("Identifier"),
            "operation_status": response.get("ProgressEvent", {}).get("OperationStatus"),
            "request_token": response.get("ProgressEvent", {}).get("RequestToken"),
            "resource_model": response.get("ProgressEvent", {}).get("ResourceModel"),
            "region": region or os.getenv("AWS_REGION", "eu-west-2")
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2)


@mcp.tool()
def cloudcontrol_delete_resource(
    resource_type: str,
    identifier: str,
    region: Optional[str] = None
) -> str:
    """
    Delete an AWS resource using Cloud Control API.

    Args:
        resource_type: AWS resource type (e.g., "AWS::EC2::VPC", "AWS::EC2::VPNGateway")
        identifier: Resource identifier (e.g., "vpc-0123456789abcdef0", "vgw-abc123")
        region: AWS region (e.g., "eu-central-1", "us-east-1"). If None, uses default region.

    Returns:
        Deletion confirmation with status

    Examples:
        - Delete VPC in default region: resource_type="AWS::EC2::VPC", identifier="vpc-0123456789abcdef0"
        - Delete VGW in eu-central-1: resource_type="AWS::EC2::VPNGateway", identifier="vgw-abc123", region="eu-central-1"
    """
    try:
        client = get_cloudcontrol_client(region)
        response = client.delete_resource(
            TypeName=resource_type,
            Identifier=identifier
        )
        region_info = f" in {region}" if region else ""
        return json.dumps({
            "operation_status": response.get("ProgressEvent", {}).get("OperationStatus"),
            "request_token": response.get("ProgressEvent", {}).get("RequestToken"),
            "message": f"Deletion initiated for {identifier}{region_info}",
            "region": region or os.getenv("AWS_REGION", "eu-west-2")
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2)


@mcp.tool()
def cloudcontrol_get_resource(
    resource_type: str,
    identifier: str,
    region: Optional[str] = None
) -> str:
    """
    Get details of an AWS resource using Cloud Control API.

    Args:
        resource_type: AWS resource type (e.g., "AWS::EC2::VPC")
        identifier: Resource identifier (e.g., "vpc-0123456789abcdef0")

    Returns:
        Complete resource details as JSON

    Example:
        resource_type="AWS::EC2::VPC", identifier="vpc-0123456789abcdef0"
    """
    try:
        client = get_cloudcontrol_client(region)
        response = client.get_resource(
            TypeName=resource_type,
            Identifier=identifier
        )
        resource_desc = response.get("ResourceDescription", {})
        return json.dumps({
            "identifier": resource_desc.get("Identifier"),
            "properties": json.loads(resource_desc.get("Properties", "{}")),
            "resource_type": resource_type
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2)


@mcp.tool()
def cloudcontrol_list_resources(
    resource_type: str,
    region: Optional[str] = None,
    max_results: int = 20
) -> str:
    """
    List AWS resources of a specific type using Cloud Control API.

    Args:
        resource_type: AWS resource type (e.g., "AWS::EC2::VPC", "AWS::EC2::Subnet")
        max_results: Maximum number of results to return (default: 20, max: 100)

    Returns:
        List of resource identifiers and basic information

    Example:
        resource_type="AWS::EC2::VPC" - Lists all VPCs in the region
    """
    try:
        client = get_cloudcontrol_client(region)
        response = client.list_resources(
            TypeName=resource_type,
            MaxResults=min(max_results, 100)
        )

        resources = []
        for item in response.get("ResourceDescriptions", []):
            try:
                props = json.loads(item.get("Properties", "{}"))
                resources.append({
                    "identifier": item.get("Identifier"),
                    "properties": props
                })
            except:
                resources.append({
                    "identifier": item.get("Identifier"),
                    "properties_raw": item.get("Properties")
                })

        return json.dumps({
            "resource_type": resource_type,
            "count": len(resources),
            "resources": resources,
            "next_token": response.get("NextToken")
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2)


@mcp.tool()
def cloudcontrol_update_resource(
    resource_type: str,
    identifier: str,
    patch_document: str,
    region: Optional[str] = None
) -> str:
    """
    Update an AWS resource using Cloud Control API.

    Args:
        resource_type: AWS resource type (e.g., "AWS::EC2::VPC")
        identifier: Resource identifier
        patch_document: JSON Patch document as string (e.g., '[{"op": "replace", "path": "/Tags", "value": [...]}]')

    Returns:
        Update status and request token

    Example:
        patch_document='[{"op": "add", "path": "/Tags/-", "value": {"Key": "Env", "Value": "Prod"}}]'
    """
    try:
        client = get_cloudcontrol_client(region)
        response = client.update_resource(
            TypeName=resource_type,
            Identifier=identifier,
            PatchDocument=patch_document
        )
        return json.dumps({
            "operation_status": response.get("ProgressEvent", {}).get("OperationStatus"),
            "request_token": response.get("ProgressEvent", {}).get("RequestToken"),
            "identifier": identifier
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2)


@mcp.tool()
def cloudcontrol_get_resource_request_status(
    request_token: str,
    region: Optional[str] = None
) -> str:
    """
    Check the status of a CloudControl resource operation (create, update, delete).

    Args:
        request_token: The request token returned from create/update/delete operations

    Returns:
        Current status of the operation including any errors

    Use this to poll for completion after initiating create/update/delete operations.
    """
    try:
        client = get_cloudcontrol_client(region)
        response = client.get_resource_request_status(
            RequestToken=request_token
        )
        progress = response.get("ProgressEvent", {})
        return json.dumps({
            "operation_status": progress.get("OperationStatus"),
            "status_message": progress.get("StatusMessage"),
            "error_code": progress.get("ErrorCode"),
            "identifier": progress.get("Identifier"),
            "operation": progress.get("Operation"),
            "resource_model": progress.get("ResourceModel")
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2)


if __name__ == "__main__":
    # Run the MCP server with HTTP transport (spec-compliant)
    print("🚀 Starting AWS CloudControl API MCP Server (HTTP Transport)")
    print("📍 Endpoint: http://127.0.0.1:4004/mcp")
    print("✅ Spec-compliant streamable HTTP transport")
    print("🔄 Backup SSE version still running on port 3004")
    print("🛠️  6 tools for universal AWS resource management")

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=4004,
        path="/mcp"
    )
