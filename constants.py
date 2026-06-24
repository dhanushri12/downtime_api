"""
═══════════════════════════════════════════════════════════════════════
CONSTANTS MODULE
═══════════════════════════════════════════════════════════════════════
Centralized configuration constants for the Wind Turbine SCADA System.
No magic strings or numbers in the codebase.
"""

from enum import Enum
from typing import Dict, Set

# ═══════════════════════════════════════════════
# APPLICATION METADATA
# ═══════════════════════════════════════════════
APP_TITLE: str = "Wind Turbine SCADA Dashboard API"
APP_VERSION: str = "2.0.0"
APP_DESCRIPTION: str = "Real-time wind turbine monitoring and management system"

# ═══════════════════════════════════════════════
# FILE UPLOAD CONSTRAINTS
# ═══════════════════════════════════════════════
ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB in bytes
UPLOAD_DIR: str = "uploads/profile_photos"

# ═══════════════════════════════════════════════
# USER ROLES
# ═══════════════════════════════════════════════
class UserRole(str, Enum):
    """Enumeration of user roles in the system."""
    EMPLOYEE = "employee"
    VENDOR = "vendor"
    RC = "rc"

VALID_ROLES: Set[str] = {role.value for role in UserRole}

# ═══════════════════════════════════════════════
# SITE CONFIGURATION
# ═══════════════════════════════════════════════
SITE_DATA_TABLES: Dict[int, str] = {
    1: "tbl_koppaldata",
    2: "tbl_bharuchdata",
    3: "tbl_karurdata",
    4: "tbl_tuticorindata",
    5: "tbl_jodhpurdata"
}

SITES: Dict[int, Dict[str, str]] = {
    1: {"name": "KOPPAL", "code": "KA"},
    2: {"name": "BHARUCH", "code": "GJ"},
    3: {"name": "KARUR", "code": "TN"},
    4: {"name": "TUTICORIN", "code": "TN"},
    5: {"name": "JODHPUR", "code": "RJ"}
}

# ═══════════════════════════════════════════════
# TURBINE STATUS
# ═══════════════════════════════════════════════
class TurbineStatus(str, Enum):
    """Enumeration of turbine operational states."""
    RUNNING = "running"
    STOPPED = "stopped"
    MISCOMMUNICATION = "miscommunication"

TURBINE_STATUS_DISTRIBUTION: Dict[str, float] = {
    TurbineStatus.RUNNING.value: 0.90,        # 90% of time
    TurbineStatus.STOPPED.value: 0.08,        # 8% of time
    TurbineStatus.MISCOMMUNICATION.value: 0.02  # 2% of time
}

# ═══════════════════════════════════════════════
# WEATHER CODES (WMO STANDARD)
# ═══════════════════════════════════════════════
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Slight Showers",
    81: "Moderate Showers",
    82: "Violent Showers",
    95: "Thunderstorm",
    96: "Thunderstorm w/ Hail",
    99: "Thunderstorm w/ Heavy Hail",
}

# ═══════════════════════════════════════════════
# WIND DIRECTION CONFIGURATION
# ═══════════════════════════════════════════════
WIND_DIRECTIONS: list = [
    'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
]
WIND_DIRECTION_DEGREES_PER_SECTOR: float = 22.5
WIND_DIRECTION_SECTORS: int = 16

# ═══════════════════════════════════════════════
# ALARM SEVERITY LEVELS
# ═══════════════════════════════════════════════
class AlarmSeverity(str, Enum):
    """Enumeration of alarm severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# ═══════════════════════════════════════════════
# ALARM PARAMETERS MAPPING
# ═══════════════════════════════════════════════
ALARM_PARAMETERS: Dict[str, tuple] = {
    "VIB001": ("Vibration", 12.5, 10.0, 2.5),
    "TMP001": ("Temperature", 85.0, 75.0, 10.0),
    "PWR001": ("Power Output", 5300.0, 5000.0, 300.0),
}
ALARM_DEFAULT_PARAMETER: tuple = ("Generic Parameter", 100.0, 80.0, 20.0)

# ═══════════════════════════════════════════════
# SYSTEM AFFECTED BY ALARMS
# ═══════════════════════════════════════════════
ALARM_SYSTEM_MAP: Dict[str, str] = {
    "VIB001": "Vibration Monitoring System",
    "TMP001": "Thermal Management System",
    "PWR001": "Power Generation System",
}
ALARM_DEFAULT_SYSTEM: str = "General Control System"

# ═══════════════════════════════════════════════
# POWER CURVE CONFIGURATION (FOR TURBINE 5.3 MW)
# ═══════════════════════════════════════════════
POWER_CURVE_CUT_IN_SPEED: float = 3.0          # m/s
POWER_CURVE_RATED_SPEED_MIN: float = 3.0       # m/s
POWER_CURVE_RATED_SPEED_MAX: float = 12.0      # m/s
POWER_CURVE_CUT_OUT_SPEED: float = 25.0        # m/s
POWER_CURVE_RATED_CAPACITY_RATIO: float = 1.0 # ratio

# ═══════════════════════════════════════════════
# OPERATIONAL DATA RANGES
# ═══════════════════════════════════════════════
CAPACITY_FACTOR_MIN: float = 0.28     # 28%
CAPACITY_FACTOR_MAX: float = 0.94     # 94%
REACTIVE_POWER_MIN: float = -600.0    # kVAR
REACTIVE_POWER_MAX: float = 600.0     # kVAR
WIND_SPEED_MIN: float = 0.0           # m/s
WIND_SPEED_MAX: float = 25.0          # m/s
ROTOR_SPEED_MIN: float = 5.0          # RPM
ROTOR_SPEED_MAX: float = 20.0         # RPM
TEMPERATURE_RUNNING_MIN: float = 28.0 # °C
TEMPERATURE_RUNNING_MAX: float = 50.0 # °C
TEMPERATURE_STOPPED_MIN: float = 20.0 # °C
TEMPERATURE_STOPPED_MAX: float = 40.0 # °C
PITCH_ANGLE_MIN: float = 0.0          # degrees
PITCH_ANGLE_MAX: float = 25.0         # degrees

# ═══════════════════════════════════════════════
# VOLTAGE SPECIFICATIONS
# ═══════════════════════════════════════════════
VOLTAGE_NOMINAL: float = 690.0  # Volts
VOLTAGE_MIN: float = 660.0      # Volts
VOLTAGE_MAX: float = 710.0      # Volts

# ═══════════════════════════════════════════════
# FREQUENCY SPECIFICATIONS
# ═══════════════════════════════════════════════
FREQUENCY_NOMINAL: float = 50.0   # Hz
FREQUENCY_MIN: float = 49.5       # Hz
FREQUENCY_MAX: float = 50.5       # Hz

# ═══════════════════════════════════════════════
# POWER FACTOR SPECIFICATIONS
# ═══════════════════════════════════════════════
POWER_FACTOR_MIN: float = 0.85
POWER_FACTOR_MAX: float = 1.0

# ═══════════════════════════════════════════════
# CACHING CONFIGURATION
# ═══════════════════════════════════════════════
LIVE_REFRESH_INTERVAL: int = 5      # seconds
STATUS_CACHE_DURATION_MIN: int = 3600  # seconds (1 hour)
STATUS_CACHE_DURATION_MAX: int = 7200  # seconds (2 hours)

# ═══════════════════════════════════════════════
# SMOOTHING FACTORS FOR LIVE DATA
# ═══════════════════════════════════════════════
SMOOTHING_FACTOR_POWER: float = 0.85
SMOOTHING_FACTOR_WIND: float = 0.85
SMOOTHING_FACTOR_ROTOR: float = 0.85
SMOOTHING_FACTOR_VOLTAGE: float = 0.98
SMOOTHING_FACTOR_FREQUENCY: float = 0.99
SMOOTHING_FACTOR_POWER_FACTOR: float = 0.98
SMOOTHING_FACTOR_TEMPERATURE: float = 0.95
SMOOTHING_FACTOR_REACTIVE_POWER: float = 0.95
SMOOTHING_FACTOR_HYDRAULIC: float = 0.98

# ═══════════════════════════════════════════════
# PERTURBATION RANGES
# ═══════════════════════════════════════════════
PERTURBATION_POWER: float = 50.0     # kW
PERTURBATION_WIND: float = 0.3       # m/s
PERTURBATION_ROTOR: float = 0.2      # RPM
PERTURBATION_VOLTAGE: float = 15.0   # V
PERTURBATION_FREQUENCY: float = 0.02 # Hz
PERTURBATION_TEMPERATURE: float = 0.3 # °C
PERTURBATION_YAW: float = 1.5        # degrees
PERTURBATION_HYDRAULIC: float = 5.0  # bar
PERTURBATION_WIND_DIRECTION: float = 2.0  # degrees

# ═══════════════════════════════════════════════
# TEMPERATURE BOUNDARIES
# ═══════════════════════════════════════════════
TEMPERATURE_AMBIENT_MIN: float = 25.0  # °C
TEMPERATURE_AMBIENT_MAX: float = 55.0  # °C
TEMPERATURE_HUB_MIN: float = 30.0      # °C
TEMPERATURE_HUB_MAX: float = 70.0      # °C

# ═══════════════════════════════════════════════
# HYDRAULIC PRESSURE BOUNDARIES
# ═══════════════════════════════════════════════
HYDRAULIC_PRESSURE_MIN: float = 140.0   # bar
HYDRAULIC_PRESSURE_MAX: float = 210.0   # bar
HYDRAULIC_PRESSURE_NOMINAL_MIN: float = 150.0  # bar
HYDRAULIC_PRESSURE_NOMINAL_MAX: float = 200.0  # bar

# ═══════════════════════════════════════════════
# OTP CONFIGURATION
# ═══════════════════════════════════════════════
OTP_LENGTH: int = 6
OTP_EXPIRY_MINUTES: int = 10

# ═══════════════════════════════════════════════
# PASSWORD VALIDATION RULES
# ═══════════════════════════════════════════════
PASSWORD_MIN_LENGTH: int = 6
PASSWORD_REQUIRE_UPPERCASE: bool = True
PASSWORD_REQUIRE_LOWERCASE: bool = True
PASSWORD_REQUIRE_DIGIT_OR_SPECIAL: bool = True

# ═══════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════
DEFAULT_PAGE_SIZE: int = 50
MAX_PAGE_SIZE: int = 1000

# ═══════════════════════════════════════════════
# HTTP STATUS CODES
# ═══════════════════════════════════════════════
HTTP_OK: int = 200
HTTP_CREATED: int = 201
HTTP_BAD_REQUEST: int = 400
HTTP_UNAUTHORIZED: int = 401
HTTP_FORBIDDEN: int = 403
HTTP_NOT_FOUND: int = 404
HTTP_CONFLICT: int = 409
HTTP_INTERNAL_SERVER_ERROR: int = 500

# ═══════════════════════════════════════════════
# ERROR MESSAGES
# ═══════════════════════════════════════════════
ERROR_INVALID_CREDENTIALS: str = "Invalid username or password"
ERROR_USER_NOT_FOUND: str = "User not found"
ERROR_USER_EXISTS: str = "Username or Email already exists"
ERROR_PASSWORD_MISMATCH: str = "Password and Confirm Password do not match"
ERROR_INVALID_OTP: str = "Invalid or expired OTP"
ERROR_INVALID_FILE_TYPE: str = "Only jpg/jpeg/png allowed"
ERROR_FILE_TOO_LARGE: str = "Photo exceeds 5MB"
ERROR_DATABASE: str = "Database error occurred"
ERROR_INTERNAL_SERVER: str = "Internal server error"
ERROR_VALIDATION_FAILED: str = "Validation failed"
ERROR_UNAUTHORIZED_ACCESS: str = "Unauthorized access"
ERROR_RESOURCE_NOT_FOUND: str = "Resource not found"

# ═══════════════════════════════════════════════
# SUCCESS MESSAGES
# ═══════════════════════════════════════════════
SUCCESS_USER_REGISTERED: str = "User Registered Successfully"
SUCCESS_LOGIN: str = "Login Successful"
SUCCESS_PASSWORD_RESET: str = "Password reset successfully"
SUCCESS_PROFILE_UPDATED: str = "Profile updated successfully"
SUCCESS_OTP_SENT: str = "OTP sent to your email"

# ═══════════════════════════════════════════════
# DATABASE MODELS
# ═══════════════════════════════════════════════
DB_TABLE_USERS: str = "tbl_users"
DB_TABLE_ALARMS: str = "tbl_alarms"
DB_TABLE_SITES: str = "tbl_sites"
DB_TABLE_TURBINES: str = "tbl_turbines"
DB_TABLE_ALARM_MASTER: str = "tbl_alarm_master"

# ═══════════════════════════════════════════════
# EXTERNAL API ENDPOINTS
# ═══════════════════════════════════════════════
API_IP_GEOLOCATION: str = "http://ip-api.com/json"
API_PUBLIC_IP: str = "https://api64.ipify.org?format=json"
API_WEATHER: str = "https://api.open-meteo.com/v1/forecast"

# ═══════════════════════════════════════════════
# API TIMEOUTS (seconds)
# ═══════════════════════════════════════════════
TIMEOUT_API_CALL: int = 10
TIMEOUT_IP_LOOKUP: int = 5

# ═══════════════════════════════════════════════
# EMAIL CONFIGURATION
# ═══════════════════════════════════════════════
EMAIL_SUBJECT_OTP: str = "Password Reset OTP"
EMAIL_SUBJECT_WELCOME: str = "Welcome to Wind Turbine SCADA System"

# ═══════════════════════════════════════════════
# BRAKE STATUS
# ═══════════════════════════════════════════════
BRAKE_STATUS_RELEASED: str = "Released"
BRAKE_STATUS_APPLIED: str = "Applied"

# ═══════════════════════════════════════════════
# GRID SYNCHRONIZATION STATUS
# ═══════════════════════════════════════════════
GRID_STATUS_SYNCHRONIZED: str = "Synchronized"
GRID_STATUS_NOT_SYNCHRONIZED: str = "Not Synchronized"

# ═══════════════════════════════════════════════
# PROBABILITY DISTRIBUTIONS (as percentages)
# ═══════════════════════════════════════════════
PROBABILITY_BRAKE_RELEASED: float = 0.98
PROBABILITY_GRID_SYNCHRONIZED: float = 0.99
PROBABILITY_STATUS_CHANGE: float = 0.10
