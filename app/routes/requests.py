"""API routes for processing requests."""

import logging
from typing import List, Dict, Any
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from app.auth import get_current_user, require_user_access
from app.services.supabase_client import supabase_service
from app.models.requests import ProcessingRequestResponse, ProcessingRequestCreate
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("/", response_model=ProcessingRequestResponse)
async def create_processing_request(
    video_file: UploadFile = File(...),
    description: str = Form(None),
    music_year_start: int = Form(1980),
    music_year_end: int = Form(2024),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ProcessingRequestResponse:
    """
    Create a new video processing request with music preferences.
    
    This endpoint:
    1. Validates the uploaded video file
    2. Uploads it to Supabase Storage  
    3. Creates a processing request record
    4. Enqueues the processing job
    5. Returns the request details
    """
    logger.info(f"Creating processing request for user: {current_user['id']}")
    logger.info(f"Music year preferences: {music_year_start}-{music_year_end}")
    
    # Validate year range
    current_year = datetime.now().year
    if music_year_start < 1950 or music_year_start > current_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid start year. Must be between 1950 and {current_year}"
        )
    
    if music_year_end < 1950 or music_year_end > current_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid end year. Must be between 1950 and {current_year}"
        )
    
    if music_year_start > music_year_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start year cannot be greater than end year"
        )

    try:
        # Validate file
        if not video_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        file_extension = "." + video_file.filename.split(".")[-1].lower()
        if file_extension not in settings.allowed_video_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {settings.allowed_video_extensions}"
            )
        
        # Check file size
        file_content = await video_file.read()
        if len(file_content) > settings.upload_max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.upload_max_size / 1024 / 1024}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid4())
        file_path = f"videos/{current_user['id']}/{file_id}_{video_file.filename}"
        
        # Upload to Supabase Storage
        video_url = await supabase_service.upload_file(
            bucket="videos",
            file_path=file_path,
            file_content=file_content,
            content_type=video_file.content_type or "video/mp4"
        )
        
        if not video_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload video file"
            )
        
        # Create processing request in database with music preferences
        request_data = await supabase_service.create_processing_request(
            user_id=current_user["id"],
            video_filename=video_file.filename,
            video_url=video_url,
            description=description,
            music_year_start=music_year_start,
            music_year_end=music_year_end
        )
        
        if not request_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create processing request"
            )
        
        # Enqueue processing job with enhanced context
        job_enqueued = await supabase_service.enqueue_processing_job(
            request_id=request_data["id"],
            video_url=video_url,
            description=description,
            music_year_start=music_year_start,
            music_year_end=music_year_end
        )
        
        if not job_enqueued:
            logger.warning(f"Failed to enqueue processing job for request {request_data['id']}")
            # Update status to failed
            await supabase_service.update_request_status(
                request_id=request_data["id"],
                status="failed",
                error_message="Failed to start processing pipeline"
            )
        
        logger.info(f"Created processing request: {request_data['id']}")
        return ProcessingRequestResponse(**request_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[ProcessingRequestResponse])
async def get_user_requests(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[ProcessingRequestResponse]:
    """
    Get all processing requests for the current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of user's processing requests
    """
    try:
        requests = await supabase_service.get_user_requests(current_user["id"])
        return [ProcessingRequestResponse(**request) for request in requests]
        
    except Exception as e:
        logger.error(f"Failed to get user requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requests"
        )

@router.get("/{request_id}", response_model=ProcessingRequestResponse)
async def get_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ProcessingRequestResponse:
    """
    Get a specific processing request by ID.
    
    Args:
        request_id: Processing request ID
        current_user: Current authenticated user
        
    Returns:
        Processing request details
        
    Raises:
        HTTPException: If request not found or access denied
    """
    try:
        request_data = await supabase_service.get_request_by_id(
            request_id=request_id,
            user_id=current_user["id"]
        )
        
        if not request_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing request not found"
            )
        
        return ProcessingRequestResponse(**request_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve request"
        )

@router.delete("/{request_id}")
async def delete_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a processing request (only if pending).
    
    Args:
        request_id: Processing request ID
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If request not found, access denied, or cannot be deleted
    """
    try:
        # Get request to verify ownership and status
        request_data = await supabase_service.get_request_by_id(
            request_id=request_id,
            user_id=current_user["id"]
        )
        
        if not request_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing request not found"
            )
        
        # Only allow deletion of pending requests
        if request_data["status"] not in ["pending", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete request that is processing or completed"
            )
        
        # Update status to cancelled
        success = await supabase_service.update_request_status(
            request_id=request_id,
            status="cancelled"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel request"
            )
        
        logger.info(f"Cancelled processing request: {request_id}")
        return {"message": "Request cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel request"
        ) 