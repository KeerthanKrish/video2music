"""Supabase client service for database and storage operations."""

import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from gotrue.errors import AuthError
from app.config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service class for Supabase operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        self.anon_client: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        
    async def authenticate_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with JWT token."""
        try:
            response = self.client.auth.get_user(token)
            return response.user.model_dump() if response.user else None
        except AuthError as e:
            logger.error(f"Authentication failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            return None
    
    async def create_processing_request(
        self, 
        user_id: str, 
        video_filename: str,
        video_url: str,
        description: Optional[str] = None,
        music_year_start: Optional[int] = None,
        music_year_end: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new processing request in the database with music preferences."""
        try:
            request_data = {
                "user_id": user_id,
                "video_filename": video_filename,
                "video_url": video_url,
                "status": "pending",
                "description": description,
                "music_year_start": music_year_start,
                "music_year_end": music_year_end
            }
            
            response = self.client.table("processing_requests").insert(request_data).execute()
            
            if response.data:
                logger.info(f"Created processing request: {response.data[0]['id']}")
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to create processing request: {e}")
            return None
    
    async def get_user_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all processing requests for a user."""
        try:
            response = self.client.table("processing_requests")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Failed to get user requests: {e}")
            return []
    
    async def get_request_by_id(self, request_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific processing request by ID."""
        try:
            response = self.client.table("processing_requests")\
                .select("*")\
                .eq("id", request_id)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            logger.error(f"Failed to get request {request_id}: {e}")
            return None
    
    async def update_request_status(
        self,
        request_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update processing request status and results."""
        try:
            update_data = {"status": status, "updated_at": "now()"}
            
            if result:
                update_data["result"] = result
                
            if error_message:
                update_data["error_message"] = error_message
                
            if status == "completed":
                update_data["completed_at"] = "now()"
            
            response = self.client.table("processing_requests")\
                .update(update_data)\
                .eq("id", request_id)\
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update request {request_id}: {e}")
            return False
    
    async def upload_file(
        self, 
        bucket: str, 
        file_path: str, 
        file_content: bytes,
        content_type: str = "video/mp4"
    ) -> Optional[str]:
        """Upload file to Supabase Storage."""
        try:
            response = self.client.storage.from_(bucket).upload(
                file_path, 
                file_content,
                file_options={"content-type": content_type}
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket).get_public_url(file_path)
                logger.info(f"File uploaded successfully: {public_url}")
                return public_url
            return None
            
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    async def get_file_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Get public URL for a file in Supabase Storage."""
        try:
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Failed to get file URL for {file_path}: {e}")
            return None
    
    async def enqueue_processing_job(
        self, 
        request_id: str, 
        video_url: str,
        description: Optional[str] = None,
        music_year_start: Optional[int] = None,
        music_year_end: Optional[int] = None
    ) -> bool:
        """Enqueue a processing job by calling the Edge Function."""
        try:
            # Check if we should use real AI processing
            if settings.use_real_ai and settings.use_edge_functions:
                logger.info(f"🎯 Starting REAL AI processing for request: {request_id}")
                
                # Prepare the request body with user preferences
                request_body = {
                    "request_id": request_id,
                    "video_url": video_url
                }
                
                # Add optional parameters if provided
                if description:
                    request_body["description"] = description
                if music_year_start is not None:
                    request_body["music_year_start"] = music_year_start
                if music_year_end is not None:
                    request_body["music_year_end"] = music_year_end
                
                # Call the actual Edge Function
                response = self.client.functions.invoke(
                    "video-processor",
                    invoke_options={
                        "body": request_body
                    }
                )
                
                # Handle response - it might be bytes or dict
                if isinstance(response, bytes):
                    try:
                        import json
                        response_data = json.loads(response.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        logger.error(f"Failed to parse Edge Function response: {e}")
                        await self.update_request_status(
                            request_id=request_id,
                            status="failed",
                            error_message=f"Invalid response format: {str(e)}"
                        )
                        return False
                else:
                    response_data = response
                
                if response_data and response_data.get("error"):
                    logger.error(f"Edge function error: {response_data['error']}")
                    # Update status to failed
                    await self.update_request_status(
                        request_id=request_id,
                        status="failed",
                        error_message=f"Edge function error: {response_data['error']}"
                    )
                    return False
                elif response_data and response_data.get("success"):
                    logger.info(f"✅ Real AI processing completed for request: {request_id}")
                    return True
                else:
                    logger.warning(f"Unexpected Edge Function response: {response_data}")
                    return True  # Continue anyway, Edge Function updates database directly
            
            # Fallback to simulation mode
            logger.info(f"🧪 Simulating processing for request: {request_id} (real AI not configured)")
            
            # Simulate processing delay
            import asyncio
            await asyncio.sleep(2)
            
            # Update status to processing
            await self.update_request_status(
                request_id=request_id,
                status="processing"
            )
            
            # Simulate completion after a short delay
            await asyncio.sleep(3)
            
            # Create unique simulation results based on video characteristics
            mock_result = self._generate_unique_simulation_result(request_id, video_url)
            
            # Update status to completed
            await self.update_request_status(
                request_id=request_id,
                status="completed",
                result=mock_result
            )
            
            logger.info(f"🧪 Simulated processing completed for request: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enqueue processing job: {e}")
            # Update status to failed
            await self.update_request_status(
                request_id=request_id,
                status="failed",
                error_message=f"Processing failed: {str(e)}"
            )
            return False
            
    def _generate_unique_simulation_result(self, request_id: str, video_url: str) -> dict:
        """Generate unique simulation results based on video characteristics."""
        import hashlib
        import time
        
        # Create hashes for uniqueness
        video_hash = int(hashlib.md5(request_id[-8:].encode()).hexdigest()[:8], 16)
        url_hash = sum(ord(c) for c in video_url)
        combined_hash = video_hash + url_hash
        
        # Generate unique frame count and names
        frame_count = 4 + (combined_hash % 4)  # 4-7 frames
        timestamp = int(time.time())
        extracted_frames = [
            f"{request_id}_frame_{str(i+1).zfill(3)}_{timestamp + i}.jpg" 
            for i in range(frame_count)
        ]
        
        # Generate unique ambient tags
        tag_categories = [
            ["Music", "Instruments", "Melody", "Harmony"],
            ["Nature", "Birds", "Wind", "Water", "Outdoor"],
            ["Urban", "Traffic", "City", "Voices", "Street"],
            ["Indoor", "Conversation", "Footsteps", "Ambient", "Room"],
            ["Electronic", "Synthesizer", "Digital", "Technology"],
            ["Celebration", "Laughter", "Applause", "Joy", "Party"],
            ["Peaceful", "Calm", "Meditation", "Quiet", "Serene"],
            ["Energetic", "Movement", "Activity", "Dynamic", "Vibrant"]
        ]
        
        category_index = combined_hash % len(tag_categories)
        ambient_tags = tag_categories[category_index][:3 + (combined_hash % 2)]
        
        # Generate unique visual elements
        visual_base = [
            "Lighting", "Color Dynamics", "Movement Patterns", "Composition", 
            "Depth", "Texture", "Contrast", "Perspective", "Focus"
        ]
        visual_context = [
            "Cinematic Flow", "Natural Beauty", "Rhythmic Motion", "Organic Shapes",
            "Geometric Forms", "Atmospheric Depth", "Character Interaction", "Environmental Context"
        ]
        
        visual_elements = []
        for i in range(4):
            if i < 2:
                idx = (combined_hash + i * 7) % len(visual_base)
                visual_elements.append(visual_base[idx])
            else:
                idx = (combined_hash + i * 11) % len(visual_context)
                visual_elements.append(visual_context[idx])
        
        # Enhanced mood generation with more variety
        mood_options = [
            "Energetic and Vibrant", "Calm and Contemplative", "Dramatic and Intense",
            "Playful and Lighthearted", "Mysterious and Intriguing", "Warm and Inviting",
            "Cool and Professional", "Nostalgic and Reflective", "Adventurous and Bold",
            "Romantic and Dreamy", "Suspenseful and Tense", "Uplifting and Inspiring",
            "Melancholic and Thoughtful", "Chaotic and Energetic", "Serene and Peaceful",
            "Dark and Moody", "Bright and Cheerful", "Sophisticated and Elegant",
            "Raw and Authentic", "Futuristic and Modern", "Whimsical and Creative"
        ]
        
        # Use multiple factors for mood selection to ensure variety
        mood_index = (combined_hash * 3 + video_hash + url_hash) % len(mood_options)
        mood = mood_options[mood_index]
        
        # Enhanced scene description templates for more variety
        description_templates = [
            f"Captivating {frame_count}-frame sequence with {mood.lower()} undertones. Audio features {', '.join(ambient_tags[:2]).lower()} elements while visuals emphasize {', '.join(visual_elements[:2]).lower()} throughout the composition.",
            f"Rich visual narrative spanning {frame_count} distinct moments, characterized by {mood.lower()} energy. The footage highlights {', '.join(visual_elements[:2]).lower()} complemented by {', '.join(ambient_tags[:2]).lower()} soundscape.",
            f"Compelling video analysis revealing {frame_count} key frames with {mood.lower()} atmosphere. Content showcases {', '.join(visual_elements[:2]).lower()} enhanced by {', '.join(ambient_tags[:2]).lower()} audio signature."
        ]
        
        description_index = (video_hash + combined_hash) % len(description_templates)
        scene_description = description_templates[description_index]
        
        # Generate unique transcription
        transcription_variants = [
            f"Audio analysis of video {request_id[-6:]} reveals {ambient_tags[0].lower()} elements with varied tonal qualities.",
            f"Voice and environmental audio detected in sequence {request_id[-6:]} with {ambient_tags[0].lower()} characteristics.",
            f"Complex audio landscape in video {request_id[-6:]} featuring {ambient_tags[0].lower()} components and ambient soundscape."
        ]
        
        transcription = transcription_variants[combined_hash % len(transcription_variants)]
        
        # Enhanced unique music recommendations with larger database
        music_database = [
            {"title": "Dynamic Rhythm", "artist": "Pulse Collective", "genre": "Electronic", "mood": "Energetic", "energy": 0.85, "valence": 0.9},
            {"title": "Serene Flow", "artist": "Ambient Waters", "genre": "Ambient", "mood": "Calm", "energy": 0.25, "valence": 0.7},
            {"title": "Urban Beats", "artist": "City Pulse", "genre": "Hip-Hop", "mood": "Urban", "energy": 0.8, "valence": 0.75},
            {"title": "Natural Harmony", "artist": "Organic Sound", "genre": "Folk", "mood": "Peaceful", "energy": 0.4, "valence": 0.8},
            {"title": "Cinematic Journey", "artist": "Epic Sounds", "genre": "Orchestral", "mood": "Dramatic", "energy": 0.9, "valence": 0.6},
            {"title": "Contemplative Space", "artist": "Mindful Tones", "genre": "Neo-Classical", "mood": "Reflective", "energy": 0.3, "valence": 0.65},
            {"title": "Vibrant Energy", "artist": "Colorful Beats", "genre": "Dance", "mood": "Joyful", "energy": 0.95, "valence": 0.92},
            {"title": "Mysterious Depths", "artist": "Shadow Music", "genre": "Dark Ambient", "mood": "Mysterious", "energy": 0.4, "valence": 0.35},
            {"title": "Sunset Vibes", "artist": "Golden Hour", "genre": "Chill Pop", "mood": "Warm", "energy": 0.6, "valence": 0.8},
            {"title": "Digital Dreams", "artist": "Synth Collective", "genre": "Synthwave", "mood": "Futuristic", "energy": 0.7, "valence": 0.7},
            {"title": "Mountain Echo", "artist": "Valley Sounds", "genre": "Acoustic", "mood": "Nature", "energy": 0.5, "valence": 0.75},
            {"title": "Night Drive", "artist": "Midnight Express", "genre": "Electronic Rock", "mood": "Adventurous", "energy": 0.85, "valence": 0.65},
            {"title": "Coffee Shop Melody", "artist": "Café Musicians", "genre": "Jazz", "mood": "Cozy", "energy": 0.4, "valence": 0.8},
            {"title": "Ocean Waves", "artist": "Seaside Harmony", "genre": "Ambient Nature", "mood": "Tranquil", "energy": 0.2, "valence": 0.9},
            {"title": "City Lights", "artist": "Metro Vibes", "genre": "Lo-Fi Hip Hop", "mood": "Modern", "energy": 0.6, "valence": 0.6},
            {"title": "Storm Brewing", "artist": "Thunder Collective", "genre": "Dark Rock", "mood": "Intense", "energy": 0.95, "valence": 0.3},
            {"title": "Pixel Perfect", "artist": "Retro Gaming", "genre": "Chiptune", "mood": "Playful", "energy": 0.8, "valence": 0.9},
            {"title": "Forest Path", "artist": "Woodland Ensemble", "genre": "Celtic", "mood": "Mystical", "energy": 0.5, "valence": 0.7}
        ]
        
        # Use a more sophisticated selection algorithm for maximum uniqueness
        recommendations = []
        used_indices = set()
        
        # Create unique seed for this video
        video_seed = hash(f"{request_id}_{video_url}") % 10000
        
        for i in range(3):
            # Use multiple factors to ensure uniqueness
            selection_factor = (combined_hash * (i + 1) + video_seed + len(video_url) * i) % len(music_database)
            
            # Ensure no duplicates
            while selection_factor in used_indices:
                selection_factor = (selection_factor + 7) % len(music_database)
            used_indices.add(selection_factor)
            
            track = music_database[selection_factor]
            
            # Add slight variations to confidence scores
            base_confidence = 0.78 + (combined_hash % 20) / 100  # 0.78-0.97
            confidence_variation = (video_seed % 10) / 100  # 0.00-0.09
            final_confidence = min(0.99, base_confidence + confidence_variation)
            
            recommendations.append({
                "title": track["title"],
                "artist": track["artist"],
                "genre": track["genre"],
                "mood": track["mood"],
                "energy_level": track["energy"],
                "valence": track["valence"],
                "confidence_score": round(final_confidence, 3)
            })
        
        reasoning = (
            f"Based on the {mood.lower()} scene analysis featuring {visual_elements[0].lower()} "
            f"and {visual_elements[1].lower()} with {ambient_tags[0].lower()} audio elements, "
            f"these recommendations complement the unique characteristics of video {request_id[-6:]}."
        )
        
        return {
            "scene_description": scene_description,
            "scene_mood": mood,
            "visual_elements": visual_elements,
            "ambient_tags": ambient_tags,
            "extracted_frames": extracted_frames,
            "transcription": transcription,
            "recommendations": recommendations,
            "reasoning": reasoning,
            "processing_duration": 4.5 + (combined_hash % 20) / 10,  # 4.5-6.4 seconds
            "model_versions": {
                "video_analysis": f"simulation-v{1 + (combined_hash % 3)}.{combined_hash % 10}",
                "audio_analysis": f"content-aware-v{1 + (combined_hash % 2)}.{(combined_hash * 7) % 10}"
            }
        }

# Global instance
supabase_service = SupabaseService() 