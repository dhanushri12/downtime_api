"""
═══════════════════════════════════════════════════════════════════════
TURBINE SERVICE MODULE
═══════════════════════════════════════════════════════════════════════
Handles turbine operational data generation and management.
Simulates realistic turbine behavior and metrics.
"""

import random
import logging
import time
from typing import Dict, List, Optional, Tuple

from constants import (
    TurbineStatus,
    TURBINE_STATUS_DISTRIBUTION,
    CAPACITY_FACTOR_MIN,
    CAPACITY_FACTOR_MAX,
    POWER_CURVE_CUT_IN_SPEED,
    POWER_CURVE_RATED_SPEED_MIN,
    POWER_CURVE_RATED_SPEED_MAX,
    POWER_CURVE_CUT_OUT_SPEED,
    REACTIVE_POWER_MIN,
    REACTIVE_POWER_MAX,
    WIND_SPEED_MIN,
    WIND_SPEED_MAX,
    ROTOR_SPEED_MIN,
    ROTOR_SPEED_MAX,
    TEMPERATURE_RUNNING_MIN,
    TEMPERATURE_RUNNING_MAX,
    TEMPERATURE_STOPPED_MIN,
    TEMPERATURE_STOPPED_MAX,
    PITCH_ANGLE_MIN,
    PITCH_ANGLE_MAX,
    STATUS_CACHE_DURATION_MIN,
    STATUS_CACHE_DURATION_MAX,
    PROBABILITY_STATUS_CHANGE,
)
from helpers import get_wind_direction

# ═══════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# GLOBAL CACHES
# ═══════════════════════════════════════════════
turbine_status_cache: Dict[int, Dict] = {}


# ═══════════════════════════════════════════════
# TURBINE SERVICE CLASS
# ═══════════════════════════════════════════════


class TurbineService:
    """Service for turbine data generation and management."""

    @staticmethod
    def generate_power_curve(capacity_kw: float) -> List[Dict[str, float]]:
        """
        Generate power curve points for a turbine.
        
        Args:
            capacity_kw: Turbine capacity in kW.
            
        Returns:
            List of power curve points with wind speed and power output.
        """
        points = []
        for wind_speed in range(0, 26):
            if wind_speed < POWER_CURVE_CUT_IN_SPEED:
                power = 0.0
            elif wind_speed < POWER_CURVE_RATED_SPEED_MAX:
                # Linear interpolation between cut-in and rated speed
                power = round(
                    capacity_kw * (
                        (wind_speed - POWER_CURVE_CUT_IN_SPEED) /
                        (POWER_CURVE_RATED_SPEED_MAX - POWER_CURVE_CUT_IN_SPEED)
                    ),
                    2
                )
            elif wind_speed < POWER_CURVE_CUT_OUT_SPEED:
                power = capacity_kw
            else:
                power = 0.0

            points.append({
                "wind_speed": float(wind_speed),
                "power_kw": power
            })

        return points

    @staticmethod
    def get_or_initialize_status(turbine_id: int) -> None:
        """
        Get or initialize turbine status cache.
        
        Args:
            turbine_id: ID of turbine.
        """
        if turbine_id not in turbine_status_cache:
            # Generate initial status based on distribution
            roll = random.random()
            if roll < TURBINE_STATUS_DISTRIBUTION[TurbineStatus.RUNNING.value]:
                status = TurbineStatus.RUNNING.value
            elif roll < (TURBINE_STATUS_DISTRIBUTION[TurbineStatus.RUNNING.value] +
                        TURBINE_STATUS_DISTRIBUTION[TurbineStatus.STOPPED.value]):
                status = TurbineStatus.STOPPED.value
            else:
                status = TurbineStatus.MISCOMMUNICATION.value

            turbine_status_cache[turbine_id] = {
                "status": status,
                "last_status_change": int(time.time()),
                "status_duration": random.randint(
                    STATUS_CACHE_DURATION_MIN,
                    STATUS_CACHE_DURATION_MAX
                )
            }

    @staticmethod
    def update_turbine_status(turbine_id: int) -> str:
        """
        Update turbine status with occasional state transitions.
        
        Args:
            turbine_id: ID of turbine.
            
        Returns:
            Current turbine status.
        """
        TurbineService.get_or_initialize_status(turbine_id)

        cached = turbine_status_cache[turbine_id]
        current_time = int(time.time())
        time_since_change = current_time - cached["last_status_change"]

        # Check if status duration expired
        if time_since_change >= cached["status_duration"]:
            if random.random() < PROBABILITY_STATUS_CHANGE:
                current_status = cached["status"]

                # Generate new status based on current state
                if current_status == TurbineStatus.RUNNING.value:
                    roll = random.random()
                    if roll < 0.70:
                        new_status = TurbineStatus.RUNNING.value
                    elif roll < 0.95:
                        new_status = TurbineStatus.STOPPED.value
                    else:
                        new_status = TurbineStatus.MISCOMMUNICATION.value

                elif current_status == TurbineStatus.STOPPED.value:
                    roll = random.random()
                    if roll < 0.60:
                        new_status = TurbineStatus.RUNNING.value
                    elif roll < 0.90:
                        new_status = TurbineStatus.STOPPED.value
                    else:
                        new_status = TurbineStatus.MISCOMMUNICATION.value

                else:  # miscommunication
                    roll = random.random()
                    if roll < 0.75:
                        new_status = TurbineStatus.RUNNING.value
                    elif roll < 0.95:
                        new_status = TurbineStatus.STOPPED.value
                    else:
                        new_status = TurbineStatus.MISCOMMUNICATION.value

                if new_status != current_status:
                    cached["status"] = new_status
                    cached["last_status_change"] = current_time
                    cached["status_duration"] = random.randint(
                        STATUS_CACHE_DURATION_MIN,
                        STATUS_CACHE_DURATION_MAX
                    )
            else:
                cached["last_status_change"] = current_time

        return cached["status"]

    @staticmethod
    def generate_metrics(turbine_id: int, capacity_mw: float) -> Dict:
        """
        Generate realistic turbine operational metrics.
        
        Args:
            turbine_id: ID of turbine.
            capacity_mw: Turbine capacity in MW.
            
        Returns:
            Dictionary of turbine metrics.
        """
        status = TurbineService.update_turbine_status(turbine_id)
        capacity_kw = capacity_mw * 1000

        if status == TurbineStatus.RUNNING.value:
            # Running turbine - realistic power generation
            capacity_factor = random.uniform(CAPACITY_FACTOR_MIN, CAPACITY_FACTOR_MAX)
            active_power_kw = round(capacity_kw * capacity_factor, 2)
            reactive_power_kvar = round(
                random.uniform(REACTIVE_POWER_MIN, REACTIVE_POWER_MAX),
                2
            )
            wind_speed_mps = round(random.uniform(4.0, 22.0), 2)
            rotor_speed_rpm = round(random.uniform(8.0, 18.0), 2)
            temperature_c = round(random.uniform(TEMPERATURE_RUNNING_MIN, TEMPERATURE_RUNNING_MAX), 1)

        elif status == TurbineStatus.STOPPED.value:
            # Stopped turbine
            active_power_kw = 0.0
            reactive_power_kvar = 0.0
            wind_speed_mps = round(random.uniform(0.0, 20.0), 2)
            rotor_speed_rpm = 0.0
            temperature_c = round(random.uniform(TEMPERATURE_STOPPED_MIN, TEMPERATURE_STOPPED_MAX), 1)

        else:  # miscommunication
            active_power_kw = 0.0
            reactive_power_kvar = 0.0
            wind_speed_mps = 0.0
            rotor_speed_rpm = 0.0
            temperature_c = 0.0

        # Pitch angles
        pitch_angle_1 = round(random.uniform(PITCH_ANGLE_MIN, PITCH_ANGLE_MAX), 2) if status == TurbineStatus.RUNNING.value else 0.0
        pitch_angle_2 = round(random.uniform(PITCH_ANGLE_MIN, PITCH_ANGLE_MAX), 2) if status == TurbineStatus.RUNNING.value else 0.0
        pitch_angle_3 = round(random.uniform(PITCH_ANGLE_MIN, PITCH_ANGLE_MAX), 2) if status == TurbineStatus.RUNNING.value else 0.0

        # Plant Load Factor
        plf_pct = round((active_power_kw / capacity_kw) * 100, 2) if capacity_kw and active_power_kw > 0 else 0.0

        return {
            "status": status,
            "active_power_kw": active_power_kw,
            "reactive_power_kvar": reactive_power_kvar,
            "wind_speed_mps": wind_speed_mps,
            "wind_direction_deg": round(random.uniform(0.0, 359.9), 1),
            "rotor_speed_rpm": rotor_speed_rpm,
            "temperature_c": temperature_c,
            "pitch_angle_1": pitch_angle_1,
            "pitch_angle_2": pitch_angle_2,
            "pitch_angle_3": pitch_angle_3,
            "plf_pct": plf_pct,
        }

    @staticmethod
    def generate_downtime_energy(metrics: Dict) -> Dict:
        """
        Generate downtime and energy metrics.
        
        Args:
            metrics: Current turbine metrics.
            
        Returns:
            Dictionary with downtime and energy data.
        """
        return {
            "ma": round(random.uniform(0, 5), 2),
            "iga": round(random.uniform(0, 3), 2),
            "ega": round(random.uniform(0, 2), 2),
            "total_downtime": round(random.uniform(0, 10), 2),
            "energy_today_kwh": round(random.uniform(10000, 50000), 2)
        }

    @staticmethod
    def clear_cache(turbine_id: Optional[int] = None) -> None:
        """
        Clear turbine cache.
        
        Args:
            turbine_id: If provided, clear only that turbine's cache. Otherwise clear all.
        """
        global turbine_status_cache
        if turbine_id is not None:
            if turbine_id in turbine_status_cache:
                del turbine_status_cache[turbine_id]
                logger.info(f"Cleared cache for turbine {turbine_id}")
        else:
            turbine_status_cache.clear()
            logger.info("Cleared all turbine caches")


# ═══════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════
turbine_service = TurbineService()
