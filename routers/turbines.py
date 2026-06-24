"""
═══════════════════════════════════════════════════════════════════════
TURBINES ROUTES
═══════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random

from database import get_db
from turbine_service import turbine_service

turbine_router = APIRouter()

@turbine_router.get("/list")
async def get_turbines(
    page: int = 1,
    limit: int = 50,
    site_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get list of turbines with pagination and filtering
    """
    # Generate mock turbine list
    total_turbines = 20
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, total_turbines)
    
    turbines = []
    for i in range(1, total_turbines + 1):
        metrics = turbine_service.generate_metrics(i, 2.1)
        turbines.append({
            "id": i,
            "name": f"Turbine-{i:03d}",
            "feeder": f"Feeder-{random.randint(1, 5)}",
            "site_id": random.randint(1, 5),
            "site_name": f"Site-{random.randint(1, 5)}",
            "status": metrics["status"],
            "capacity_mw": 2.1,
            "active_power_kw": metrics["active_power_kw"],
            "wind_speed_mps": metrics["wind_speed_mps"],
            "last_update": datetime.now().isoformat()
        })
    
    return {
        "success": True,
        "data": turbines[start_idx:end_idx],
        "total": total_turbines,
        "page": page,
        "limit": limit,
        "total_pages": (total_turbines + limit - 1) // limit
    }

@turbine_router.get("/{turbine_id}/details")
async def get_turbine_details(turbine_id: int, db: Session = Depends(get_db)):
    """
    Get detailed turbine information
    """
    metrics = turbine_service.generate_metrics(turbine_id, 2.1)
    
    return {
        "success": True,
        "data": {
            "id": turbine_id,
            "name": f"Turbine-{turbine_id:03d}",
            "model": "WTG-2.1MW",
            "capacity_mw": 2.1,
            "hub_height_m": 80.0,
            "rotor_diameter_m": 93.0,
            "commission_date": "2023-01-01",
            "status": metrics["status"],
            "metrics": metrics,
            "last_update": datetime.now().isoformat()
        }
    }

@turbine_router.get("/{turbine_id}/status")
async def get_turbine_status(turbine_id: int, db: Session = Depends(get_db)):
    """
    Get turbine current status
    """
    status = turbine_service.update_turbine_status(turbine_id)
    
    return {
        "success": True,
        "data": {
            "turbine_id": turbine_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    }

@turbine_router.post("/{turbine_id}/reset")
async def reset_turbine(turbine_id: int, db: Session = Depends(get_db)):
    """
    Reset turbine and clear cache
    """
    turbine_service.clear_cache(turbine_id)
    
    return {
        "success": True,
        "message": f"Turbine {turbine_id} reset successfully",
        "timestamp": datetime.now().isoformat()
    }