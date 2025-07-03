import { useState, useEffect, useRef } from 'react';
import type { User, Session } from '@supabase/supabase-js';
import { AuthError } from '@supabase/supabase-js';
import { supabase } from '../services/supabase';

export interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    session: null,
    loading: true,
    error: null,
  });

  const lastRefreshAttempt = useRef<number>(0);
  const refreshCooldown = 5000; // 5 seconds between refresh attempts

  useEffect(() => {
    let isMounted = true;

    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (!isMounted) return;
        
        if (error) {
          console.error('Auth session error:', error);
          setAuthState(prev => ({
            ...prev,
            loading: false,
            error: error.message,
          }));
        } else {
          // Check if session is expired
          if (session?.expires_at) {
            const isExpired = session.expires_at * 1000 < Date.now();
            
            if (isExpired) {
              setAuthState(prev => ({
                ...prev,
                user: null,
                session: null,
                loading: false,
                error: null,
              }));
              return;
            }
          }
          
          setAuthState(prev => ({
            ...prev,
            user: session?.user ?? null,
            session,
            loading: false,
            error: null,
          }));
        }
      } catch (error) {
        console.error('Auth session error:', error);
        if (isMounted) {
          setAuthState(prev => ({
            ...prev,
            loading: false,
            error: 'Failed to get session',
          }));
        }
      }
    };

    getInitialSession();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (!isMounted) return;
        
        // Handle specific events
        if (event === 'TOKEN_REFRESHED') {
          lastRefreshAttempt.current = Date.now();
        } else if (event === 'SIGNED_OUT') {
          lastRefreshAttempt.current = 0;
        }
        
        if (session) {
          // Check if session is expired and handle carefully
          if (session.expires_at) {
            const isExpired = session.expires_at * 1000 < Date.now();
            
            if (isExpired) {
              // Check if we can attempt a refresh (rate limiting)
              const timeSinceLastRefresh = Date.now() - lastRefreshAttempt.current;
              if (timeSinceLastRefresh > refreshCooldown) {
                lastRefreshAttempt.current = Date.now();
                
                try {
                  const { data, error } = await supabase.auth.refreshSession();
                  if (error) {
                    console.error('Session refresh failed:', error.message);
                    await supabase.auth.signOut();
                    return;
                  }
                  // The refresh will trigger another auth state change
                  return;
                } catch (refreshError) {
                  console.error('Session refresh error:', refreshError);
                  await supabase.auth.signOut();
                  return;
                }
              } else {
                await supabase.auth.signOut();
                return;
              }
            }
          }
        }
        
        setAuthState(prev => ({
          ...prev,
          user: session?.user ?? null,
          session,
          loading: false,
          error: null,
        }));
      }
    );

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const signIn = async (email: string, password: string): Promise<{ error?: AuthError }> => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Add timeout to prevent hanging
      const signInPromise = supabase.auth.signInWithPassword({
        email,
        password,
      });

      // Set a timeout for the sign-in attempt
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Sign in timeout')), 10000); // 10 second timeout
      });

      const { data, error } = await Promise.race([signInPromise, timeoutPromise]) as any;

      if (error) {
        console.error('Sign in error:', error);
        setAuthState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
        return { error };
      }

      // Set a fallback timeout to reset loading state if auth state change doesn't fire
      setTimeout(() => {
        setAuthState(prev => {
          if (prev.loading) {
            return {
              ...prev,
              loading: false,
              user: data.user,
              session: data.session,
              error: null
            };
          }
          return prev;
        });
      }, 3000); // 3 second fallback
      
      // State will be updated by the auth state change listener
      return { error: undefined };
    } catch (error: any) {
      console.error('Unexpected sign in error:', error);
      const errorMessage = error.message === 'Sign in timeout' 
        ? 'Sign in request timed out. Please check your connection and try again.'
        : 'An unexpected error occurred';
      
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return { error: new AuthError(errorMessage) };
    }
  };

  const signUp = async (
    email: string, 
    password: string, 
    options?: { full_name?: string }
  ): Promise<{ error?: AuthError }> => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: options?.full_name || '',
          },
        },
      });

      if (error) {
        console.error('Sign up error:', error);
        setAuthState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
        return { error };
      }
      
      // State will be updated by the auth state change listener
      return { error: undefined };
    } catch (error) {
      console.error('Unexpected sign up error:', error);
      const errorMessage = 'An unexpected error occurred';
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return { error: new AuthError(errorMessage) };
    }
  };

  const signOut = async (): Promise<{ error?: AuthError }> => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const { error } = await supabase.auth.signOut();

      if (error) {
        console.error('Sign out error:', error);
        setAuthState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
        return { error };
      }

      // State will be updated by the auth state change listener
      return { error: undefined };
    } catch (error) {
      console.error('Unexpected sign out error:', error);
      const errorMessage = 'An unexpected error occurred';
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      return { error: new AuthError(errorMessage) };
    }
  };

  const resetPassword = async (email: string): Promise<{ error?: AuthError }> => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email);
      if (error) {
        console.error('Password reset error:', error);
      }
      return { error: error || undefined };
    } catch (error) {
      console.error('Unexpected password reset error:', error);
      return { error: new AuthError('An unexpected error occurred') };
    }
  };

  return {
    ...authState,
    signIn,
    signUp,
    signOut,
    resetPassword,
    isAuthenticated: !!authState.user && !!authState.session,
  };
}; 