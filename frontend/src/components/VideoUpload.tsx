import React, { useState, useCallback } from 'react';
import type { ProcessingRequest, UploadProgress } from '../types';
import { ProcessingStatus } from '../types';
import { apiService } from '../services/api';

interface VideoUploadProps {
  onUploadComplete?: (request: ProcessingRequest) => void;
  className?: string;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({ 
  onUploadComplete, 
  className = '' 
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [musicYearStart, setMusicYearStart] = useState(1980);
  const [musicYearEnd, setMusicYearEnd] = useState(new Date().getFullYear());
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  // Accepted video formats
  const acceptedFormats = ['.mp4', '.mov', '.avi', '.mkv', '.webm'];
  const maxFileSize = 100 * 1024 * 1024; // 100MB

  const validateFile = (file: File): string | null => {
    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFormats.includes(extension)) {
      return `Unsupported format. Please use: ${acceptedFormats.join(', ')}`;
    }

    // Check file size
    if (file.size > maxFileSize) {
      return `File too large. Maximum size is ${maxFileSize / 1024 / 1024}MB`;
    }

    return null;
  };

  const handleFileSelect = useCallback((selectedFile: File) => {
    const validation = validateFile(selectedFile);
    if (validation) {
      setError(validation);
      return;
    }

    setFile(selectedFile);
    setError(null);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setProgress({ loaded: 0, total: file.size, percentage: 0 });

    try {
      // Enhanced upload with year preferences
      const request = await apiService.uploadVideo(
        file, 
        description || undefined,
        musicYearStart,
        musicYearEnd,
        (progressEvent) => {
          if (progressEvent.total) {
            const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress({
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage
            });
          }
        }
      );
      
      setFile(null);
      setDescription('');
      setProgress(null);
      
      if (onUploadComplete) {
        onUploadComplete(request);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
      setProgress(null);
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleYearStartChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setMusicYearStart(value);
    if (value > musicYearEnd) {
      setMusicYearEnd(value);
    }
  };

  const handleYearEndChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setMusicYearEnd(value);
    if (value < musicYearStart) {
      setMusicYearStart(value);
    }
  };

  return (
    <div className={`video-upload ${className}`}>
      <div className="upload-section">
        <h3>🎬 Upload Video for Analysis</h3>
        <p>Upload a video to get AI-powered music recommendations based on its mood and content.</p>

        {/* File Drop Zone */}
        <div
          className={`drop-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('video-input')?.click()}
        >
          <input
            id="video-input"
            type="file"
            accept={acceptedFormats.join(',')}
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />

          {file ? (
            <div className="file-info">
              <div className="file-icon">🎬</div>
              <div className="file-details">
                <div className="file-name">{file.name}</div>
                <div className="file-size">{formatFileSize(file.size)}</div>
              </div>
              <button
                className="remove-file"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                  setError(null);
                }}
              >
                ❌
              </button>
            </div>
          ) : (
            <div className="drop-prompt">
              <div className="drop-icon">📁</div>
              <div className="drop-text">
                <strong>Click to select</strong> or drag and drop your video
              </div>
              <div className="drop-formats">
                Supported: {acceptedFormats.join(', ')}
              </div>
              <div className="drop-size">
                Maximum size: {maxFileSize / 1024 / 1024}MB
              </div>
            </div>
          )}
        </div>

        {/* Description Input */}
        <div className="form-group">
          <label htmlFor="description">
            Description & Music Preferences
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the video content and what style of music you're looking for (e.g., 'energetic dance video, looking for upbeat electronic music' or 'calm nature scenes, prefer acoustic/instrumental')"
            rows={3}
            disabled={uploading}
          />
          <small className="form-hint">
            💡 This description will help our AI find music that better matches your preferences and video content.
          </small>
        </div>

        {/* Music Year Range Slider */}
        <div className="form-group">
          <label>
            🎵 Music Era Preference: {musicYearStart} - {musicYearEnd}
          </label>
          <div className="year-range-container">
            <div className="year-slider-group">
              <label htmlFor="year-start">From:</label>
              <input
                id="year-start"
                type="range"
                min="1950"
                max={new Date().getFullYear()}
                step="1"
                value={musicYearStart}
                onChange={handleYearStartChange}
                disabled={uploading}
                className="year-slider"
              />
              <span className="year-display">{musicYearStart}</span>
            </div>
            <div className="year-slider-group">
              <label htmlFor="year-end">To:</label>
              <input
                id="year-end"
                type="range"
                min="1950"
                max={new Date().getFullYear()}
                step="1"
                value={musicYearEnd}
                onChange={handleYearEndChange}
                disabled={uploading}
                className="year-slider"
              />
              <span className="year-display">{musicYearEnd}</span>
            </div>
          </div>
          <small className="form-hint">
            🎼 Choose the era of music you prefer for recommendations (e.g., 1980s classics, 2010s hits, or mix of all eras)
          </small>
        </div>

        {/* Enhanced Upload Progress */}
        {progress && (
          <div className="upload-progress">
            <div className="progress-header">
              <span>📤 Uploading...</span>
              <span>{progress.percentage}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
            <div className="progress-text">
              {formatFileSize(progress.loaded)} / {formatFileSize(progress.total)}
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* Upload Button */}
        <button
          className="btn-primary upload-btn"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? '⏳ Processing...' : '🚀 Analyze Video'}
        </button>
      </div>
    </div>
  );
}; 