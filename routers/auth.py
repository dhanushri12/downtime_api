"""
═══════════════════════════════════════════════════════════════════════
AUTHENTICATION ROUTES
═══════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict

from database import get_db
from models import LoginModel, ForgotPassword, VerifyOTP, ResetPassword
from constants import (
    SUCCESS_LOGIN,
    SUCCESS_OTP_SENT,
    SUCCESS_PASSWORD_RESET,
    ERROR_INVALID_CREDENTIALS,
    ERROR_USER_NOT_FOUND,
    ERROR_INVALID_OTP,
    ERROR_PASSWORD_MISMATCH
)
from helpers import generate_otp, validate_password
from email_service import email_service

auth_router = APIRouter()

# Temporary storage for OTPs (use Redis/DB in production)
otp_storage: Dict[str, dict] = {}

@auth_router.post("/login")
async def login(login_data: LoginModel, db: Session = Depends(get_db)):
    """
    Authenticate user with username/email and password
    """
    # TODO: Implement actual database validation
    # This is a mock implementation
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

@auth_router.post("/get-otp")
async def get_otp(forgot_data: ForgotPassword, db: Session = Depends(get_db)):
    """
    Send OTP to user's email for password reset
    """
    email = forgot_data.email
    
    # TODO: Check if email exists in database
    # For now, mock implementation
    if email:
        otp = generate_otp()
        otp_storage[email] = {"otp": otp}
        
        # Send OTP via email
        email_service.send_otp_email(email, otp)
        
        return {
            "success": True,
            "message": SUCCESS_OTP_SENT,
            "data": {"email": email}
        }
    raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)

@auth_router.post("/verify-otp")
async def verify_otp(verify_data: VerifyOTP, db: Session = Depends(get_db)):
    """
    Verify OTP sent to user's email
    """
    email = verify_data.email
    otp = verify_data.otp
    
    stored_otp = otp_storage.get(email)
    
    if stored_otp and stored_otp["otp"] == otp:
        # Mark OTP as verified
        otp_storage[email]["verified"] = True
        return {
            "success": True,
            "message": "OTP verified successfully",
            "data": {"email": email}
        }
    
    raise HTTPException(status_code=400, detail=ERROR_INVALID_OTP)

@auth_router.post("/set-password")
async def set_password(reset_data: ResetPassword, db: Session = Depends(get_db)):
    """
    Set new password after OTP verification
    """
    email = reset_data.email
    new_password = reset_data.new_password
    confirm_password = reset_data.confirm_password
    
    # Check if passwords match
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail=ERROR_PASSWORD_MISMATCH)
    
    # Validate password strength
    password_error = validate_password(new_password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)
    
    # Check if OTP was verified
    stored_data = otp_storage.get(email)
    if not stored_data or not stored_data.get("verified"):
        raise HTTPException(status_code=400, detail="OTP not verified")
    
    # TODO: Update password in database
    # Remove OTP after successful password reset
    otp_storage.pop(email, None)
    
    return {
        "success": True,
        "message": SUCCESS_PASSWORD_RESET,
        "data": {"email": email}
    }

@auth_router.post("/reset-password")
async def reset_password(reset_data: ResetPassword, db: Session = Depends(get_db)):
    """
    Reset password (combined OTP verification + password reset)
    """
    # Same as set_password but with additional validation
    return await set_password(reset_data, db)

@auth_router.post("/verify-password")
async def verify_password(login_data: LoginModel, db: Session = Depends(get_db)):
    """
    Verify user password (for additional security checks)
    """
    # TODO: Implement actual password verification
    if login_data.identifier == "admin" and login_data.password == "admin123":
        return {
            "success": True,
            "message": "Password verified successfully"
        }
    raise HTTPException(status_code=401, detail=ERROR_INVALID_CREDENTIALS)