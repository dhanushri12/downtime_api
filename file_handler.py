"""
═══════════════════════════════════════════════════════════════════════
FILE HANDLER MODULE
═══════════════════════════════════════════════════════════════════════
Handles file uploads, validation, and storage operations.
"""

import os
import logging
from typing import Optional
from pathlib import Path

from fastapi import HTTPException, UploadFile

from config import settings
from constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from helpers import generate_uuid_hex

# ═══════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# DIRECTORY INITIALIZATION
# ═══════════════════════════════════════════════
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════
# FILE HANDLER CLASS
# ═══════════════════════════════════════════════


class FileHandler:
    """Handles file operations including upload and validation."""

    @staticmethod
    def validate_file(file: UploadFile) -> tuple[bool, str]:
        """
        Validate uploaded file.
        
        Args:
            file: FastAPI UploadFile object.
            
        Returns:
            Tuple of (is_valid: bool, message: str).
        """
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return False, f"Only {', '.join(ALLOWED_EXTENSIONS)} files allowed"

        return True, "Valid"

    @staticmethod
    async def save_photo(file: UploadFile) -> str:
        """
        Save uploaded photo file.
        
        Args:
            file: FastAPI UploadFile object.
            
        Returns:
            File path where photo was saved.
            
        Raises:
            HTTPException: If file is invalid or too large.
        """
        try:
            # Validate file
            is_valid, message = FileHandler.validate_file(file)
            if not is_valid:
                logger.warning(f"Invalid file upload: {message}")
                raise HTTPException(status_code=400, detail=message)

            # Read file contents
            contents = await file.read()

            # Check file size
            if len(contents) > MAX_FILE_SIZE:
                logger.warning(
                    f"File too large: {len(contents)} bytes, max {MAX_FILE_SIZE}"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Photo exceeds maximum allowed size (5MB)"
                )

            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1].lower()
            filename = f"{generate_uuid_hex()}{file_ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)

            logger.info(f"Photo saved successfully: {file_path}")
            return file_path

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving photo: {str(e)}")
            raise HTTPException(status_code=500, detail="Error saving file")

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            file_path: Path to file to delete.
            
        Returns:
            True if deletion successful, False otherwise.
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Path to file.
            
        Returns:
            True if file exists, False otherwise.
        """
        return os.path.exists(file_path)

    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file.
            
        Returns:
            File size in bytes, None if file doesn't exist.
        """
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception as e:
            logger.error(f"Error getting file size: {str(e)}")
            return None

    @staticmethod
    def get_all_uploads() -> list[str]:
        """
        Get list of all uploaded files.
        
        Returns:
            List of file paths in upload directory.
        """
        try:
            if os.path.exists(settings.UPLOAD_DIR):
                files = []
                for filename in os.listdir(settings.UPLOAD_DIR):
                    file_path = os.path.join(settings.UPLOAD_DIR, filename)
                    if os.path.isfile(file_path):
                        files.append(file_path)
                return files
            return []
        except Exception as e:
            logger.error(f"Error listing uploads: {str(e)}")
            return []


# ═══════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════
file_handler = FileHandler()
