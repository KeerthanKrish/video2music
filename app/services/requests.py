"""Processing request service with business logic."""

import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from supabase import Client

from ..models.requests import (
    ProcessingRequest,
    ProcessingRequestCreate,
    ProcessingRequestResponse,
    ProcessingStatus,
)


class ProcessingRequestService:
    """Service for managing processing requests."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_request(
        self, user_id: UUID, request_data: ProcessingRequestCreate
    ) -> ProcessingRequestResponse:
        """Create a new processing request."""
        request_id = uuid.uuid4()
        now = datetime.utcnow()

        # Store request in database
        request_dict = {
            "id": str(request_id),
            "user_id": str(user_id),
            "video_filename": request_data.video_filename,
            "video_content_type": request_data.video_content_type,
            "status": ProcessingStatus.PENDING,
            "description": request_data.description,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        response = self.supabase.table("processing_requests").insert(request_dict).execute()

        if not response.data:
            raise Exception("Failed to create processing request")

        # Enqueue processing job
        await self._enqueue_processing_job(request_id, request_data.video_filename)

        return ProcessingRequestResponse(**response.data[0])

    async def get_user_requests(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[ProcessingRequestResponse]:
        """Get processing requests for a user."""
        response = (
            self.supabase.table("processing_requests")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return [ProcessingRequestResponse(**item) for item in response.data]

    async def get_request_by_id(
        self, request_id: UUID, user_id: UUID
    ) -> Optional[ProcessingRequestResponse]:
        """Get a specific processing request by ID."""
        response = (
            self.supabase.table("processing_requests")
            .select("*")
            .eq("id", str(request_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        if not response.data:
            return None

        return ProcessingRequestResponse(**response.data[0])

    async def update_request_status(
        self, request_id: UUID, status: ProcessingStatus, error_message: Optional[str] = None
    ) -> None:
        """Update processing request status."""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }

        if error_message:
            update_data["error_message"] = error_message

        if status == ProcessingStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow().isoformat()

        self.supabase.table("processing_requests").update(update_data).eq(
            "id", str(request_id)
        ).execute()

    async def _enqueue_processing_job(self, request_id: UUID, video_filename: str) -> None:
        """Enqueue processing job in Supabase queue."""
        job_data = {
            "request_id": str(request_id),
            "video_filename": video_filename,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Insert into job queue table
        self.supabase.table("processing_jobs").insert(job_data).execute()

        # Note: In a real implementation, you might also trigger the Edge Function
        # or use Supabase's built-in queue functionality 