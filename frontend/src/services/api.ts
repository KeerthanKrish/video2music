import axios from 'axios';
import { supabase } from './supabase';
import type { ProcessingRequest } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with enhanced config for video processing
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for video processing
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  
  return config;
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      error.message = 'Request timed out. Please try again with a smaller file or check your connection.';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Enhanced video upload with music preferences and progress tracking
  async uploadVideo(
    file: File, 
    description?: string, 
    musicYearStart?: number, 
    musicYearEnd?: number,
    onProgress?: (progressEvent: { loaded: number; total: number }) => void
  ): Promise<ProcessingRequest> {
    const formData = new FormData();
    formData.append('video_file', file);
    
    if (description) {
      formData.append('description', description);
    }
    
    if (musicYearStart !== undefined) {
      formData.append('music_year_start', musicYearStart.toString());
    }
    
    if (musicYearEnd !== undefined) {
      formData.append('music_year_end', musicYearEnd.toString());
    }

    const response = await api.post('/requests/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 minutes timeout for uploads
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total
          });
        }
      },
    });

    return response.data;
  },

  // Get all user requests with enhanced polling
  async getUserRequests(): Promise<ProcessingRequest[]> {
    const response = await api.get('/requests/', {
      timeout: 60000, // 1 minute for listing requests
    });
    return response.data;
  },

  // Get specific request by ID with progress tracking
  async getRequest(requestId: string): Promise<ProcessingRequest> {
    const response = await api.get(`/requests/${requestId}`, {
      timeout: 60000, // 1 minute for individual request
    });
    return response.data;
  },

  // Delete/cancel a request
  async deleteRequest(requestId: string): Promise<void> {
    await api.delete(`/requests/${requestId}`, {
      timeout: 30000, // 30 seconds for deletion
    });
  },

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await api.get('/', {
      timeout: 10000, // 10 seconds for health check
    });
    return response.data;
  },

  // Get processing progress for real-time updates
  async getProcessingProgress(requestId: string): Promise<ProcessingRequest> {
    const response = await api.get(`/requests/${requestId}/progress`, {
      timeout: 10000, // 10 seconds for progress check
    });
    return response.data;
  },
};

export default apiService; 