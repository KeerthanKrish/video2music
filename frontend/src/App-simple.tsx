import React from 'react';

function App() {
  return (
    <div style={{ padding: '2rem', textAlign: 'center', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#007bff' }}>🎵 video2music</h1>
      <p>React app is working!</p>
      <p>Current time: {new Date().toLocaleTimeString()}</p>
      <div style={{ marginTop: '2rem' }}>
        <h3>Environment Test:</h3>
        <p>Supabase URL: {import.meta.env.VITE_SUPABASE_URL || 'Not set'}</p>
        <p>API Base URL: {import.meta.env.VITE_API_BASE_URL || 'Not set'}</p>
      </div>
    </div>
  );
}

export default App; 