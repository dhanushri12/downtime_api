"""
═══════════════════════════════════════════════════════════════════════
GEOLOCATION SERVICE MODULE
═══════════════════════════════════════════════════════════════════════
Handles IP address geolocation and public IP detection.
"""

import ipaddress
import logging
from typing import Dict, Optional

import httpx

from config import settings
from constants import (
    API_IP_GEOLOCATION,
    API_PUBLIC_IP,
    TIMEOUT_API_CALL,
    TIMEOUT_IP_LOOKUP,
)

# ═══════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# GEOLOCATION SERVICE CLASS
# ═══════════════════════════════════════════════


class GeolocationService:
    """Service for IP geolocation and public IP detection."""

    def __init__(self):
        """Initialize geolocation service."""
        self.ip_api_url = settings.IP_GEOLOCATION_API
        self.public_ip_api_url = settings.PUBLIC_IP_API

    async def get_public_ip(self) -> str:
        """
        Get server's public IP address.
        
        Returns:
            Public IP address string, or "Unknown" if lookup fails.
        """
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_IP_LOOKUP) as client:
                response = await client.get(self.public_ip_api_url)
                response.raise_for_status()
                data = response.json()
                public_ip = data.get("ip", "Unknown")
                logger.info(f"Public IP retrieved: {public_ip}")
                return public_ip
        except httpx.TimeoutException:
            logger.warning("Timeout getting public IP")
            return "Unknown"
        except Exception as e:
            logger.error(f"Error getting public IP: {str(e)}")
            return "Unknown"

    async def get_geolocation(self, ip_address: str) -> Dict[str, str]:
        """
        Get geolocation information for an IP address.
        
        Args:
            ip_address: IP address to lookup.
            
        Returns:
            Dictionary with geolocation data.
        """
        try:
            # Clean IP address
            clean_ip = ip_address.split(":")[0].strip()

            # Check if IP is private/loopback
            ip_obj = ipaddress.ip_address(clean_ip)
            is_private = ip_obj.is_private or ip_obj.is_loopback

            # Get public IP if private
            if is_private:
                public_ip = await self.get_public_ip()
            else:
                public_ip = clean_ip

            # Lookup geolocation
            async with httpx.AsyncClient(timeout=TIMEOUT_API_CALL) as client:
                response = await client.get(f"{self.ip_api_url}/{public_ip}")
                response.raise_for_status()
                data = response.json()

                geolocation = {
                    "private_ip": clean_ip,
                    "public_ip": public_ip,
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("countryCode", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "timezone": data.get("timezone", "Unknown"),
                    "latitude": str(data.get("lat", 0.0)),
                    "longitude": str(data.get("lon", 0.0)),
                    "isp": data.get("isp", "Unknown"),
                }

                logger.info(f"Geolocation retrieved for {clean_ip}: {geolocation['city']}, {geolocation['country']}")
                return geolocation

        except Exception as e:
            logger.error(f"Error getting geolocation for {ip_address}: {str(e)}")
            return self._get_default_geolocation(ip_address)

    @staticmethod
    def _get_default_geolocation(ip_address: str) -> Dict[str, str]:
        """
        Return default geolocation object when lookup fails.
        
        Args:
            ip_address: IP address.
            
        Returns:
            Default geolocation dictionary.
        """
        return {
            "private_ip": ip_address,
            "public_ip": "Unknown",
            "country": "Unknown",
            "country_code": "Unknown",
            "region": "Unknown",
            "city": "Unknown",
            "timezone": "Unknown",
            "latitude": "0.0",
            "longitude": "0.0",
            "isp": "Unknown",
        }

    @staticmethod
    def is_private_ip(ip_address: str) -> bool:
        """
        Check if IP address is private.
        
        Args:
            ip_address: IP address to check.
            
        Returns:
            True if IP is private, False otherwise.
        """
        try:
            clean_ip = ip_address.split(":")[0].strip()
            ip_obj = ipaddress.ip_address(clean_ip)
            return ip_obj.is_private or ip_obj.is_loopback
        except ValueError:
            logger.warning(f"Invalid IP address: {ip_address}")
            return False


# ═══════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════
geolocation_service = GeolocationService()
