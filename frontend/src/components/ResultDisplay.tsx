import React, { useState } from 'react';
import type { ProcessingRequest, MusicRecommendation } from '../types';
import { ProcessingStatus } from '../types';

interface ResultDisplayProps {
  request: ProcessingRequest | null;
  onClose?: () => void;
  className?: string;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({
  request,
  onClose,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'recommendations' | 'details'>('overview');

  if (!request) {
    return (
      <div className={`result-display empty ${className}`}>
        <div className="empty-state">
          <div className="empty-icon">🎵</div>
          <h4>No results to display</h4>
          <p>Select a completed processing request to view results.</p>
        </div>
      </div>
    );
  }

  const isCompleted = request.status === ProcessingStatus.COMPLETED;
  const isProcessing = request.status === ProcessingStatus.PROCESSING;
  const result = request.result;

  const getMoodEmoji = (mood?: string): string => {
    if (!mood) return '🎵';
    const moodLower = mood.toLowerCase();
    if (moodLower.includes('happy') || moodLower.includes('joy')) return '😊';
    if (moodLower.includes('sad') || moodLower.includes('melancholy')) return '😢';
    if (moodLower.includes('energetic') || moodLower.includes('upbeat')) return '⚡';
    if (moodLower.includes('calm') || moodLower.includes('peaceful')) return '😌';
    if (moodLower.includes('dramatic') || moodLower.includes('intense')) return '🎭';
    if (moodLower.includes('romantic') || moodLower.includes('love')) return '💝';
    return '🎵';
  };

  const formatConfidence = (score: number): string => {
    return `${Math.round(score * 100)}%`;
  };

  const getEnergyBar = (level: number) => {
    const percentage = Math.round(level * 100);
    return (
      <div className="energy-bar">
        <div className="energy-fill" style={{ width: `${percentage}%` }}></div>
        <span className="energy-text">{percentage}%</span>
      </div>
    );
  };

  const playPreview = (previewUrl: string) => {
    // For demo, we'll just show an alert
    // In real implementation, this would play the audio preview
    alert(`🎵 Playing preview: ${previewUrl}`);
  };

  // Get processing progress information
  const getProcessingProgress = () => {
    if (!result?.progress_updates) return null;
    
    const latestUpdate = result.progress_updates[result.progress_updates.length - 1];
    if (!latestUpdate) return null;
    
    return {
      stage: latestUpdate.stage,
      progress: latestUpdate.progress,
      message: latestUpdate.message
    };
  };

  const progress = getProcessingProgress();

  const renderProcessingProgress = () => {
    if (!isProcessing && request.status !== ProcessingStatus.PENDING) return null;

    const stages = [
      { id: 'initialization', name: 'Initializing', icon: '🔄' },
      { id: 'frame_extraction', name: 'Extracting Frames', icon: '🎬' },
      { id: 'audio_transcription', name: 'Transcribing Audio', icon: '🎤' },
      { id: 'ambient_analysis', name: 'Analyzing Audio', icon: '🔊' },
      { id: 'scene_analysis', name: 'Understanding Scene', icon: '🎭' },
      { id: 'music_matching', name: 'Finding Music', icon: '🎵' }
    ];

    const currentProgress = progress?.progress || 0;
    const currentStage = progress?.stage || 'initialization';
    const currentMessage = progress?.message || 'Starting processing...';

    return (
      <div className="processing-progress">
        <div className="progress-header">
          <h4>🔄 Processing Video</h4>
          <span className="progress-percentage">{Math.round(currentProgress)}%</span>
        </div>
        
        <div className="progress-message">
          {currentMessage}
        </div>
        
        <div className="stage-progress-bar">
          <div 
            className="stage-progress-fill" 
            style={{ width: `${currentProgress}%` }}
          />
        </div>
        
        <div className="stage-indicators">
          {stages.map((stage, index) => {
            const isActive = stage.id === currentStage;
            const isCompleted = index < stages.findIndex(s => s.id === currentStage);
            
            return (
              <div 
                key={stage.id}
                className={`stage-indicator ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
              >
                <div className="stage-icon">{stage.icon}</div>
                <div className="stage-name">{stage.name}</div>
              </div>
            );
          })}
        </div>
        
        <div className="processing-time">
          Started: {new Date(request.created_at).toLocaleTimeString()}
        </div>
      </div>
    );
  };

  return (
    <div className={`result-display ${className}`}>
      <div className="result-header">
        <div className="result-title">
          <h3>📊 Analysis Results</h3>
          <span className="video-name">{request.video_filename}</span>
          {request.description && (
            <div className="user-description">
              💭 "{request.description}"
            </div>
          )}
          {(request.music_year_start || request.music_year_end) && (
            <div className="music-preferences">
              🎼 Music Era: {request.music_year_start || 1980} - {request.music_year_end || 2024}
            </div>
          )}
        </div>
        {onClose && (
          <button className="close-btn" onClick={onClose}>
            ❌
          </button>
        )}
      </div>

      {!isCompleted ? (
        <div className="processing-state">
          {isProcessing ? (
            renderProcessingProgress()
          ) : (
            <div className="processing-icon">
              {request.status === ProcessingStatus.PENDING && '⏳'}
              {request.status === ProcessingStatus.FAILED && '❌'}
            </div>
          )}
          
          {!isProcessing && (
            <>
              <h4>
                {request.status === ProcessingStatus.PENDING && 'Analysis Pending'}
                {request.status === ProcessingStatus.FAILED && 'Analysis Failed'}
              </h4>
              <p>
                {request.status === ProcessingStatus.PENDING && 'Your video is queued for processing...'}
                {request.status === ProcessingStatus.FAILED && request.error_message}
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="result-content">
          <div className="result-tabs">
            <button 
              className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📋 Overview
            </button>
            <button 
              className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommendations')}
            >
              🎵 Music ({result?.recommendations?.length || 0})
            </button>
            <button 
              className={`tab ${activeTab === 'details' ? 'active' : ''}`}
              onClick={() => setActiveTab('details')}
            >
              🔍 Details
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                {result?.scene_mood && (
                  <div className="mood-section">
                    <h4>
                      {getMoodEmoji(result.scene_mood)} Scene Mood
                    </h4>
                    <div className="mood-value">{result.scene_mood}</div>
                  </div>
                )}

                {result?.scene_description && (
                  <div className="description-section">
                    <h4>📝 Scene Description</h4>
                    <p>{result.scene_description}</p>
                  </div>
                )}

                {result?.transcription && (
                  <div className="transcription-section">
                    <h4>🎤 Transcription</h4>
                    <p className="transcription-text">{result.transcription}</p>
                  </div>
                )}

                {result?.visual_elements && result.visual_elements.length > 0 && (
                  <div className="visual-elements">
                    <h4>👁️ Visual Elements</h4>
                    <div className="element-tags">
                      {result.visual_elements.map((element, index) => (
                        <span key={index} className="element-tag">
                          {element}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result?.processing_duration && (
                  <div className="processing-info">
                    <h4>⏱️ Processing Time</h4>
                    <p>{result.processing_duration.toFixed(1)}s</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="recommendations-tab">
                {result?.reasoning && (
                  <div className="reasoning-section">
                    <h4>🧠 Why These Songs?</h4>
                    <p>{result.reasoning}</p>
                  </div>
                )}

                {result?.recommendations && result.recommendations.length > 0 ? (
                  <div className="recommendations-list">
                    {result.recommendations.map((rec, index) => (
                      <div key={index} className="recommendation-item">
                        <div className="rec-header">
                          <div className="rec-title">
                            <h5>{rec.title}</h5>
                            <div className="rec-artist">{rec.artist}</div>
                          </div>
                          <div className="rec-confidence">
                            {formatConfidence(rec.confidence_score)}
                          </div>
                        </div>

                        <div className="rec-details">
                          <div className="rec-meta">
                            <span className="genre-tag">{rec.genre}</span>
                            <span className="mood-tag">{rec.mood}</span>
                          </div>

                          <div className="rec-metrics">
                            <div className="metric">
                              <label>Energy Level</label>
                              {getEnergyBar(rec.energy_level)}
                            </div>
                            <div className="metric">
                              <label>Positivity</label>
                              {getEnergyBar(rec.valence)}
                            </div>
                          </div>

                          <div className="rec-actions">
                            {rec.preview_url && (
                              <button 
                                className="btn-secondary preview-btn"
                                onClick={() => playPreview(rec.preview_url!)}
                              >
                                🎵 Preview
                              </button>
                            )}
                            {rec.spotify_id && (
                              <a 
                                href={`https://open.spotify.com/track/${rec.spotify_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-primary spotify-btn"
                              >
                                🎧 Open in Spotify
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-recommendations">
                    <p>No music recommendations available.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'details' && (
              <div className="details-tab">
                {result?.ambient_tags && result.ambient_tags.length > 0 && (
                  <div className="ambient-section">
                    <h4>🔊 Ambient Audio Tags</h4>
                    <div className="element-tags">
                      {result.ambient_tags.map((tag, index) => (
                        <span key={index} className="element-tag">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="metadata-section">
                  <h4>🤖 Processing Metadata</h4>
                  <div className="metadata-grid">
                    <div className="metadata-item">
                      <label>Request ID</label>
                      <span>{request.id}</span>
                    </div>
                    <div className="metadata-item">
                      <label>Status</label>
                      <span>{request.status}</span>
                    </div>
                    <div className="metadata-item">
                      <label>Created</label>
                      <span>{new Date(request.created_at).toLocaleString()}</span>
                    </div>
                    {request.completed_at && (
                      <div className="metadata-item">
                        <label>Completed</label>
                        <span>{new Date(request.completed_at).toLocaleString()}</span>
                      </div>
                    )}
                    {result?.model_versions && Object.keys(result.model_versions).length > 0 && (
                      <div className="metadata-item">
                        <label>AI Models</label>
                        <div className="model-versions">
                          {Object.entries(result.model_versions).map(([key, value]) => (
                            <div key={key} className="model-version">
                              <strong>{key}:</strong> {value}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}; 