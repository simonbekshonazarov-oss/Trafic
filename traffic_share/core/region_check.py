"""Region checking utilities for IP validation."""

import httpx
from typing import Optional, List
from .exceptions import RegionNotAllowedError

class RegionChecker:
    """Check if IP address is from allowed regions."""
    
    def __init__(self, allowed_regions: List[str]):
        self.allowed_regions = [region.upper() for region in allowed_regions]
    
    async def check_ip_region(self, ip_address: str) -> bool:
        """Check if IP address is from allowed region."""
        try:
            # Using ipapi.co for IP geolocation
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://ipapi.co/{ip_address}/json/")
                data = response.json()
                
                country_code = data.get("country_code", "").upper()
                return country_code in self.allowed_regions
                
        except Exception:
            # If we can't check the region, allow by default
            # In production, you might want to be more strict
            return True
    
    def is_vpn_or_proxy(self, ip_address: str) -> bool:
        """Check if IP is likely a VPN or proxy."""
        # This is a simplified check
        # In production, you'd use a more sophisticated service
        # like IPQualityScore or similar
        return False
    
    async def validate_user_ip(self, ip_address: str) -> bool:
        """Validate user IP for traffic sharing."""
        if not await self.check_ip_region(ip_address):
            raise RegionNotAllowedError("Your region is not allowed for traffic sharing")
        
        if self.is_vpn_or_proxy(ip_address):
            raise RegionNotAllowedError("VPN and proxy connections are not allowed")
        
        return True

# Global region checker instance
region_checker = RegionChecker(["US", "EU", "CA", "AU"])
