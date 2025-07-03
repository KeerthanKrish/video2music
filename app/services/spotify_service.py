"""Spotify API service for music recommendations."""

import base64
import logging
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class SpotifyService:
    """Service for Spotify Web API integration."""
    
    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.access_token: Optional[str] = None
        logger.info(f"Spotify service initialized with client_id: {self.client_id[:10] if self.client_id else 'None'}...")
        
    async def _get_access_token(self) -> str:
        """Get Spotify access token using client credentials flow."""
        if self.access_token:
            return self.access_token
            
        try:
            # Check if credentials are properly configured
            if not self.client_id or not self.client_secret or self.client_id == "your_spotify_client_id_here":
                logger.warning("Spotify credentials not properly configured")
                raise Exception("Spotify credentials not configured")
            
            # Encode client credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://accounts.spotify.com/api/token",
                    headers={
                        "Authorization": f"Basic {credentials_b64}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"grant_type": "client_credentials"}
                )
                
                logger.info(f"Spotify token response status: {response.status_code}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    logger.info("Successfully obtained Spotify access token")
                    return self.access_token
                else:
                    logger.error(f"Failed to get Spotify token: {response.status_code} - {response.text}")
                    raise Exception(f"Spotify auth failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Spotify authentication error: {e}")
            raise
    
    def _map_mood_to_spotify_params(self, scene_mood: str, energy_level: float = 0.5) -> Dict[str, Any]:
        """Map scene mood to Spotify audio features and search parameters."""
        mood_mappings = {
            "Joyful and Energetic": {
                "valence": 0.8,
                "energy": 0.9,
                "danceability": 0.8,
                "tempo": "120-140",
                "genres": ["pop", "dance", "funk", "upbeat"]
            },
            "Calm and Peaceful": {
                "valence": 0.6,
                "energy": 0.3,
                "danceability": 0.4,
                "tempo": "60-100",
                "genres": ["ambient", "chill", "acoustic", "folk"]
            },
            "Dramatic and Intense": {
                "valence": 0.4,
                "energy": 0.8,
                "danceability": 0.5,
                "tempo": "100-130",
                "genres": ["rock", "cinematic", "epic", "orchestral"]
            },
            "Romantic": {
                "valence": 0.7,
                "energy": 0.4,
                "danceability": 0.6,
                "tempo": "70-110",
                "genres": ["love songs", "ballad", "romantic", "r&b"]
            },
            "Mysterious": {
                "valence": 0.3,
                "energy": 0.6,
                "danceability": 0.4,
                "tempo": "80-120",
                "genres": ["dark", "electronic", "ambient", "experimental"]
            }
        }
        
        return mood_mappings.get(scene_mood, mood_mappings["Joyful and Energetic"])
    
    async def search_tracks_by_mood(
        self, 
        scene_mood: str, 
        visual_elements: List[str], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for tracks based on scene mood and visual elements."""
        try:
            token = await self._get_access_token()
            mood_params = self._map_mood_to_spotify_params(scene_mood)
            
            # Create search query based on mood and visual elements
            search_terms = []
            
            # Add mood-based terms (simpler approach)
            if scene_mood == "Joyful and Energetic":
                search_terms.extend(["happy", "upbeat", "energetic", "fun"])
            elif scene_mood == "Calm and Peaceful":
                search_terms.extend(["calm", "peaceful", "chill", "relaxing"])
            elif scene_mood == "Dramatic and Intense":
                search_terms.extend(["dramatic", "intense", "epic", "powerful"])
            elif scene_mood == "Romantic":
                search_terms.extend(["love", "romantic", "sweet", "tender"])
            else:
                search_terms.extend(["music", "popular", "trending"])
            
            # Add visual element context
            if "Dancing" in visual_elements:
                search_terms.append("dance")
            if "Nature" in visual_elements:
                search_terms.append("nature")
            if "Party" in visual_elements or "Celebration" in visual_elements:
                search_terms.append("party")
                
            # Create simple search query
            query = " ".join(search_terms[:3])  # Use top 3 terms
            logger.info(f"Spotify search query: '{query}'")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.spotify.com/v1/search",
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "q": query,
                        "type": "track",
                        "limit": limit,  # Just get what we need
                        "market": "US"
                    }
                )
                
                logger.info(f"Spotify API response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    tracks = data.get("tracks", {}).get("items", [])
                    logger.info(f"Found {len(tracks)} tracks from Spotify")
                    
                    if len(tracks) == 0:
                        logger.warning(f"No tracks found for query: '{query}'")
                        return []
                    
                    # Format tracks without audio features 
                    recommendations = []
                    for track in tracks[:limit]:
                        # Estimate mood based on track name and artist
                        estimated_mood = self._estimate_mood_from_track_info(track, scene_mood)
                        
                        formatted_track = {
                            "title": track["name"],
                            "artist": ", ".join([artist["name"] for artist in track["artists"]]),
                            "genre": "Various",  # Spotify doesn't provide genre in track data
                            "mood": estimated_mood,
                            "energy_level": self._estimate_energy_from_mood(scene_mood),
                            "valence": self._estimate_valence_from_mood(scene_mood),
                            "preview_url": track.get("preview_url"),
                            "spotify_id": track["id"],
                            "spotify_url": track["external_urls"]["spotify"],
                            "confidence_score": self._calculate_basic_confidence(track, scene_mood),
                            "audio_features": {
                                "danceability": self._estimate_danceability(scene_mood, visual_elements),
                                "tempo": self._estimate_tempo(scene_mood),
                                "popularity": track.get("popularity", 50)
                            }
                        }
                        
                        recommendations.append(formatted_track)
                    
                    return recommendations
                    
                else:
                    logger.error(f"Spotify search failed with status {response.status_code}: {response.text}")
                    
                return []
                
        except Exception as e:
            logger.error(f"Spotify search error: {e}")
            return []
    
    def _estimate_mood_from_track_info(self, track: Dict, scene_mood: str) -> str:
        """Estimate mood based on track name and context."""
        title = track["name"].lower()
        artist = track["artists"][0]["name"].lower()
        
        # Simple heuristics based on common words
        if any(word in title for word in ["happy", "joy", "fun", "party", "dance"]):
            return "Upbeat and Joyful"
        elif any(word in title for word in ["love", "heart", "romantic"]):
            return "Romantic"
        elif any(word in title for word in ["calm", "peace", "chill", "relax"]):
            return "Calm and Peaceful"
        elif any(word in title for word in ["intense", "power", "strong", "epic"]):
            return "Intense and Dramatic"
        else:
            return scene_mood  # Default to scene mood
    
    def _estimate_energy_from_mood(self, scene_mood: str) -> float:
        """Estimate energy level based on scene mood."""
        mood_energy = {
            "Joyful and Energetic": 0.8,
            "Calm and Peaceful": 0.3,
            "Dramatic and Intense": 0.8,
            "Romantic": 0.4,
            "Mysterious": 0.6
        }
        return mood_energy.get(scene_mood, 0.5)
    
    def _estimate_valence_from_mood(self, scene_mood: str) -> float:
        """Estimate valence (positivity) based on scene mood."""
        mood_valence = {
            "Joyful and Energetic": 0.9,
            "Calm and Peaceful": 0.6,
            "Dramatic and Intense": 0.4,
            "Romantic": 0.7,
            "Mysterious": 0.3
        }
        return mood_valence.get(scene_mood, 0.5)
    
    def _estimate_danceability(self, scene_mood: str, visual_elements: List[str]) -> float:
        """Estimate danceability based on mood and visual elements."""
        base_dance = {
            "Joyful and Energetic": 0.8,
            "Calm and Peaceful": 0.3,
            "Dramatic and Intense": 0.5,
            "Romantic": 0.6,
            "Mysterious": 0.4
        }.get(scene_mood, 0.5)
        
        # Boost if dancing is in visual elements
        if "Dancing" in visual_elements or "Party" in visual_elements:
            base_dance = min(base_dance + 0.2, 1.0)
            
        return base_dance
    
    def _estimate_tempo(self, scene_mood: str) -> float:
        """Estimate tempo based on scene mood."""
        mood_tempo = {
            "Joyful and Energetic": 130,
            "Calm and Peaceful": 80,
            "Dramatic and Intense": 120,
            "Romantic": 90,
            "Mysterious": 100
        }
        return mood_tempo.get(scene_mood, 100)
    
    def _calculate_basic_confidence(self, track: Dict, scene_mood: str) -> float:
        """Calculate basic confidence score based on popularity and relevance."""
        popularity = track.get("popularity", 50) / 100  # Normalize to 0-1
        
        # Simple relevance check based on track title
        title = track["name"].lower()
        relevance = 0.5  # Base relevance
        
        if scene_mood == "Joyful and Energetic":
            if any(word in title for word in ["happy", "joy", "fun", "party", "dance", "upbeat"]):
                relevance += 0.3
        elif scene_mood == "Calm and Peaceful":
            if any(word in title for word in ["calm", "peace", "chill", "relax", "quiet"]):
                relevance += 0.3
        
        # Combine popularity and relevance 
        return min((popularity * 0.4 + relevance * 0.6), 1.0)
    
    async def get_recommendations_by_scene(
        self, 
        scene_description: str, 
        scene_mood: str, 
        visual_elements: List[str],
        ambient_tags: List[str]
    ) -> List[Dict[str, Any]]:
        """Get music recommendations based on complete scene analysis."""
        try:
            # Use Spotify search for now (recommendations endpoint requires seed tracks)
            recommendations = await self.search_tracks_by_mood(
                scene_mood, visual_elements, limit=3
            )
            
            if not recommendations and scene_mood != "Joyful and Energetic":
                # Fallback to a more general mood if no results
                recommendations = await self.search_tracks_by_mood(
                    "Joyful and Energetic", visual_elements, limit=3
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting scene recommendations: {e}")
            return []


# Global instance
spotify_service = SpotifyService() 