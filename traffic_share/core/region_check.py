"""
IP region and VPN detection utilities
"""

import ipaddress
import re
from typing import Optional, Dict, Any
import httpx

from traffic_share.core.constants import ALLOWED_REGIONS
from traffic_share.core.exceptions import RegionNotAllowedError, VPNDetectedError


class RegionChecker:
    """Check IP region and detect VPN/Proxy"""
    
    # Known VPN/proxy IP ranges (example - should be updated regularly)
    VPN_IP_RANGES = [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]
    
    # Known cloud provider ranges (partial list for demo)
    CLOUD_PROVIDER_RANGES = [
        # Add AWS, GCP, Azure ranges
    ]
    
    def __init__(self, ip_api_enabled: bool = True):
        self.ip_api_enabled = ip_api_enabled
    
    def is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    def is_in_range(self, ip: str, ip_ranges: list) -> bool:
        """Check if IP is in given ranges"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for ip_range in ip_ranges:
                if ip_obj in ipaddress.ip_network(ip_range):
                    return True
            return False
        except ValueError:
            return False
    
    def is_vpn_or_proxy(self, ip: str) -> bool:
        """Detect if IP is VPN or proxy"""
        # Check private IPs
        if self.is_private_ip(ip):
            return True
        
        # Check against VPN ranges
        if self.is_in_range(ip, self.VPN_IP_RANGES):
            return True
        
        # Check cloud providers
        if self.is_in_range(ip, self.CLOUD_PROVIDER_RANGES):
            return True
        
        return False
    
    async def get_ip_info(self, ip: str) -> Dict[str, Any]:
        """Get IP information from external API"""
        if not self.ip_api_enabled:
            # Fallback to basic check
            return {
                "ip": ip,
                "country_code": "US",  # Default
                "region": "US",
                "is_vpn": self.is_vpn_or_proxy(ip)
            }
        
        try:
            async with httpx.AsyncClient() as client:
                # Using ip-api.com (free tier)
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        "ip": ip,
                        "country_code": data.get("countryCode", ""),
                        "country": data.get("country", ""),
                        "region": data.get("countryCode", ""),
                        "city": data.get("city", ""),
                        "isp": data.get("isp", ""),
                        "is_vpn": self.is_vpn_or_proxy(ip) or self._is_hosting_provider(data.get("isp", ""))
                    }
                
        except Exception:
            pass
        
        # Fallback
        return {
            "ip": ip,
            "country_code": "US",
            "region": "US",
            "is_vpn": self.is_vpn_or_proxy(ip)
        }
    
    def _is_hosting_provider(self, isp: str) -> bool:
        """Check if ISP is a known hosting provider"""
        hosting_keywords = [
            "amazon", "aws", "azure", "google cloud", "digitalocean",
            "linode", "vultr", "ovh", "hetzner", "vpn", "proxy"
        ]
        
        isp_lower = isp.lower()
        return any(keyword in isp_lower for keyword in hosting_keywords)
    
    async def validate_region(self, ip: str) -> Dict[str, Any]:
        """Validate if IP is from allowed region and not VPN"""
        ip_info = await self.get_ip_info(ip)
        
        # Check VPN
        if ip_info.get("is_vpn", False):
            raise VPNDetectedError(f"VPN or proxy detected from IP: {ip}")
        
        # Check region
        region = ip_info.get("country_code", "")
        if region not in ALLOWED_REGIONS:
            raise RegionNotAllowedError(
                f"Region {region} is not allowed. Allowed regions: {', '.join(ALLOWED_REGIONS)}"
            )
        
        return ip_info
    
    def extract_ip_from_request(self, headers: dict, remote_addr: str) -> str:
        """Extract real IP from request headers"""
        # Check X-Forwarded-For header
        forwarded_for = headers.get("x-forwarded-for")
        if forwarded_for:
            # Get first IP from chain
            ip = forwarded_for.split(",")[0].strip()
            return ip
        
        # Check X-Real-IP header
        real_ip = headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to remote address
        return remote_addr
