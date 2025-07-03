import React from 'react';
import type { ProcessingRequest } from '../types';
import { ProcessingStatus } from '../types';

interface RequestHistoryProps {
  requests: ProcessingRequest[];
  onRequestSelect?: (request: ProcessingRequest) => void;
  className?: string;
}

export const RequestHistory: React.FC<RequestHistoryProps> = ({
  requests,
  onRequestSelect,
  className = ''
}) => {
  const getStatusIcon = (status: ProcessingStatus): string => {
    switch (status) {
      case ProcessingStatus.PENDING:
        return '⏳';
      case ProcessingStatus.PROCESSING:
        return '🔄';
      case ProcessingStatus.COMPLETED:
        return '✅';
      case ProcessingStatus.FAILED:
        return '❌';
      case ProcessingStatus.CANCELLED:
        return '🚫';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status: ProcessingStatus): string => {
    switch (status) {
      case ProcessingStatus.PENDING:
        return '#ffc107';
      case ProcessingStatus.PROCESSING:
        return '#007bff';
      case ProcessingStatus.COMPLETED:
        return '#28a745';
      case ProcessingStatus.FAILED:
        return '#dc3545';
      case ProcessingStatus.CANCELLED:
        return '#6c757d';
      default:
        return '#6c757d';
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDuration = (createdAt: string, completedAt?: string): string => {
    if (!completedAt) return 'In progress...';
    
    const start = new Date(createdAt);
    const end = new Date(completedAt);
    const durationMs = end.getTime() - start.getTime();
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
  };

  if (requests.length === 0) {
    return (
      <div className={`request-history empty ${className}`}>
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <h4>No processing requests yet</h4>
          <p>Upload a video to see your processing history here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`request-history ${className}`}>
      <div className="history-header">
        <h3>📊 Processing History</h3>
        <span className="request-count">
          {requests.length} request{requests.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="requests-list">
        {requests.map((request) => (
          <div 
            key={request.id}
            className={`request-item ${request.status}`}
            onClick={() => onRequestSelect?.(request)}
          >
            <div className="request-header">
              <div className="request-title">
                <span className="status-icon" style={{ color: getStatusColor(request.status) }}>
                  {getStatusIcon(request.status)}
                </span>
                <span className="filename">{request.video_filename}</span>
              </div>
              <div className="request-date">
                {formatDate(request.created_at)}
              </div>
            </div>

            <div className="request-meta">
              <div className="status-badge" style={{ backgroundColor: getStatusColor(request.status) }}>
                {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
              </div>
              
              {request.status === ProcessingStatus.COMPLETED && (
                <div className="duration">
                  ⚡ {formatDuration(request.created_at, request.completed_at)}
                </div>
              )}

              {request.result?.recommendations && (
                <div className="recommendations-count">
                  🎵 {request.result.recommendations.length} songs
                </div>
              )}
            </div>

            {request.description && (
              <div className="request-description">
                {request.description}
              </div>
            )}

            {request.error_message && (
              <div className="error-message">
                ❌ {request.error_message}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}; 