"""
NIOSXaaS (NIOS as a Service) API Client
Handles Universal Service (VPN) provisioning via Infoblox NIOSXaaS API
API Docs: https://csp.infoblox.com/apidoc/docs/NIOSXasaService
"""

import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class NIOSXaaSClient:
    """Client for Infoblox NIOSXaaS API - Universal Service / VPN Management"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize NIOSXaaS API client

        Args:
            api_key: Infoblox API key (defaults to INFOBLOX_API_KEY env var)
            base_url: Base URL for API (defaults to https://csp.infoblox.com)
        """
        self.api_key = api_key or os.getenv("INFOBLOX_API_KEY")
        self.base_url = (base_url or os.getenv("INFOBLOX_BASE_URL", "https://csp.infoblox.com")).rstrip("/")

        if not self.api_key:
            raise ValueError("INFOBLOX_API_KEY environment variable or api_key parameter is required")

        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session.headers.update(self.headers)

    # ==================== Universal Services ====================

    def list_universal_services(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List all universal services"""
        url = f"{self.base_url}/api/universalinfra/v1/universalservices"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_universal_service(self, name: str, description: str = "",
                                 capabilities: Optional[List[Dict]] = None,
                                 tags: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new universal service"""
        url = f"{self.base_url}/api/universalinfra/v1/universalservices"
        payload = {
            "name": name,
            "description": description,
            "capabilities": capabilities or [],
            "tags": tags or {}
        }

        r = self.session.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def get_universal_service(self, service_id: str) -> Dict[str, Any]:
        """Get universal service by ID"""
        url = f"{self.base_url}/api/universalinfra/v1/universalservices/{service_id}"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def update_universal_service(self, service_id: str, **kwargs) -> Dict[str, Any]:
        """Update universal service"""
        url = f"{self.base_url}/api/universalinfra/v1/universalservices/{service_id}"
        r = self.session.put(url, headers=self.headers, json=kwargs)
        r.raise_for_status()
        return r.json()

    def delete_universal_service(self, service_id: str) -> Dict[str, Any]:
        """Delete universal service"""
        url = f"{self.base_url}/api/universalinfra/v1/universalservices/{service_id}"
        r = self.session.delete(url, headers=self.headers)
        r.raise_for_status()
        return {"status": "deleted", "id": service_id}

    # ==================== Endpoints ====================

    def list_endpoints(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List all endpoints"""
        url = f"{self.base_url}/api/universalinfra/v1/endpoints"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_endpoint(self, name: str, service_location: str, service_ip: str,
                       universal_service_id: str, size: str, neighbour_ips: List[str],
                       routing_config: Dict, preferred_provider: str = "AWS",
                       routing_type: str = "dynamic", tags: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new endpoint"""
        url = f"{self.base_url}/api/universalinfra/v1/endpoints"
        payload = {
            "name": name,
            "service_location": service_location,
            "service_ip": service_ip,
            "universal_service_id": universal_service_id,
            "size": size,
            "neighbour_ips": neighbour_ips,
            "routing_config": routing_config,
            "preferred_provider": preferred_provider,
            "routing_type": routing_type,
            "tags": tags or {}
        }

        r = self.session.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def get_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Get endpoint by ID"""
        url = f"{self.base_url}/api/universalinfra/v1/endpoints/{endpoint_id}"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def update_endpoint(self, endpoint_id: str, **kwargs) -> Dict[str, Any]:
        """Update endpoint"""
        url = f"{self.base_url}/api/universalinfra/v1/endpoints/{endpoint_id}"
        r = self.session.put(url, headers=self.headers, json=kwargs)
        r.raise_for_status()
        return r.json()

    def delete_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Delete endpoint"""
        url = f"{self.base_url}/api/universalinfra/v1/endpoints/{endpoint_id}"
        r = self.session.delete(url, headers=self.headers)
        r.raise_for_status()
        return {"status": "deleted", "id": endpoint_id}

    # ==================== Access Locations ====================

    def list_access_locations(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List all access locations"""
        url = f"{self.base_url}/api/universalinfra/v1/accesslocations"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_access_location(self, endpoint_id: str, location_id: str,
                              credential_id: str, wan_ip_addresses: List[str],
                              cloud_type: str = "AWS", routing_type: str = "dynamic",
                              tunnel_configs: Optional[List[Dict]] = None,
                              tags: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new access location"""
        url = f"{self.base_url}/api/universalinfra/v1/accesslocations"
        payload = {
            "endpoint_id": endpoint_id,
            "location_id": location_id,
            "credential_id": credential_id,
            "wan_ip_addresses": wan_ip_addresses,
            "cloud_type": cloud_type,
            "routing_type": routing_type,
            "tunnel_configs": tunnel_configs or [],
            "tags": tags or {}
        }

        r = self.session.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def get_access_location(self, location_id: str) -> Dict[str, Any]:
        """Get access location by ID"""
        url = f"{self.base_url}/api/universalinfra/v1/accesslocations/{location_id}"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def update_access_location(self, location_id: str, tunnel_ip: Optional[str] = None,
                               tunnel_configs: Optional[List[dict]] = None) -> Dict[str, Any]:
        """
        Update access location tunnel IPs using consolidated/configure endpoint.
        This is the correct way to update VPN tunnel IPs after AWS VPN creation.

        Args:
            location_id: Access location ID (short form, e.g., 'm7m2bbbtfctnlnvrndxhc2n5z5tqhrqj')
            tunnel_ip: Primary tunnel IP to update (for simple single-tunnel update)
            tunnel_configs: Full tunnel configuration (for advanced updates)

        Returns:
            Dictionary with update result from consolidated/configure endpoint
        """
        # Get current access location details
        access_url = f"{self.base_url}/api/universalinfra/v1/accesslocations"
        r = self.session.get(access_url, headers=self.headers)
        r.raise_for_status()
        access_locations = r.json().get("results", [])

        # Find matching access location
        access_loc = None
        for loc in access_locations:
            loc_id = loc.get("id", "").split("/")[-1]
            if loc_id == location_id or loc.get("id") == location_id:
                access_loc = loc
                break

        if not access_loc:
            return {"error": f"Access location {location_id} not found"}

        # Get endpoint details
        endpoint_id = access_loc.get("endpoint_id")
        endpoint_url = f"{self.base_url}/api/universalinfra/v1/endpoints"
        r = self.session.get(endpoint_url, headers=self.headers)
        r.raise_for_status()
        endpoints = r.json().get("results", [])

        endpoint = None
        for ep in endpoints:
            ep_id = ep.get("id", "").split("/")[-1]
            if ep_id == endpoint_id or ep.get("id") == endpoint_id:
                endpoint = ep
                break

        if not endpoint:
            return {"error": f"Endpoint {endpoint_id} not found"}

        # Get universal service ID and current capabilities
        usvc_id = endpoint.get("universal_service_id")
        usvc_url = f"{self.base_url}/api/universalinfra/v1/universal_services/{usvc_id}"
        r = self.session.get(usvc_url, headers=self.headers)
        r.raise_for_status()
        usvc = r.json().get("result", {})

        # Extract current capabilities or use defaults
        current_caps = usvc.get("capabilities", [])
        dns_profile_id = ""
        dfp_profile_id = ""

        for cap in current_caps:
            if cap.get("type") == "dns":
                dns_profile_id = cap.get("profile_id", "")
            elif cap.get("type") == "dfp":
                dfp_profile_id = cap.get("profile_id", "")

        # If no DFP profile, get default security policy
        if not dfp_profile_id:
            try:
                sec_policies_url = f"{self.base_url}/api/atcfw/v1/security_policies"
                r = self.session.get(sec_policies_url, headers=self.headers, params={"_fields": "id,name,is_default"})
                r.raise_for_status()
                for policy in r.json().get("results", []):
                    if policy.get("is_default"):
                        dfp_profile_id = str(policy.get("id"))
                        break
                if not dfp_profile_id and r.json().get("results"):
                    dfp_profile_id = str(r.json()["results"][0]["id"])
            except:
                pass  # If we can't get security policy, try without it

        # Build tunnel configs - update primary tunnel IP if provided
        tunnels = access_loc.get("tunnel_configs", [])
        if tunnel_ip and len(tunnels) > 0:
            # Update primary tunnel with new IP
            pri_tunnel = tunnels[0]
            if "physical_tunnels" in pri_tunnel and len(pri_tunnel["physical_tunnels"]) > 0:
                pri_tunnel["physical_tunnels"][0]["access_ip"] = tunnel_ip
        elif tunnel_configs:
            tunnels = tunnel_configs

        # Build consolidated/configure payload
        payload = {
            "universal_service": {
                "operation": "UPDATE",
                "id": usvc_id,
                "name": usvc.get("name", ""),
                "description": usvc.get("description", ""),
                "capabilities": [
                    {"type": "dns", "profile_id": dns_profile_id},
                    {"type": "dfp", "profile_id": dfp_profile_id}
                ] if dfp_profile_id else [{"type": "dns", "profile_id": dns_profile_id}],
                "tags": usvc.get("tags", {})
            },
            "access_locations": {
                "create": [],
                "update": [{
                    "endpoint_id": endpoint_id.split("/")[-1] if "/" in str(endpoint_id) else endpoint_id,
                    "id": location_id.split("/")[-1] if "/" in str(location_id) else location_id,
                    "routing_type": access_loc.get("routing_type", "dynamic"),
                    "type": access_loc.get("type", "Cloud VPN"),
                    "name": access_loc.get("name", ""),
                    "cloud_type": access_loc.get("cloud_type", "AWS"),
                    "cloud_region": access_loc.get("cloud_region", ""),
                    "lan_subnets": access_loc.get("lan_subnets", []),
                    "tunnel_configs": tunnels
                }],
                "delete": []
            },
            "endpoints": {
                "create": [],
                "update": [{
                    "id": endpoint_id.split("/")[-1] if "/" in str(endpoint_id) else endpoint_id,
                    "name": endpoint.get("name", ""),
                    "size": endpoint.get("size", "S"),
                    "service_location": endpoint.get("service_location", ""),
                    "service_ip": endpoint.get("service_ip", ""),
                    "neighbour_ips": endpoint.get("neighbour_ips", []),
                    "preferred_provider": endpoint.get("preferred_provider", "AWS"),
                    "tags": endpoint.get("tags", {}),
                    "routing_type": endpoint.get("routing_type", "dynamic"),
                    "routing_config": endpoint.get("routing_config", {})
                }],
                "delete": []
            },
            "credentials": {"create": [], "update": []},
            "locations": {"create": [], "update": []}
        }

        # Call consolidated/configure endpoint
        config_url = f"{self.base_url}/api/universalinfra/v1/consolidated/configure"
        r = self.session.post(config_url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def delete_access_location(self, location_id: str) -> Dict[str, Any]:
        """Delete access location"""
        url = f"{self.base_url}/api/universalinfra/v1/accesslocations/{location_id}"
        r = self.session.delete(url, headers=self.headers)
        r.raise_for_status()
        return {"status": "deleted", "id": location_id}

    # ==================== Helpers ====================

    def list_supported_sizes(self) -> Dict[str, Any]:
        """List supported endpoint sizes"""
        url = f"{self.base_url}/api/universalinfra/v1/supportedsizes"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def list_cloud_provider_regions(self, provider: str = "AWS") -> Dict[str, Any]:
        """List available regions for cloud provider"""
        url = f"{self.base_url}/api/universalinfra/v1/cloudproviderregions"
        payload = {"provider": provider}
        r = self.session.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def list_capabilities(self) -> Dict[str, Any]:
        """List available service capabilities"""
        url = f"{self.base_url}/api/universalinfra/v1/capabilities"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    # ==================== Credentials (IAM API) ====================

    def list_credentials(self, name_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        List all credentials via IAM API.

        Args:
            name_filter: Optional name filter (partial match)

        Returns:
            Dictionary with 'results' containing list of credentials
        """
        url = f"{self.base_url}/api/iam/v2/keys"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()

        result = r.json()

        # Apply name filter if provided
        if name_filter and "results" in result:
            result["results"] = [
                cred for cred in result["results"]
                if name_filter.lower() in cred.get("name", "").lower()
            ]

        return result

    def create_credential(self, name: str, value: str,
                         unique_suffix: bool = True) -> Dict[str, Any]:
        """
        Create a new PSK credential via IAM API.

        Args:
            name: Credential name (will add UUID suffix if unique_suffix=True)
            value: Pre-shared key value
            unique_suffix: If True, adds 6-char UUID suffix to avoid duplicates

        Returns:
            Dictionary with 'results' containing credential details including 'id'
        """
        import uuid

        if unique_suffix:
            suffix = uuid.uuid4().hex[:6]
            name = f"{name}-{suffix}"

        url = f"{self.base_url}/api/iam/v2/keys"
        payload = {
            "name": name,
            "source_id": "psk",
            "key_type": "psk",
            "key_data": {
                "psk": value
            }
        }

        r = self.session.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def get_credential(self, credential_id: str) -> Dict[str, Any]:
        """
        Get credential by ID via IAM API.

        Args:
            credential_id: The credential ID

        Returns:
            Dictionary with 'result' containing credential details
        """
        url = f"{self.base_url}/api/iam/v2/keys/{credential_id}"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def delete_credential(self, credential_id: str) -> Dict[str, Any]:
        """
        Delete credential via IAM API.

        Args:
            credential_id: The credential ID

        Returns:
            Dictionary with deletion confirmation
        """
        url = f"{self.base_url}/api/iam/v2/keys/{credential_id}"
        r = self.session.delete(url, headers=self.headers)
        r.raise_for_status()
        return {"status": "deleted", "id": credential_id}

    def find_or_create_credential(self, name: str, value: str) -> Dict[str, Any]:
        """
        Find existing credential by name or create new one with unique suffix.

        Args:
            name: Base credential name
            value: Pre-shared key value

        Returns:
            Dictionary with credential details including 'id'
        """
        # Try to find existing credential
        credentials = self.list_credentials(name_filter=name)

        if credentials.get("results"):
            # Return first match
            existing = credentials["results"][0]
            return {
                "id": existing["id"],
                "name": existing["name"],
                "reused": True
            }

        # Create new credential with unique suffix
        result = self.create_credential(name=name, value=value, unique_suffix=True)
        cred = result.get("results", {})
        return {
            "id": cred.get("id"),
            "name": cred.get("name"),
            "reused": False
        }

    # ==================== Consolidated Configure API ====================

    def consolidated_configure(self, payload: Dict[str, Any], max_retries: int = 12) -> Dict[str, Any]:
        """
        Execute consolidated configure operation (atomic CREATE/UPDATE for VPN infrastructure).
        Handles Universal Service, Endpoints, Access Locations, and Credentials in one transaction.

        Args:
            payload: Configuration payload with sections:
                - universal_service: Service configuration
                - endpoints: Endpoint configurations (create/update/delete)
                - access_locations: Access location configurations (create/update/delete)
                - credentials: Credential configurations (create/update)
                - locations: Location configurations (create/update)
            max_retries: Maximum retry attempts for 409/429 conflicts (default: 12)

        Returns:
            Dictionary with operation result
        """
        url = f"{self.base_url}/api/universalinfra/v1/consolidated/configure"

        attempt = 1
        while attempt <= max_retries:
            r = self.session.post(url, json=payload)

            # Success
            if r.status_code == 200:
                return r.json() if r.text else {"status": "success"}

            # Conflict or rate limit - retry with backoff
            if r.status_code in (409, 429):
                retry_after = r.headers.get("Retry-After")
                if retry_after:
                    try:
                        sleep_time = int(retry_after)
                    except ValueError:
                        sleep_time = min(60, 5 * (2 ** (attempt - 1)))
                else:
                    sleep_time = min(60, 5 * (2 ** (attempt - 1)))

                print(f"⏳ Operation in progress (HTTP {r.status_code}). Retry {attempt}/{max_retries} in {sleep_time}s...")
                import time
                time.sleep(sleep_time)
                attempt += 1
                continue

            # Other errors - raise immediately
            r.raise_for_status()

        # Max retries exceeded
        r.raise_for_status()
        return r.json() if r.text else {}
