"""
═══════════════════════════════════════════════════════════════════════
USERS ROUTES
═══════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import UserMaster
from file_handler import file_handler
from constants import SUCCESS_PROFILE_UPDATED

user_router = APIRouter()

@user_router.get("/me")
async def get_current_user(db: Session = Depends(get_db)):
    """
    Get current user profile
    """
    # TODO: Get user from JWT token
    # Mock user data
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

@user_router.put("/profile")
async def update_profile(
    fullname: str = None,
    emailid: str = None,
    contactno: str = None,
    theme: str = None,
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    # TODO: Implement actual profile update
    photo_path = None
    if photo:
        photo_path = await file_handler.save_photo(photo)
    
    return {
        "success": True,
        "message": SUCCESS_PROFILE_UPDATED,
        "data": {
            "fullname": fullname,
            "emailid": emailid,
            "contactno": contactno,
            "theme": theme,
            "photo": photo_path
        }
    }

@user_router.get("/ip-history")
async def get_ip_history(db: Session = Depends(get_db)):
    """
    Get user's IP access history
    """
    # TODO: Implement actual IP history
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