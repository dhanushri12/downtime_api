"""
═══════════════════════════════════════════════════════════════════════
ALARMS ROUTES
═══════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from database import get_db
from models import (
    AlarmResponse,
    AlarmRecord,
    AlarmSummary,
    AlarmPagination,
    AlarmErrorFormModel,
    AlarmTurbineItem,
    AlarmHistoryItem
)
from constants import (
    HTTP_OK,
    HTTP_NOT_FOUND
)

alarm_router = APIRouter()

@alarm_router.get("/alarms")
async def get_alarms(
    page: int = 1,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get alarms with pagination and filtering
    """
    # Generate mock alarms
    total_records = 100
    total_pages = (total_records + limit - 1) // limit
    
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_records)
    
    alarm_data = []
    statuses = ["active", "cleared", "warning"]
    risk_types = ["critical", "high", "medium", "low"]
    
    for i in range(start_idx, end_idx):
        alarm_status = status if status else random.choice(statuses)
        alarm_data.append(AlarmRecord(
            id=i+1,
            errorcode=f"ERR{random.randint(100, 999)}",
            description=f"Alarm {i+1} description",
            risktype=random.choice(risk_types),
            status=alarm_status,
            source=random.choice(["SCADA", "Turbine", "Network"]),
            sitename=f"Site-{random.randint(1, 5)}",
            occurred=datetime.now().isoformat(),
            cleared=datetime.now().isoformat() if alarm_status == "cleared" else None
        ))
    
    summary = AlarmSummary(
        total=total_records,
        active=random.randint(10, 30),
        warning=random.randint(5, 15),
        cleared=random.randint(40, 70),
        critical=random.randint(1, 5)
    )
    
    pagination = AlarmPagination(
        current_page=page,
        total_pages=total_pages,
        total_records=total_records,
        limit=limit
    )
    
    return AlarmResponse(
        success=True,
        server_timestamp=datetime.now().isoformat(),
        summary=summary,
        pagination=pagination,
        data=alarm_data
    )

@alarm_router.post("/alarms/acknowledge")
async def acknowledge_alarm(alarm_data: AlarmErrorFormModel, db: Session = Depends(get_db)):
    """
    Acknowledge and log alarm with resolution details
    """
    # TODO: Save alarm acknowledgment to database
    return {
        "success": True,
        "message": "Alarm acknowledged successfully",
        "data": {
            "turbine_name": alarm_data.turbine_name,
            "error_code": alarm_data.error_code,
            "acknowledged_by": alarm_data.acknowledged_by,
            "timestamp": datetime.now().isoformat()
        }
    }

@alarm_router.get("/alarms/turbine/{turbine_id}")
async def get_turbine_alarms(turbine_id: int, db: Session = Depends(get_db)):
    """
    Get alarm history for a specific turbine
    """
    # Generate mock alarm history for turbine
    alarm_codes = ["VIB001", "TMP001", "PWR001", "CTR001", "GRD001"]
    
    alarm_history = []
    for i in range(5):
        alarm_history.append(AlarmHistoryItem(
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat() if random.random() > 0.5 else None,
            deviation=round(random.uniform(0.5, 5.0), 2),
            risktype=random.choice(["critical", "high", "medium"]),
            acknowledged_by="admin" if random.random() > 0.3 else None
        ))
    
    return AlarmTurbineItem(
        alarm_code=random.choice(alarm_codes),
        description=f"Alarm for turbine {turbine_id}",
        risktype=random.choice(["critical", "high", "medium"]),
        start_time=datetime.now().isoformat(),
        end_time=None,
        turbine_name=f"Turbine-{turbine_id:03d}",
        model="WTG-2.1MW",
        location=f"Location-{random.randint(1, 10)}",
        system_affected="Vibration Monitoring System",
        parameter="Vibration Amplitude",
        measured_value=round(random.uniform(8, 15), 2),
        threshold_value=10.0,
        deviation=round(random.uniform(0.5, 5.0), 2),
        alarm_history=alarm_history
    )