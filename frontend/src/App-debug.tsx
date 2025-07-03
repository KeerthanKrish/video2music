import React, { useState } from 'react';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Sign in attempt:', { email, password });
    setIsLoggedIn(true);
  };

  const handleSignOut = () => {
    setIsLoggedIn(false);
    setEmail('');
    setPassword('');
  };

  if (isLoggedIn) {
    return (
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <div className="logo-section">
              <h1>🎵 video2music</h1>
              <p>Welcome, {email}</p>
            </div>
            
            <div className="header-actions">
              <button 
                className="btn-secondary"
                onClick={handleSignOut}
              >
                Sign Out
              </button>
            </div>
          </div>
        </header>

        <main className="app-main">
          <div className="dashboard">
            <div className="dashboard-section">
              <h3>Upload Video for Analysis</h3>
              <p>Upload functionality will be implemented here</p>
            </div>
            
            <div className="dashboard-section">
              <h3>Processing History</h3>
              <p>Request history will be shown here</p>
            </div>
          </div>
        </main>

        <footer className="app-footer">
          <p>&copy; 2024 video2music. AI-powered video analysis for music discovery.</p>
        </footer>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="auth-container">
        <div className="app-header">
          <h1>🎵 video2music</h1>
          <p>AI-powered video analysis for mood-based music recommendations</p>
        </div>
        
        <div className="auth-form">
          <h2>Sign In to video2music</h2>
          
          <form onSubmit={handleSignIn}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
              />
            </div>

            <button 
              type="submit" 
              className="btn-primary"
            >
              Sign In
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App; 