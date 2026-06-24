"""
═══════════════════════════════════════════════════════════════════════
DASHBOARD ROUTES
═══════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import random

from database import get_db
from models import (
    DashboardResponse,
    DashboardSummary,
    TurbinesPage,
    TurbineItem,
    ActiveAlarmItem,
    TurbineCountData,
    TurbineOverviewFinalResponse,
    TurbineOverviewMainData,
    TurbineOverviewPagination,
    TurbineOverviewItem,
    ViewDetails,
    LiveData,
    PieChartData,
    PowerCurveData,
    DowntimeEnergy
)
from turbine_service import turbine_service
from constants import TurbineStatus

dashboard_router = APIRouter()

@dashboard_router.get("/live-api")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Get real-time dashboard data
    """
    # Generate mock turbine data
    turbines = []
    total_power = 0
    running_count = 0
    stopped_count = 0
    miscomm_count = 0
    
    for i in range(1, 21):  # 20 turbines
        metrics = turbine_service.generate_metrics(i, 2.1)
        
        if metrics["status"] == TurbineStatus.RUNNING.value:
            running_count += 1
            total_power += metrics["active_power_kw"] / 1000  # Convert to MW
        elif metrics["status"] == TurbineStatus.STOPPED.value:
            stopped_count += 1
        else:
            miscomm_count += 1
        
        turbines.append(TurbineItem(
            id=i,
            name=f"Turbine-{i:03d}",
            feeder=f"Feeder-{random.randint(1, 5)}",
            status=metrics["status"],
            active_power_kw=metrics["active_power_kw"],
            reactive_power_kvar=metrics["reactive_power_kvar"],
            wind_speed_mps=metrics["wind_speed_mps"],
            rotor_speed_rpm=metrics["rotor_speed_rpm"],
            temperature_c=metrics["temperature_c"],
            pitch_angle_1=metrics["pitch_angle_1"],
            pitch_angle_2=metrics["pitch_angle_2"],
            pitch_angle_3=metrics["pitch_angle_3"]
        ))
    
    # Generate mock active alarms
    active_alarms = []
    for i in range(3):
        active_alarms.append(ActiveAlarmItem(
            alarm_id=i+1,
            turbine_name=f"Turbine-{random.randint(1, 20):03d}",
            error_code=f"ERR{random.randint(100, 999)}",
            description=f"Alarm {i+1} description",
            risk_type=random.choice(["critical", "high", "medium", "low"]),
            occurred_datetime=datetime.now().isoformat()
        ))
    
    summary = DashboardSummary(
        total_turbines=20,
        running_turbines=running_count,
        stopped_turbines=stopped_count,
        active_alarms=len(active_alarms),
        total_power_mw=round(total_power, 2),
        avg_wind_speed_mps=round(random.uniform(5, 15), 2)
    )
    
    turbines_page = TurbinesPage(
        data=turbines,
        total=len(turbines),
        page=1,
        limit=50
    )
    
    return DashboardResponse(
        summary=summary,
        turbines=turbines_page,
        active_alarms=active_alarms
    )

@dashboard_router.get("/turbine-overview")
async def get_turbine_overview(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get turbine overview with pagination
    """
    # Generate turbine overview data
    turbine_items = []
    total_power = 0
    running_count = 0
    stopped_count = 0
    miscomm_count = 0
    total_plf = 0
    total_wind_speed = 0
    
    total_turbines = 20
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_turbines)
    
    for i in range(1, total_turbines + 1):
        metrics = turbine_service.generate_metrics(i, 2.1)
        status = metrics["status"]
        
        if status == TurbineStatus.RUNNING.value:
            running_count += 1
            total_power += metrics["active_power_kw"] / 1000
        elif status == TurbineStatus.STOPPED.value:
            stopped_count += 1
        else:
            miscomm_count += 1
        
        total_plf += metrics["plf_pct"]
        total_wind_speed += metrics["wind_speed_mps"]
        
        # Create turbine overview item
        if start_idx <= i <= end_idx:
            view_details = ViewDetails(
                id=i,
                turbine_name=f"Turbine-{i:03d}",
                ip=f"192.168.1.{i}",
                feeder=f"Feeder-{random.randint(1, 5)}",
                active_power_kw=metrics["active_power_kw"],
                reactive_power_kvar=metrics["reactive_power_kvar"],
                wind_speed_mps=metrics["wind_speed_mps"],
                plf_pct=metrics["plf_pct"],
                rotor_speed_rpm=metrics["rotor_speed_rpm"],
                wind_direction=f"{random.randint(0, 359)}°",
                temperature_c=metrics["temperature_c"],
                alarm_code=None,
                alarm_description=None,
                turbine_status=status,
                model="WTG-2.1MW",
                hub_height_m=80.0,
                capacity_mw=2.1,
                commission_date="2023-01-01",
                site_name=f"Site-{random.randint(1, 5)}",
                location=f"Location-{random.randint(1, 10)}",
                last_update_data=datetime.now().isoformat()
            )
            
            live_data = LiveData(
                turbine_name=f"Turbine-{i:03d}",
                active_power_kw=metrics["active_power_kw"],
                reactive_power_kvar=metrics["reactive_power_kvar"],
                voltage_v=random.uniform(660, 710),
                current_a=random.uniform(100, 500),
                frequency_hz=random.uniform(49.5, 50.5),
                power_factor=random.uniform(0.85, 1.0),
                rotor_speed_rpm=metrics["rotor_speed_rpm"],
                generator_speed_rpm=metrics["rotor_speed_rpm"] * 10,
                wind_speed_mps=metrics["wind_speed_mps"],
                wind_direction_deg=metrics["wind_direction_deg"],
                ambient_temperature_c=random.uniform(20, 40),
                hub_temperature_c=random.uniform(30, 50),
                yaw_position_deg=random.uniform(0, 359),
                hydraulic_pressure_bar=random.uniform(140, 210),
                brake_status="Released",
                grid_synchronization="Synchronized",
                ip=f"192.168.1.{i}",
                site_name=f"Site-{random.randint(1, 5)}"
            )
            
            piechart = PieChartData(
                active_power_kw=metrics["active_power_kw"],
                reactive_power_kvar=metrics["reactive_power_kvar"],
                wind_speed_mps=metrics["wind_speed_mps"],
                rotor_speed_rpm=metrics["rotor_speed_rpm"]
            )
            
            powercurve = PowerCurveData(
                turbine_id=i,
                energy_today_kwh=random.uniform(10000, 50000),
                turbine_status=status,
                downtime={"total": random.uniform(0, 10)},
                graph=turbine_service.generate_power_curve(2100)
            )
            
            turbine_items.append(TurbineOverviewItem(
                id=i,
                turbine_name=f"Turbine-{i:03d}",
                feeder=f"Feeder-{random.randint(1, 5)}",
                status=status,
                active_power_kw=metrics["active_power_kw"],
                wind_speed_mps=metrics["wind_speed_mps"],
                rotor_speed_rpm=metrics["rotor_speed_rpm"],
                temperature_c=metrics["temperature_c"],
                plf_pct=metrics["plf_pct"],
                pitch_angle_1=metrics["pitch_angle_1"],
                pitch_angle_2=metrics["pitch_angle_2"],
                pitch_angle_3=metrics["pitch_angle_3"],
                error_code=None,
                ip=f"192.168.1.{i}",
                sitename=f"Site-{random.randint(1, 5)}",
                power_generation=metrics["active_power_kw"],
                view_details=view_details,
                live_data=live_data,
                piechart=piechart,
                powercurve=powercurve
            ))
    
    main_data = TurbineOverviewMainData(
        total_turbine=total_turbines,
        running=running_count,
        stopped=stopped_count,
        miscommunication=miscomm_count,
        active_alarm=random.randint(0, 10),
        installed_capacity_mw=total_turbines * 2.1,
        total_power_generation_mw=round(total_power, 2),
        total_plf=round(total_plf / total_turbines, 2),
        avg_wind_speed_mps=round(total_wind_speed / total_turbines, 2)
    )
    
    pagination = TurbineOverviewPagination(
        data=turbine_items,
        total=total_turbines,
        page=page,
        limit=limit
    )
    
    return TurbineOverviewFinalResponse(
        status="success",
        server_timestamp=datetime.now().isoformat(),
        data=main_data,
        turbines=pagination
    )