"""Tests for processing requests API routes."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.main import app
from app.models.requests import ProcessingStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user_id():
    """Mock user ID for testing."""
    return uuid4()


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = MagicMock()
    mock.auth.get_user.return_value.user.id = str(uuid4())
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": str(uuid4()), "email": "test@example.com"}
    ]
    return mock


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "mock-jwt-token"


class TestProcessingRequests:
    """Test cases for processing requests endpoints."""

    @patch("app.routes.requests.get_current_user_id")
    @patch("app.routes.requests.get_supabase_client")
    async def test_create_processing_request_success(
        self, mock_supabase_client, mock_get_user_id, client, mock_user_id
    ):
        """Test successful processing request creation."""
        # Setup mocks
        mock_get_user_id.return_value = mock_user_id
        mock_supabase = MagicMock()
        mock_supabase_client.return_value = mock_supabase
        
        # Mock storage upload
        mock_supabase.storage.from_.return_value.upload.return_value = {"error": None}
        
        # Mock database insert
        mock_request_data = {
            "id": str(uuid4()),
            "user_id": str(mock_user_id),
            "video_filename": "test.mp4",
            "status": ProcessingStatus.PENDING,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            mock_request_data
        ]

        # Create test video file
        test_video_content = b"fake video content"
        
        # Make request
        response = client.post(
            "/requests/",
            files={"video": ("test.mp4", test_video_content, "video/mp4")},
            data={"description": "Test video"},
            headers={"Authorization": "Bearer mock-token"},
        )

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["video_filename"].endswith(".mp4")
        assert response_data["status"] == ProcessingStatus.PENDING
        assert response_data["user_id"] == str(mock_user_id)

    @patch("app.routes.requests.get_current_user_id")
    def test_create_processing_request_invalid_file_type(
        self, mock_get_user_id, client, mock_user_id
    ):
        """Test processing request creation with invalid file type."""
        mock_get_user_id.return_value = mock_user_id
        
        # Create test non-video file
        test_content = b"fake text content"
        
        response = client.post(
            "/requests/",
            files={"video": ("test.txt", test_content, "text/plain")},
            headers={"Authorization": "Bearer mock-token"},
        )

        assert response.status_code == 400
        assert "File must be a video" in response.json()["detail"]

    @patch("app.routes.requests.get_current_user_id")
    @patch("app.services.requests.ProcessingRequestService.get_user_requests")
    async def test_get_user_requests_success(
        self, mock_get_user_requests, mock_get_user_id, client, mock_user_id
    ):
        """Test successful retrieval of user requests."""
        mock_get_user_id.return_value = mock_user_id
        
        # Mock service response
        mock_requests = [
            {
                "id": str(uuid4()),
                "user_id": str(mock_user_id),
                "video_filename": "test1.mp4",
                "status": ProcessingStatus.COMPLETED,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": str(uuid4()),
                "user_id": str(mock_user_id),
                "video_filename": "test2.mp4",
                "status": ProcessingStatus.PENDING,
                "created_at": "2024-01-01T01:00:00Z",
                "updated_at": "2024-01-01T01:00:00Z",
            },
        ]
        mock_get_user_requests.return_value = mock_requests

        response = client.get(
            "/requests/",
            headers={"Authorization": "Bearer mock-token"},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["video_filename"] == "test1.mp4"

    @patch("app.routes.requests.get_current_user_id")
    @patch("app.services.requests.ProcessingRequestService.get_request_by_id")
    async def test_get_request_by_id_success(
        self, mock_get_request_by_id, mock_get_user_id, client, mock_user_id
    ):
        """Test successful retrieval of specific request."""
        mock_get_user_id.return_value = mock_user_id
        request_id = uuid4()
        
        # Mock service response
        mock_request = {
            "id": str(request_id),
            "user_id": str(mock_user_id),
            "video_filename": "test.mp4",
            "status": ProcessingStatus.COMPLETED,
            "result": {
                "recommendations": [
                    {
                        "title": "Test Song",
                        "artist": "Test Artist",
                        "genre": "Test Genre",
                        "mood": "happy",
                        "energy_level": 0.8,
                        "valence": 0.9,
                        "confidence_score": 0.95,
                    }
                ]
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z",
        }
        mock_get_request_by_id.return_value = mock_request

        response = client.get(
            f"/requests/{request_id}",
            headers={"Authorization": "Bearer mock-token"},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(request_id)
        assert response_data["status"] == ProcessingStatus.COMPLETED
        assert len(response_data["result"]["recommendations"]) == 1

    @patch("app.routes.requests.get_current_user_id")
    @patch("app.services.requests.ProcessingRequestService.get_request_by_id")
    async def test_get_request_by_id_not_found(
        self, mock_get_request_by_id, mock_get_user_id, client, mock_user_id
    ):
        """Test request not found scenario."""
        mock_get_user_id.return_value = mock_user_id
        request_id = uuid4()
        
        # Mock service returning None (not found)
        mock_get_request_by_id.return_value = None

        response = client.get(
            f"/requests/{request_id}",
            headers={"Authorization": "Bearer mock-token"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_upload_without_auth(self, client):
        """Test upload endpoint without authentication."""
        test_video_content = b"fake video content"
        
        response = client.post(
            "/requests/",
            files={"video": ("test.mp4", test_video_content, "video/mp4")},
            # No Authorization header
        )

        assert response.status_code == 401

    @patch("app.routes.requests.get_current_user_id")
    @patch("app.routes.requests.get_supabase_client")
    async def test_create_processing_request_storage_error(
        self, mock_supabase_client, mock_get_user_id, client, mock_user_id
    ):
        """Test handling of storage upload error."""
        mock_get_user_id.return_value = mock_user_id
        mock_supabase = MagicMock()
        mock_supabase_client.return_value = mock_supabase
        
        # Mock storage upload failure
        mock_supabase.storage.from_.return_value.upload.return_value = {
            "error": "Storage error"
        }

        test_video_content = b"fake video content"
        
        response = client.post(
            "/requests/",
            files={"video": ("test.mp4", test_video_content, "video/mp4")},
            headers={"Authorization": "Bearer mock-token"},
        )

        assert response.status_code == 500
        assert "Failed to upload video" in response.json()["detail"]


class TestProcessingRequestService:
    """Test cases for ProcessingRequestService."""

    @pytest.fixture
    def service(self):
        """Create service instance with mock Supabase client."""
        mock_supabase = MagicMock()
        from app.services.requests import ProcessingRequestService
        return ProcessingRequestService(mock_supabase)

    async def test_enqueue_processing_job(self, service):
        """Test job enqueueing."""
        request_id = uuid4()
        video_filename = "test.mp4"
        
        # Mock the database insert
        service.supabase.table.return_value.insert.return_value.execute.return_value = True

        await service._enqueue_processing_job(request_id, video_filename)

        # Verify job was inserted
        service.supabase.table.assert_called_with("processing_jobs")

    async def test_update_request_status(self, service):
        """Test status update."""
        request_id = uuid4()
        
        await service.update_request_status(
            request_id, ProcessingStatus.COMPLETED
        )

        # Verify update was called
        service.supabase.table.return_value.update.assert_called()
        service.supabase.table.return_value.update.return_value.eq.assert_called_with(
            "id", str(request_id)
        ) 