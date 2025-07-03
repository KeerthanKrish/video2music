"""Application configuration settings."""

from typing import List, Optional
import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Configuration
    app_name: str = "video2music"
    debug: bool = False
    
    # Supabase Configuration
    supabase_url: str = Field(default="https://aolcnzeoxiofkwbfuinz.supabase.co")
    supabase_anon_key: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvbGNuemVveGlvZmt3YmZ1aW56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1MzY5MTIsImV4cCI6MjA2NTExMjkxMn0.r3RRCoDKkGzjAhsWLK2YAHL1TJjatUT4PFsAS4DFzro")
    supabase_service_role_key: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvbGNuemVveGlvZmt3YmZ1aW56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTUzNjkxMiwiZXhwIjoyMDY1MTEyOTEyfQ.QKSQZD6XlaLpgIQjEyfahdoJUE0UeIakHutm38RvRmI")
    
    # Processing Configuration - Enable real processing when API keys are provided
    use_edge_functions: bool = Field(default=True)
    use_real_ai: bool = Field(default=False)  # Will be set to True when API keys are valid
    
    # JWT Configuration
    jwt_secret: str = "development-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Service APIs - Load from environment variables
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Spotify API Configuration - Load from environment variables
    spotify_client_id: str = Field(default="", env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(default="", env="SPOTIFY_CLIENT_SECRET")
    
    # Storage Configuration
    upload_max_size: int = Field(default=104857600)
    allowed_video_extensions: list[str] = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    
    # Processing Configuration
    max_frames_extract: int = 10
    frame_interval_seconds: float = 2.0
    audio_analysis_duration: int = 30
    
    # Development URLs
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # Application Settings
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"], env="CORS_ORIGINS"
    )

    # Processing Settings
    max_processing_time: int = Field(default=600, env="MAX_PROCESSING_TIME")
    enable_gpu: bool = Field(default=False, env="ENABLE_GPU")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-enable real AI if API keys are provided and valid
        has_gemini = (self.gemini_api_key and 
                     self.gemini_api_key != "your_gemini_api_key_here" and
                     self.gemini_api_key.startswith("AIza"))
        
        has_openai = (self.openai_api_key and 
                     self.openai_api_key != "your_openai_api_key_here" and
                     self.openai_api_key.startswith("sk-"))
        
        has_supabase = (self.supabase_service_role_key and 
                       self.supabase_service_role_key != "your_service_role_key_here" and
                       len(self.supabase_service_role_key) > 50)
        
        if (has_gemini or has_openai) and has_supabase:
            self.use_real_ai = True
            print("🎯 Real AI processing enabled!")
        elif has_supabase:
            self.use_real_ai = True  # Can still use enhanced simulation
            print("🧪 Enhanced simulation mode enabled")
        else:
            print("⚠️ Using basic simulation mode - add API keys for real AI processing")

    class Config:
        """Pydantic configuration."""

        env_file = ["backend.env", ".env"]  # Load from backend.env first, then .env
        case_sensitive = False
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 