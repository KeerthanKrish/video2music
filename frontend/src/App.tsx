import React, { useState, useEffect } from 'react';
import { VideoUpload } from './components/VideoUpload';
import { RequestHistory } from './components/RequestHistory';
import { ResultDisplay } from './components/ResultDisplay';
import { SignInForm } from './components/Auth/SignInForm';
import { SignUpForm } from './components/Auth/SignUpForm';
import { useAuth } from './hooks/useAuth';
import { apiService } from './services/api';
import type { ProcessingRequest } from './types';
import { ProcessingStatus } from './types';
import './App.css';

type AuthMode = 'signin' | 'signup';

function App() {
  const { user, loading: authLoading } = useAuth();
  const [authMode, setAuthMode] = useState<AuthMode>('signin');
  const [requests, setRequests] = useState<ProcessingRequest[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<ProcessingRequest | null>(null);
  const [loading, setLoading] = useState(false);

  const isAuthenticated = !!user;

  // Load user requests on auth
  useEffect(() => {
    if (isAuthenticated) {
      loadRequests();
    }
  }, [isAuthenticated]);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const userRequests = await apiService.getUserRequests();
      setRequests(userRequests);
    } catch (error) {
      console.error('Failed to load requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = async (request: ProcessingRequest) => {
    setRequests(prev => [request, ...prev]);
    
    // Enhanced polling for status updates with progress tracking
    const pollStatus = async () => {
      try {
        const updatedRequest = await apiService.getRequest(request.id);
        setRequests(prev => prev.map(req => 
          req.id === request.id ? updatedRequest : req
        ));
        
        // Update selected request if it's the one being viewed
        if (selectedRequest?.id === request.id) {
          setSelectedRequest(updatedRequest);
        }
        
        // Continue polling if still processing with exponential backoff
        if (updatedRequest.status === ProcessingStatus.PROCESSING || 
            updatedRequest.status === ProcessingStatus.PENDING) {
          
          // Check for progress updates to determine poll frequency
          const hasProgress = updatedRequest.result?.progress_updates?.length && updatedRequest.result.progress_updates.length > 0;
          const latestProgress = hasProgress ? 
            updatedRequest.result?.progress_updates?.[updatedRequest.result.progress_updates.length - 1] : null;
          
          // More frequent polling during active processing
          const pollInterval = hasProgress && latestProgress && latestProgress.progress > 0 ? 
            1500 : // 1.5 seconds if actively processing
            3000;  // 3 seconds if pending/waiting
          
          setTimeout(pollStatus, pollInterval);
        }
      } catch (error) {
        console.error('Failed to poll request status:', error);
        // Retry polling after error with longer delay
        setTimeout(pollStatus, 5000);
      }
    };
    
    // Start polling after a short delay
    setTimeout(pollStatus, 1000);
  };

  const handleRequestSelect = (request: ProcessingRequest) => {
    setSelectedRequest(request);
    
    // If the selected request is still processing, start polling for updates
    if (request.status === ProcessingStatus.PROCESSING || 
        request.status === ProcessingStatus.PENDING) {
      
      const pollSelectedRequest = async () => {
        try {
          const updatedRequest = await apiService.getRequest(request.id);
          setSelectedRequest(updatedRequest);
          setRequests(prev => prev.map(req => 
            req.id === request.id ? updatedRequest : req
          ));
          
          // Continue polling if still processing
          if (updatedRequest.status === ProcessingStatus.PROCESSING || 
              updatedRequest.status === ProcessingStatus.PENDING) {
            setTimeout(pollSelectedRequest, 2000);
          }
        } catch (error) {
          console.error('Failed to poll selected request:', error);
        }
      };
      
      // Start polling for the selected request
      setTimeout(pollSelectedRequest, 1000);
    }
  };

  const handleRequestDelete = async (requestId: string) => {
    try {
      await apiService.deleteRequest(requestId);
      setRequests(prev => prev.filter(req => req.id !== requestId));
      
      // Clear selection if deleted request was selected
      if (selectedRequest?.id === requestId) {
        setSelectedRequest(null);
      }
    } catch (error) {
      console.error('Failed to delete request:', error);
    }
  };

  if (authLoading) {
    return (
      <div className="app loading">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="app">
        <div className="auth-container">
          <div className="app-header">
            <h1>🎵 video2music</h1>
            <p>AI-powered video analysis for mood-based music recommendations with customizable year preferences</p>
          </div>
          
          {authMode === 'signin' ? (
            <SignInForm onSwitchToSignUp={() => setAuthMode('signup')} />
          ) : (
            <SignUpForm onSwitchToSignIn={() => setAuthMode('signin')} />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎵 video2music</h1>
          <p>AI-powered video analysis for personalized music recommendations</p>
        </div>
        <div className="header-actions">
          <span className="user-info">Welcome, {user?.email}</span>
          <button 
            className="btn-secondary"
            onClick={() => window.location.reload()}
          >
            🔄 Refresh
          </button>
        </div>
      </header>

      <main className="app-main">
        <div className="upload-section">
          <VideoUpload onUploadComplete={handleUploadComplete} />
        </div>

        <div className="content-grid">
          <div className="history-panel">
            <RequestHistory 
              requests={requests}
              onRequestSelect={handleRequestSelect}
            />
          </div>

          <div className="results-panel">
            <ResultDisplay 
              request={selectedRequest}
              onClose={() => setSelectedRequest(null)}
            />
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>🎼 Powered by AI • 🎯 Enhanced with Spotify API • 📅 Customizable Music Eras</p>
      </footer>
    </div>
  );
}

export default App
