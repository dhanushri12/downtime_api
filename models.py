# models.py - Add at top
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base

class SiteMaster(Base):
    __tablename__ = "tbl_sitemaster"

    id = Column(Integer, primary_key=True, index=True)
    sitename = Column(String(100))

class Theme(Base):
    __tablename__ = "tbl_theme"

    id = Column(Integer, primary_key=True, index=True)
    themename = Column(String(100))\
    
class UserMaster(Base):
    __tablename__ = "tbl_usermaster"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100))
    username = Column(String(100))
    emailid = Column(String(255), unique=True)
    contactno = Column(String(100))
    usertype_id = Column(Integer)
    sitemaster_id = Column(Integer)
    theme = Column(String(50))
    photo = Column(String(100))
    password = Column(String(255))
    confirmpassword = Column(String(255))

class UserType(Base):
    __tablename__ = "tbl_usertype"

    id = Column(Integer, primary_key=True, index=True)
    usertype = Column(String(100))


# ═══════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════
class LiveData(BaseModel):
    turbine_name: str
    active_power_kw: float
    reactive_power_kvar: float
    voltage_v: float
    current_a: float
    frequency_hz: float
    power_factor: float
    rotor_speed_rpm: float
    generator_speed_rpm: float
    wind_speed_mps: float
    wind_direction_deg: float
    ambient_temperature_c: float
    hub_temperature_c: float
    yaw_position_deg: float
    hydraulic_pressure_bar: float
    brake_status: str
    grid_synchronization: str
    ip: Optional[str] = None
    site_name: Optional[str] = None

class DGRRegister(BaseModel):
    fullName: str
    userName: str
    emailId: str
    contactNo: str
    userType: int
    siteName: Optional[int] = None
    theme: Optional[str] = "light"
    photoUpload: Optional[str] = None
    password: str
    confirmPassword: str

class DowntimeEnergy(BaseModel):
    ma: float
    iga: float
    ega: float
    total_downtime: float
    energy_today_kwh: float
    power_curve: float

class FeederItem(BaseModel):
    id: int
    turbine_name: str
    ip: str
    feeder: str
    site_name: str
    state: str
    status: str
    active_power_kw: float
    reactive_power_kvar: float
    wind_speed_mps: float
    wind_direction_deg: float
    rotor_speed_rpm: float
    temperature_c: float
    pitch_angle_1: float
    pitch_angle_2: float
    pitch_angle_3: float
    plf_pct: float
    alarm_code: Optional[str]
    live_data: LiveData
    downtime_and_energy: DowntimeEnergy

class TurbineCountData(BaseModel):
    total_turbine: int
    running: int
    stopped: int
    miscommunication: int
    active_alarm: int
    installed_capacity_mw: float
    total_active_generation_power_mw: float
    avg_wind_speed_mps: float
    plf_pct: float



class LoginModel(BaseModel):
    identifier: str
    password: str
    captcha_id: str
    captcha_text: str
    role: str

class ForgotPassword(BaseModel):
    email: str

class VerifyOTP(BaseModel):
    email: str
    otp: str

class ResetPassword(BaseModel):
    email: str
    new_password: str
    confirm_password: str

class AlarmRecord(BaseModel):
    id: int
    errorcode: str
    description: str
    risktype: str
    status: str
    source: str
    sitename: Optional[str]
    occurred: Optional[str]
    cleared: Optional[str]

class AlarmSummary(BaseModel):
    total: int
    active: int
    warning: int
    cleared: int
    critical: int

class AlarmPagination(BaseModel):
    current_page: int
    total_pages: int
    total_records: int
    limit: int

class AlarmResponse(BaseModel):
    success: bool
    server_timestamp: str
    summary: AlarmSummary
    pagination: AlarmPagination
    data: List[AlarmRecord]

class DashboardSummary(BaseModel):
    total_turbines: int
    running_turbines: int
    stopped_turbines: int
    active_alarms: int
    total_power_mw: float
    avg_wind_speed_mps: float

class TurbineItem(BaseModel):
    id: int
    name: str
    feeder: str
    status: str
    active_power_kw: float
    reactive_power_kvar: float
    wind_speed_mps: float
    rotor_speed_rpm: float
    temperature_c: float
    pitch_angle_1: float
    pitch_angle_2: float
    pitch_angle_3: float

class TurbinesPage(BaseModel):
    data: List[TurbineItem]
    total: int
    page: int
    limit: int

class ActiveAlarmItem(BaseModel):
    alarm_id: int
    turbine_name: str
    error_code: str
    description: str
    risk_type: str
    occurred_datetime: str

class DashboardResponse(BaseModel):
    summary: DashboardSummary
    turbines: TurbinesPage
    active_alarms: List[ActiveAlarmItem]

class AlarmErrorFormModel(BaseModel):
    turbine_name: str
    error_code: str
    possible_cause: str
    recommended_action: str
    acknowledged_by: str
    comments: Optional[str] = None
    
class AlarmHistoryItem(BaseModel):
    start_time: Optional[str]
    end_time: Optional[str]
    deviation: float
    risktype: str
    acknowledged_by: Optional[str]
    
class AlarmTurbineItem(BaseModel):
    alarm_code: str
    description: str
    risktype: str
    start_time: Optional[str]
    end_time: Optional[str]
    turbine_name: str
    model: str
    location: str
    system_affected: str
    parameter: str
    measured_value: float
    threshold_value: float
    deviation: float
    alarm_history: List[AlarmHistoryItem]
    
class PieChartData(BaseModel):
    active_power_kw: float
    reactive_power_kvar: float
    wind_speed_mps: float
    rotor_speed_rpm: float

class PowerCurvePoint(BaseModel):
    wind_speed: float
    power_kw: float

class PowerCurveData(BaseModel):
    turbine_id: int
    energy_today_kwh: float
    turbine_status: str
    downtime: dict
    graph: List[PowerCurvePoint]

class ViewDetails(BaseModel):
    id: int
    turbine_name: str
    ip: str
    feeder: str
    active_power_kw: float
    reactive_power_kvar: float
    wind_speed_mps: float
    plf_pct: float
    rotor_speed_rpm: float
    wind_direction: str
    temperature_c: float
    alarm_code: Optional[str]
    alarm_description: Optional[str]
    turbine_status: str
    model: str
    hub_height_m: float
    capacity_mw: float
    commission_date: str
    site_name: str
    location: str
    last_update_data: str

class TurbineOverviewItem(BaseModel):
    id: int
    turbine_name: str
    feeder: str
    status: str
    active_power_kw: float
    wind_speed_mps: float
    rotor_speed_rpm: float
    temperature_c: float
    plf_pct: float
    pitch_angle_1: float
    pitch_angle_2: float
    pitch_angle_3: float
    error_code: Optional[str] = None
    ip: Optional[str] = None
    sitename: Optional[str] = None
    power_generation: Optional[float] = None
    view_details: ViewDetails
    live_data: LiveData
    piechart: PieChartData
    powercurve: PowerCurveData

class TurbineOverviewPagination(BaseModel):
    data: List[TurbineOverviewItem]
    total: int
    page: int
    limit: int

class TurbineOverviewMainData(BaseModel):
    total_turbine: int
    running: int
    stopped: int
    miscommunication: int
    active_alarm: int
    installed_capacity_mw: float
    total_power_generation_mw: float
    total_plf: float
    avg_wind_speed_mps: float

class TurbineOverviewFinalResponse(BaseModel):
    status: str
    server_timestamp: str
    data: TurbineOverviewMainData
    turbines: TurbineOverviewPagination

class MachineAvailability(BaseModel):
    available_hours: float
    unavailable_hours: float
    availability_pct: float    
