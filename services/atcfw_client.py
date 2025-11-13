"""
Atcfw (Advanced Threat Control Firewall / DFP) API Client
Handles DNS Firewall Protection, Security Policies, and Threat Intelligence
API Docs: https://csp.infoblox.com/apidoc/docs/Atcfw
"""

import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class AtcfwClient:
    """Client for Infoblox Atcfw API - DNS Security & Threat Protection"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Atcfw API client

        Args:
            api_key: Infoblox API key (defaults to INFOBLOX_API_KEY env var)
            base_url: Base URL for API (defaults to https://csp.infoblox.com)
        """
        self.api_key = api_key or os.getenv("INFOBLOX_API_KEY")
        self.base_url = (base_url or os.getenv("INFOBLOX_BASE_URL", "https://csp.infoblox.com")).rstrip("/")

        if not self.api_key:
            raise ValueError("INFOBLOX_API_KEY environment variable or api_key parameter is required")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        })

    # ==================== Security Policies ====================

    def list_security_policies(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List all security policies"""
        url = f"{self.base_url}/api/atcfw/v1/security_policies"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.session.headers, params=params)
        r.raise_for_status()
        return r.json()

    def get_security_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get security policy by ID"""
        url = f"{self.base_url}/api/atcfw/v1/security_policies/{policy_id}"
        r = self.session.get(url, headers=self.session.headers)
        r.raise_for_status()
        return r.json()

    # ==================== Named Lists (Custom Threat Intel) ====================

    def list_named_lists(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List custom threat intelligence named lists"""
        url = f"{self.base_url}/api/atcfw/v1/named_lists"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.session.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_named_list(self, name: str, type: str, items: Optional[List[str]] = None,
                         description: str = "", tags: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a custom named list for threat intelligence

        Args:
            name: List name
            type: List type (custom_list, etc.)
            items: List of items (domains, IPs, etc.)
            description: List description
            tags: Optional tags

        Returns:
            Created named list details
        """
        url = f"{self.base_url}/api/atcfw/v1/named_lists"
        payload = {
            "name": name,
            "type": type,
            "description": description,
            "items": items or [],
            "tags": tags or {}
        }

        r = self.session.post(url, headers=self.session.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def update_named_list(self, list_id: str, **kwargs) -> Dict[str, Any]:
        """Update a named list"""
        url = f"{self.base_url}/api/atcfw/v1/named_lists/{list_id}"
        r = self.session.put(url, headers=self.session.headers, json=kwargs)
        r.raise_for_status()
        return r.json()

    def delete_named_list(self, list_id: str) -> Dict[str, Any]:
        """Delete a named list"""
        url = f"{self.base_url}/api/atcfw/v1/named_lists/{list_id}"
        r = self.session.delete(url, headers=self.session.headers)
        r.raise_for_status()
        return {"status": "deleted", "id": list_id}

    # ==================== Application Filters ====================

    def list_application_filters(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List application filters"""
        url = f"{self.base_url}/api/atcfw/v1/application_filters"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.session.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_application_filter(self, name: str, criteria: List[Dict],
                                  description: str = "") -> Dict[str, Any]:
        """Create an application filter"""
        url = f"{self.base_url}/api/atcfw/v1/application_filters"
        payload = {
            "name": name,
            "criteria": criteria,
            "description": description
        }

        r = self.session.post(url, headers=self.session.headers, json=payload)
        r.raise_for_status()
        return r.json()

    # ==================== Category Filters ====================

    def list_category_filters(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List content category filters"""
        url = f"{self.base_url}/api/atcfw/v1/category_filters"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.session.headers, params=params)
        r.raise_for_status()
        return r.json()

    def list_content_categories(self) -> Dict[str, Any]:
        """List available content categories"""
        url = f"{self.base_url}/api/atcfw/v1/content_categories"
        r = self.session.get(url, headers=self.session.headers)
        r.raise_for_status()
        return r.json()

    # ==================== Internal Domain Lists ====================

    def list_internal_domain_lists(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List internal domain lists"""
        url = f"{self.base_url}/api/atcfw/v1/internal_domain_lists"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.session.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_internal_domain_list(self, name: str, internal_domains: List[str],
                                    description: str = "", tags: Optional[Dict] = None) -> Dict[str, Any]:
        """Create internal domain list"""
        url = f"{self.base_url}/api/atcfw/v1/internal_domain_lists"
        payload = {
            "name": name,
            "internal_domains": internal_domains,
            "description": description,
            "tags": tags or {}
        }

        r = self.session.post(url, headers=self.session.headers, json=payload)
        r.raise_for_status()
        return r.json()

    # ==================== Access Codes (Bypass Codes) ====================

    def list_access_codes(self, filter_expr: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """List access/bypass codes"""
        url = f"{self.base_url}/api/atcfw/v1/access_codes"
        params = {"_limit": limit}
        if filter_expr:
            params["_filter"] = filter_expr

        r = self.session.get(url, headers=self.session.headers, params=params)
        r.raise_for_status()
        return r.json()

    def create_access_code(self, name: str, activation: str, expiration: str,
                          rules: Optional[List[Dict]] = None,
                          description: str = "") -> Dict[str, Any]:
        """Create an access/bypass code"""
        url = f"{self.base_url}/api/atcfw/v1/access_codes"
        payload = {
            "name": name,
            "activation": activation,
            "expiration": expiration,
            "rules": rules or [],
            "description": description
        }

        r = self.session.post(url, headers=self.session.headers, json=payload)
        r.raise_for_status()
        return r.json()
