"""
═══════════════════════════════════════════════════════════════════════
MAIN APPLICATION MODULE - COMPLETE WITH ALL ROUTES
═══════════════════════════════════════════════════════════════════════
"""

from typing import List, Dict
from datetime import datetime
import random

from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from config import settings
from constants import (
    APP_TITLE, APP_VERSION, APP_DESCRIPTION,
    SUCCESS_LOGIN, SUCCESS_OTP_SENT, SUCCESS_PASSWORD_RESET,
    SUCCESS_PROFILE_UPDATED,
    ERROR_INVALID_CREDENTIALS, ERROR_USER_NOT_FOUND,
    ERROR_INVALID_OTP, ERROR_PASSWORD_MISMATCH,
    TurbineStatus
)
from database import init_db, test_db_connection, get_db
from turbine_service import turbine_service
from helpers import generate_otp, validate_password
from email_service import email_service
from file_handler import file_handler
from models import (
    LoginModel, ForgotPassword, VerifyOTP, ResetPassword,
    UserType, SiteMaster, DGRRegister,
    DashboardResponse, DashboardSummary, TurbinesPage,
    TurbineItem, ActiveAlarmItem,
    TurbineOverviewFinalResponse, TurbineOverviewMainData,
    TurbineOverviewPagination, TurbineOverviewItem,
    ViewDetails, LiveData, PieChartData, PowerCurveData,
    AlarmResponse, AlarmRecord, AlarmSummary, AlarmPagination,
    AlarmErrorFormModel, AlarmTurbineItem, AlarmHistoryItem
)

# ═══════════════════════════════════════════════
# FASTAPI APPLICATION INITIALIZATION
# ═══════════════════════════════════════════════

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    contact={
        "name": "Wind Turbine Support Team",
        "email": "support@windturbine.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ═══════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════

cors_origins: List[str] = settings.get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════
# STATIC FILES
# ═══════════════════════════════════════════════

try:
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads"
    )
except Exception:
    pass

# ═══════════════════════════════════════════════
# GLOBAL EXCEPTION HANDLER
# ═══════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.is_development() else "An error occurred"
        }
    )

# ═══════════════════════════════════════════════
# STARTUP & SHUTDOWN
# ═══════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    test_db_connection()
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    pass

# ═══════════════════════════════════════════════
# TEMPORARY STORAGE FOR OTPs
# ═══════════════════════════════════════════════

otp_storage: Dict[str, dict] = {}

# ═════════════════════════════════════════════════════════════════════
# SYSTEM ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "environment": settings.APP_ENV
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "title": APP_TITLE,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# ═════════════════════════════════════════════════════════════════════
# AUTHENTICATION ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.post("/auth/login", tags=["Authentication"])
async def login(login_data: LoginModel, db: Session = Depends(get_db)):
    """Authenticate user with username/email and password"""
    if login_data.identifier == "admin" and login_data.password == "admin123":
        return {
            "success": True,
            "message": SUCCESS_LOGIN,
            "data": {
                "token": "mock_jwt_token",
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "role": login_data.role
                }
            }
        }
    raise HTTPException(status_code=401, detail=ERROR_INVALID_CREDENTIALS)

@app.post("/auth/get-otp", tags=["Authentication"])
async def get_otp(forgot_data: ForgotPassword, db: Session = Depends(get_db)):
    """Send OTP to user's email for password reset"""
    email = forgot_data.email
    if email:
        otp = generate_otp()
        otp_storage[email] = {"otp": otp}
        email_service.send_otp_email(email, otp)
        return {
            "success": True,
            "message": SUCCESS_OTP_SENT,
            "data": {"email": email}
        }
    raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)

@app.post("/auth/verify-otp", tags=["Authentication"])
async def verify_otp(verify_data: VerifyOTP, db: Session = Depends(get_db)):
    """Verify OTP sent to user's email"""
    email = verify_data.email
    otp = verify_data.otp
    stored_otp = otp_storage.get(email)
    
    if stored_otp and stored_otp["otp"] == otp:
        otp_storage[email]["verified"] = True
        return {
            "success": True,
            "message": "OTP verified successfully",
            "data": {"email": email}
        }
    raise HTTPException(status_code=400, detail=ERROR_INVALID_OTP)

@app.post("/auth/set-password", tags=["Authentication"])
async def set_password(reset_data: ResetPassword, db: Session = Depends(get_db)):
    """Set new password after OTP verification"""
    email = reset_data.email
    new_password = reset_data.new_password
    confirm_password = reset_data.confirm_password
    
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail=ERROR_PASSWORD_MISMATCH)
    
    password_error = validate_password(new_password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)
    
    stored_data = otp_storage.get(email)
    if not stored_data or not stored_data.get("verified"):
        raise HTTPException(status_code=400, detail="OTP not verified")
    
    otp_storage.pop(email, None)
    return {
        "success": True,
        "message": SUCCESS_PASSWORD_RESET,
        "data": {"email": email}
    }

@app.post("/auth/reset-password", tags=["Authentication"])
async def reset_password(reset_data: ResetPassword, db: Session = Depends(get_db)):
    """Reset password (combined OTP verification + password reset)"""
    return await set_password(reset_data, db)

@app.post("/auth/verify-password", tags=["Authentication"])
async def verify_password(login_data: LoginModel, db: Session = Depends(get_db)):
    """Verify user password"""
    if login_data.identifier == "admin" and login_data.password == "admin123":
        return {"success": True, "message": "Password verified successfully"}
    raise HTTPException(status_code=401, detail=ERROR_INVALID_CREDENTIALS)

# ═════════════════════════════════════════════════════════════════════
# DGR REGISTER (USER REGISTRATION) ENDPOINT
# ═════════════════════════════════════════════════════════════════════

@app.post("/post_dgrRegister", tags=["Authentication"])
def post_dgrRegister(
    request: DGRRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user (DGR Register)
    """
    if request.password != request.confirmPassword:
        raise HTTPException(
            status_code=400,
            detail="Password and Confirm Password do not match"
        )
    
    user_type = (
        db.query(UserType)
        .filter(UserType.id == request.userType)
        .first()
    )
    if not user_type:
        raise HTTPException(
            status_code=404,
            detail="Invalid User Type"
        )
    
    if user_type.usertype == "Site Person":
        if not request.siteName:
            raise HTTPException(
                status_code=400,
                detail="Site Name is mandatory for Site Person"
            )
    else:
        request.siteName = None
    
    query = text("""
        INSERT INTO tbl_usermaster
        (
            fullname,
            username,
            emailid,
            contactno,
            usertype_id,
            sitemaster_id,
            theme,
            photo,
            password,
            confirmpassword
        )
        VALUES
        (
            :fullname,
            :username,
            :emailid,
            :contactno,
            :usertype_id,
            :sitemaster_id,
            :theme,
            :photo,
            :password,
            :confirmpassword
        )
    """)
    
    db.execute(
        query,
        {
            "fullname": request.fullName,
            "username": request.userName,
            "emailid": request.emailId,
            "contactno": request.contactNo,
            "usertype_id": request.userType,
            "sitemaster_id": request.siteName,
            "theme": request.theme or "light",
            "photo": request.photoUpload,
            "password": request.password,
            "confirmpassword": request.confirmPassword
        }
    )
    db.commit()
    
    return {
        "status": True,
        "message": "User Registered Successfully"
    }

# ═════════════════════════════════════════════════════════════════════
# GET USERTYPE & GET SITENAME APIs
# ═════════════════════════════════════════════════════════════════════

@app.get("/get_usertype", tags=["Users"])
def get_usertype(db: Session = Depends(get_db)):
    """
    Get all user types from tbl_usertype
    """
    try:
        user_types = db.query(UserType).all()
        
        if not user_types:
            return {
                "status": False,
                "message": "No user types found",
                "data": []
            }
        
        result = []
        for ut in user_types:
            result.append({
                "id": ut.id,
                "usertype": ut.usertype
            })
        
        return {
            "status": True,
            "message": "User types retrieved successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user types: {str(e)}"
        )

@app.get("/get_sitename", tags=["Users"])
def get_sitename(db: Session = Depends(get_db)):
    """
    Get all site names from tbl_sitemaster
    """
    try:
        sites = db.query(SiteMaster).all()
        
        if not sites:
            return {
                "status": False,
                "message": "No sites found",
                "data": []
            }
        
        result = []
        for site in sites:
            result.append({
                "id": site.id,
                "sitename": site.sitename
            })
        
        return {
            "status": True,
            "message": "Site names retrieved successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving site names: {str(e)}"
        )

# ═════════════════════════════════════════════════════════════════════
# USERS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.get("/users/me", tags=["Users"])
async def get_current_user(db: Session = Depends(get_db)):
    """Get current user profile"""
    return {
        "success": True,
        "data": {
            "id": 1,
            "fullname": "Admin User",
            "username": "admin",
            "emailid": "admin@example.com",
            "contactno": "+1234567890",
            "usertype_id": 1,
            "sitemaster_id": 1,
            "theme": "light",
            "photo": "/uploads/profile_photos/default.jpg"
        }
    }

@app.put("/users/profile", tags=["Users"])
async def update_profile(
    fullname: str = None,
    emailid: str = None,
    contactno: str = None,
    theme: str = None,
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        photo_path = None
        
        if photo:
            is_valid, message = file_handler.validate_file(photo)
            if not is_valid:
                raise HTTPException(status_code=400, detail=message)
            photo_path = await file_handler.save_photo(photo)
            photo_path = f"/uploads/profile_photos/{photo_path.split('/')[-1]}"
        
        return {
            "success": True,
            "message": SUCCESS_PROFILE_UPDATED,
            "data": {
                "fullname": fullname or "Admin User",
                "emailid": emailid or "admin@example.com",
                "contactno": contactno or "+1234567890",
                "theme": theme or "light",
                "photo": photo_path or "/uploads/profile_photos/default.jpg"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating profile: {str(e)}"
        )

@app.get("/users/ip-history", tags=["Users"])
async def get_ip_history(db: Session = Depends(get_db)):
    """Get user's IP access history"""
    return {
        "success": True,
        "data": {
            "current_ip": "192.168.1.1",
            "history": [
                {
                    "ip": "192.168.1.1",
                    "timestamp": datetime.now().isoformat(),
                    "location": "Local Network"
                }
            ]
        }
    }

# ═════════════════════════════════════════════════════════════════════
# TURBINE ENDPOINTS (Direct)
# ═════════════════════════════════════════════════════════════════════

@app.get("/api/turbine/{turbine_id}", tags=["Turbines"])
async def get_turbine(turbine_id: int):
    """Get turbine metrics for a specific turbine"""
    return turbine_service.generate_metrics(turbine_id=turbine_id, capacity_mw=2.1)

@app.get("/api/turbine/{turbine_id}/power-curve", tags=["Turbines"])
async def power_curve(turbine_id: int):
    """Get power curve data for a specific turbine"""
    return turbine_service.generate_power_curve(2100)

@app.get("/api/turbine/{turbine_id}/downtime", tags=["Turbines"])
async def downtime(turbine_id: int):
    """Get downtime and energy data for a specific turbine"""
    metrics = turbine_service.generate_metrics(turbine_id=turbine_id, capacity_mw=2.1)
    return turbine_service.generate_downtime_energy(metrics)

# ═════════════════════════════════════════════════════════════════════
# TURBINES ROUTES
# ═════════════════════════════════════════════════════════════════════

@app.get("/turbines/list", tags=["Turbines"])
async def get_turbines(page: int = 1, limit: int = 50, db: Session = Depends(get_db)):
    """Get list of turbines with pagination"""
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

@app.get("/turbines/{turbine_id}/details", tags=["Turbines"])
async def get_turbine_details(turbine_id: int, db: Session = Depends(get_db)):
    """Get detailed turbine information"""
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

@app.get("/turbines/{turbine_id}/status", tags=["Turbines"])
async def get_turbine_status(turbine_id: int, db: Session = Depends(get_db)):
    """Get turbine current status"""
    status = turbine_service.update_turbine_status(turbine_id)
    return {
        "success": True,
        "data": {
            "turbine_id": turbine_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    }

@app.post("/turbines/{turbine_id}/reset", tags=["Turbines"])
async def reset_turbine(turbine_id: int, db: Session = Depends(get_db)):
    """Reset turbine and clear cache"""
    turbine_service.clear_cache(turbine_id)
    return {
        "success": True,
        "message": f"Turbine {turbine_id} reset successfully",
        "timestamp": datetime.now().isoformat()
    }

# ═════════════════════════════════════════════════════════════════════
# DASHBOARD ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.get("/dashboard/live-api", tags=["Dashboard"])
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get real-time dashboard data"""
    turbines = []
    total_power = 0
    running_count = 0
    stopped_count = 0
    miscomm_count = 0
    
    for i in range(1, 21):
        metrics = turbine_service.generate_metrics(i, 2.1)
        
        if metrics["status"] == TurbineStatus.RUNNING.value:
            running_count += 1
            total_power += metrics["active_power_kw"] / 1000
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
    
    turbines_page = TurbinesPage(data=turbines, total=len(turbines), page=1, limit=50)
    
    return DashboardResponse(
        summary=summary,
        turbines=turbines_page,
        active_alarms=active_alarms
    )

@app.get("/dashboard/turbine-overview", tags=["Dashboard"])
async def get_turbine_overview(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    """Get turbine overview with pagination"""
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

# ═════════════════════════════════════════════════════════════════════
# ALARMS ENDPOINTS
# ═════════════════════════════════════════════════════════════════════

@app.get("/alarms/alarms", tags=["Alarms"])
async def get_alarms(page: int = 1, limit: int = 50, status: str = None, db: Session = Depends(get_db)):
    """Get alarms with pagination and filtering"""
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

@app.post("/alarms/alarms/acknowledge", tags=["Alarms"])
async def acknowledge_alarm(alarm_data: AlarmErrorFormModel, db: Session = Depends(get_db)):
    """Acknowledge and log alarm with resolution details"""
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

@app.get("/alarms/alarms/turbine/{turbine_id}", tags=["Alarms"])
async def get_turbine_alarms(turbine_id: int, db: Session = Depends(get_db)):
    """Get alarm history for a specific turbine"""
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

# ═════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT
# ═════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.is_development(),
        log_level="debug"
    )