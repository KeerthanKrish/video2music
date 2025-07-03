import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface SignInFormProps {
  onSwitchToSignUp: () => void;
}

export const SignInForm: React.FC<SignInFormProps> = ({ onSwitchToSignUp }) => {
  const { signIn, loading, signUp } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [loadingTimeout, setLoadingTimeout] = useState<NodeJS.Timeout | null>(null);

  // Clear timeout when component unmounts or loading changes
  useEffect(() => {
    if (!loading && loadingTimeout) {
      clearTimeout(loadingTimeout);
      setLoadingTimeout(null);
    }
    
    return () => {
      if (loadingTimeout) {
        clearTimeout(loadingTimeout);
      }
    };
  }, [loading, loadingTimeout]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear errors when user starts typing
    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.email || !formData.password) {
      setError('Please enter both email and password');
      return;
    }

    console.log('📝 SignInForm: Starting sign in process...');

    // Set a timeout to catch stuck loading states
    const timeout = setTimeout(() => {
      console.warn('⚠️ SignInForm: Sign in taking too long, showing error');
      setError('Sign in is taking longer than expected. Please check your connection and try again.');
    }, 15000); // 15 second timeout

    setLoadingTimeout(timeout);

    try {
      const { error } = await signIn(formData.email, formData.password);
      
      // Clear the timeout since we got a response
      clearTimeout(timeout);
      setLoadingTimeout(null);
      
      if (error) {
        console.error('❌ SignInForm: Sign in failed:', error.message);
        setError(error.message);
      } else {
        console.log('✅ SignInForm: Sign in completed successfully');
      }
    } catch (error: any) {
      console.error('❌ SignInForm: Unexpected error:', error);
      clearTimeout(timeout);
      setLoadingTimeout(null);
      setError(error.message || 'Failed to sign in');
    }
  };

  return (
    <div className="auth-form">
      <h2>Sign In to video2music</h2>
      <p className="auth-subtitle">Welcome back! Please sign in to your account</p>
      
      {error && (
        <div className="error-message">
          {error}
          {error.includes('taking longer') && (
            <div style={{ marginTop: '10px', fontSize: '14px' }}>
              <strong>Troubleshooting tips:</strong>
              <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                <li>Check your internet connection</li>
                <li>Verify your email and password are correct</li>
                <li>Try refreshing the page</li>
                <li>Check the debug panel for more details</li>
              </ul>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            disabled={loading}
            placeholder="Enter your email"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            required
            disabled={loading}
            placeholder="Enter your password"
          />
        </div>

        <button 
          type="submit" 
          className="btn-primary"
          disabled={loading}
        >
          {loading ? 'Signing In...' : 'Sign In'}
        </button>

        {/* Debug: Quick test user button */}
        <button
          type="button"
          onClick={async () => {
            console.log('🧪 Creating test user...');
            const timestamp = Date.now();
            const testEmail = `test${timestamp}@gmail.com`; // Use gmail.com instead of example.com
            const testPassword = 'TestPassword123!';
            
            console.log('📧 Test email:', testEmail);
            console.log('🔑 Test password:', testPassword);
            
            try {
              // First create the user
              console.log('📝 Attempting signup...');
              const { error: signUpError } = await signUp(testEmail, testPassword);
              if (signUpError) {
                console.error('❌ Test signup failed:', signUpError);
                alert(`Test signup failed: ${signUpError.message}`);
                return;
              }
              
              console.log('✅ Test user created successfully:', testEmail);
              
              // Wait a moment for user creation to complete
              await new Promise(resolve => setTimeout(resolve, 1000));
              
              // Then try to sign in with the new user
              console.log('🔑 Attempting signin...');
              const { error: signInError } = await signIn(testEmail, testPassword);
              if (signInError) {
                console.error('❌ Test signin failed:', signInError);
                alert(`Test signin failed: ${signInError.message}\n\nBut signup worked! This means the auth service is functional.`);
              } else {
                console.log('✅ Test signin successful!');
                alert(`🎉 Test completely successful!\n\nEmail: ${testEmail}\nPassword: ${testPassword}\n\nYour Supabase auth is working perfectly!`);
              }
            } catch (error: any) {
              console.error('❌ Test error:', error);
              alert(`Test error: ${error.message}`);
            }
          }}
          disabled={loading}
          style={{ 
            marginTop: '10px', 
            backgroundColor: '#f39c12', 
            border: 'none', 
            padding: '8px 12px', 
            borderRadius: '4px',
            color: 'white',
            fontSize: '12px'
          }}
        >
          🧪 Create & Test New User
        </button>
      </form>

      <div className="auth-switch">
        <p>
          Don't have an account?{' '}
          <button 
            type="button" 
            className="auth-link"
            onClick={onSwitchToSignUp}
            disabled={loading}
          >
            Create Account
          </button>
        </p>
      </div>
    </div>
  );
}; 