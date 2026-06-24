"""
═══════════════════════════════════════════════════════════════════════
HELPERS MODULE
═══════════════════════════════════════════════════════════════════════
Common utility functions used across the application.
Includes ID generation, password validation, client IP detection, etc.
"""

import re
import uuid
import random
import string
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import Request

from constants import (
    PASSWORD_MIN_LENGTH,
    PASSWORD_REQUIRE_UPPERCASE,
    PASSWORD_REQUIRE_LOWERCASE,
    PASSWORD_REQUIRE_DIGIT_OR_SPECIAL,
    WIND_DIRECTIONS,
    WIND_DIRECTION_DEGREES_PER_SECTOR,
    WIND_DIRECTION_SECTORS,
)

# ═══════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# ID GENERATION
# ═══════════════════════════════════════════════


def generate_short_id(length: int = 8) -> str:
    """
    Generate a random short ID string.
    
    Args:
        length: Length of ID to generate (default 8).
        
    Returns:
        Random alphanumeric string suitable for short IDs.
        
    Example:
        >>> id = generate_short_id()
        >>> len(id)
        8
    """
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return ''.join(random.choices(chars, k=length))


def generate_uuid() -> str:
    """
    Generate a universally unique identifier.
    
    Returns:
        UUID string.
    """
    return str(uuid.uuid4())


def generate_uuid_hex() -> str:
    """
    Generate a UUID in hexadecimal format.
    
    Returns:
        UUID hex string (no dashes).
    """
    return uuid.uuid4().hex


# ═══════════════════════════════════════════════
# PASSWORD VALIDATION
# ═══════════════════════════════════════════════


def validate_password(password: str) -> Optional[str]:
    """
    Validate password against security requirements.
    
    Args:
        password: Password to validate.
        
    Returns:
        Error message if validation fails, None if password is valid.
        
    Example:
        >>> error = validate_password("weak")
        >>> print(error)
        'Password must be at least 6 characters'
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters"

    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return "Password must contain uppercase letter"

    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return "Password must contain lowercase letter"

    if PASSWORD_REQUIRE_DIGIT_OR_SPECIAL:
        if not re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must contain number or special character"

    return None


# ═══════════════════════════════════════════════
# CLIENT IP DETECTION
# ═══════════════════════════════════════════════


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    Handles proxy headers and IPv6 addresses.
    
    Args:
        request: FastAPI Request object.
        
    Returns:
        Client IP address.
        
    Example:
        >>> ip = get_client_ip(request)
        >>> print(ip)
        '192.168.1.1'
    """
    # Check X-Forwarded-For header (proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Direct connection
    if request.client:
        return request.client.host

    return "Unknown"


# ═══════════════════════════════════════════════
# DATE/TIME FORMATTING
# ═══════════════════════════════════════════════


def format_alarm_datetime(date_str: Optional[str], time_str: Optional[str]) -> Optional[str]:
    """
    Format alarm date and time strings.
    
    Args:
        date_str: Date string in YYYY-MM-DD format.
        time_str: Time string in HH:MM:SS format.
        
    Returns:
        Formatted datetime string, None if parsing fails.
        
    Example:
        >>> result = format_alarm_datetime("2024-01-15", "14:30:00")
        >>> print(result)
        '15/01/2024 14:30:00'
    """
    if not date_str or not time_str:
        return None

    try:
        date_obj = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
        time_part = str(time_str)[:8]
        return f"{date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year} {time_part}"
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to format datetime: {str(e)}")
        return None


# ═══════════════════════════════════════════════
# WIND DIRECTION CONVERSION
# ═══════════════════════════════════════════════


def get_wind_direction(degrees: float) -> str:
    """
    Convert wind direction in degrees to cardinal direction.
    
    Args:
        degrees: Wind direction in degrees (0-360).
        
    Returns:
        Cardinal direction string (N, NE, E, SE, S, SW, W, NW, etc.).
        
    Example:
        >>> direction = get_wind_direction(45)
        >>> print(direction)
        'NE'
    """
    # Normalize degrees to 0-360 range
    degrees = degrees % 360

    # Calculate sector index
    idx = round(degrees / WIND_DIRECTION_DEGREES_PER_SECTOR) % WIND_DIRECTION_SECTORS

    return WIND_DIRECTIONS[idx]


# ═══════════════════════════════════════════════
# STRING UTILITIES
# ═══════════════════════════════════════════════


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP (One-Time Password).
    
    Args:
        length: Length of OTP (default 6).
        
    Returns:
        Random numeric OTP string.
    """
    return ''.join(random.choices(string.digits, k=length))


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate.
        
    Returns:
        True if email is valid format, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate.
        
    Returns:
        True if phone is valid format, False otherwise.
    """
    pattern = r'^[0-9\-\+\s\(\)]{10,}$'
    return re.match(pattern, phone) is not None


# ═══════════════════════════════════════════════
# LIST OPERATIONS
# ═══════════════════════════════════════════════


def flatten_list(nested_list: List) -> List:
    """
    Flatten a nested list.
    
    Args:
        nested_list: List containing nested lists.
        
    Returns:
        Flattened list.
        
    Example:
        >>> result = flatten_list([[1, 2], [3, 4]])
        >>> print(result)
        [1, 2, 3, 4]
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def remove_duplicates(items: List) -> List:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        items: List with potential duplicates.
        
    Returns:
        List with duplicates removed.
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ═══════════════════════════════════════════════
# ROUNDING AND FORMATTING
# ═══════════════════════════════════════════════


def round_to_decimals(value: float, decimals: int = 2) -> float:
    """
    Round a float value to specified decimal places.
    
    Args:
        value: Value to round.
        decimals: Number of decimal places.
        
    Returns:
        Rounded value.
    """
    return round(value, decimals)


def format_large_number(value: float, decimals: int = 2) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        value: Number to format.
        decimals: Decimal places to show.
        
    Returns:
        Formatted string (e.g., "1.5M", "500K").
    """
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"
