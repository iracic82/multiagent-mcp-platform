"""
IPAM Client for Infoblox Universal DDI / BloxOne API

This client handles authentication and communication with IPAM systems.
Supports: Infoblox BloxOne DDI, Universal DDI, and other IPAM solutions.
"""

import httpx
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv

load_dotenv()


class IPAMClient:
    """
    Client for interacting with IPAM (IP Address Management) systems.

    Primarily designed for Infoblox Universal DDI / BloxOne API, but can be
    adapted for other IPAM solutions.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize IPAM client.

        Args:
            base_url: IPAM API base URL (e.g., "https://csp.infoblox.com/api/ddi/v1")
            api_key: API key for authentication
            timeout: HTTP request timeout in seconds
        """
        self.base_url = base_url or os.getenv("IPAM_BASE_URL", "https://csp.infoblox.com/api/ddi/v1")
        self.api_key = api_key or os.getenv("IPAM_API_KEY")

        if not self.api_key:
            raise ValueError("IPAM API key is required. Set IPAM_API_KEY environment variable.")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout
        )

    async def list_subnets(
        self,
        space: Optional[str] = None,
        filter_query: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List IP subnets from IPAM.

        Args:
            space: IP space name to filter by
            filter_query: Additional filter query (e.g., "address>'10.0.0.0'")
            limit: Maximum number of results

        Returns:
            List of subnet dictionaries
        """
        params = {"_limit": limit}

        if space:
            params["space"] = space
        if filter_query:
            params["_filter"] = filter_query

        response = await self.client.get("/ipam/subnet", params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    async def get_subnet(self, subnet_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific subnet.

        Args:
            subnet_id: Subnet identifier

        Returns:
            Subnet details dictionary
        """
        response = await self.client.get(f"/ipam/subnet/{subnet_id}")
        response.raise_for_status()
        return response.json()

    async def search_subnets(
        self,
        cidr: Optional[str] = None,
        address: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for subnets by various criteria.

        Args:
            cidr: CIDR notation to search for (e.g., "192.168.1.0/24")
            address: IP address to find containing subnet
            tag: Tag to filter by

        Returns:
            List of matching subnets
        """
        filters = []

        if cidr:
            filters.append(f"address=='{cidr}'")
        if address:
            filters.append(f"address=='{address}'")
        if tag:
            filters.append(f"tags~'{tag}'")

        filter_query = " and ".join(filters) if filters else None
        return await self.list_subnets(filter_query=filter_query)

    async def get_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """
        Get information about a specific IP address.

        Args:
            ip_address: IP address to query (e.g., "192.168.1.10")

        Returns:
            IP address details including allocation status, usage, etc.
        """
        # Search for IP address
        response = await self.client.get(
            "/ipam/address",
            params={"_filter": f"address=='{ip_address}'"}
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if results:
            return results[0]
        else:
            return {
                "address": ip_address,
                "state": "available",
                "usage": []
            }

    async def allocate_next_ip(
        self,
        subnet_id: str,
        hostname: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Allocate the next available IP address from a subnet.

        Args:
            subnet_id: Subnet to allocate from
            hostname: Optional hostname to associate
            comment: Optional comment/description

        Returns:
            Allocated IP address details
        """
        payload = {
            "subnet": subnet_id
        }

        if hostname:
            payload["names"] = [{"name": hostname, "type": "hostname"}]
        if comment:
            payload["comment"] = comment

        response = await self.client.post("/ipam/address", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_subnet_utilization(
        self,
        subnet_id: Optional[str] = None,
        cidr: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get utilization statistics for a subnet.

        Args:
            subnet_id: Subnet identifier
            cidr: Subnet CIDR (alternative to subnet_id)

        Returns:
            Utilization data including total, used, and available IPs
        """
        if not subnet_id and not cidr:
            raise ValueError("Either subnet_id or cidr must be provided")

        if cidr and not subnet_id:
            # Find subnet by CIDR first
            subnets = await self.search_subnets(cidr=cidr)
            if not subnets:
                raise ValueError(f"Subnet {cidr} not found")
            subnet_id = subnets[0].get("id")

        # Get subnet details
        subnet = await self.get_subnet(subnet_id)

        # Extract utilization info
        utilization = subnet.get("utilization", {})

        return {
            "subnet": subnet.get("address"),
            "space": subnet.get("space"),
            "total_ips": utilization.get("total", 0),
            "used_ips": utilization.get("used", 0),
            "available_ips": utilization.get("available", 0),
            "utilization_percent": utilization.get("utilization", 0),
            "dhcp_free": utilization.get("dhcp_free", 0),
            "dhcp_total": utilization.get("dhcp_total", 0)
        }

    async def list_ip_spaces(self) -> List[Dict[str, Any]]:
        """
        List all IP spaces in IPAM.

        Returns:
            List of IP space dictionaries
        """
        response = await self.client.get("/ipam/ip_space")
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    async def search_available_subnets(
        self,
        size: int,
        space: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find available subnets of a specific size.

        Args:
            size: Subnet size (e.g., 24 for /24)
            space: IP space to search in

        Returns:
            List of available subnets
        """
        params = {
            "_filter": f"cidr=={size}",
            "_limit": 50
        }

        if space:
            params["space"] = space

        response = await self.client.get("/ipam/subnet", params=params)
        response.raise_for_status()

        data = response.json()
        subnets = data.get("results", [])

        # Filter to only include subnets with low utilization
        available = [
            s for s in subnets
            if s.get("utilization", {}).get("utilization", 100) < 80
        ]

        return available

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
_ipam_client_instance: Optional[IPAMClient] = None


def get_ipam_client() -> IPAMClient:
    """Get or create the global IPAM client instance"""
    global _ipam_client_instance
    if _ipam_client_instance is None:
        _ipam_client_instance = IPAMClient()
    return _ipam_client_instance
