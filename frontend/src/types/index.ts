export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
  updated_at: string;
}

export enum ProcessingStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export interface MusicRecommendation {
  title: string;
  artist: string;
  genre: string;
  mood: string;
  energy_level: number;
  valence: number;
  preview_url?: string;
  spotify_id?: string;
  confidence_score: number;
}

export interface ProcessingProgress {
  stage: string;
  progress: number;
  message: string;
  timestamp: number;
}

export interface ProcessingResult {
  extracted_frames: string[];
  scene_description?: string;
  scene_mood?: string;
  visual_elements: string[];
  transcription?: string;
  ambient_tags: string[];
  audio_features: Record<string, any>;
  recommendations: MusicRecommendation[];
  reasoning?: string;
  processing_duration?: number;
  model_versions: Record<string, string>;
  progress_updates?: ProcessingProgress[];
}

export interface ProcessingRequest {
  id: string;
  user_id: string;
  video_filename: string;
  video_url?: string;
  status: ProcessingStatus;
  description?: string;
  music_year_start?: number;
  music_year_end?: number;
  result?: ProcessingResult;
  error_message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface ProcessingRequestCreate {
  video_filename: string;
  video_content_type: string;
  description?: string;
  music_year_start?: number;
  music_year_end?: number;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
} 