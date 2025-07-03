// Debug script to test Supabase authentication flow
import { createClient } from '@supabase/supabase-js';

// Replace with your actual values from environment
const supabaseUrl = process.env.VITE_SUPABASE_URL || 'your-supabase-url';
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function debugAuth() {
  console.log('🔍 Starting authentication debug...');
  
  // Check if environment variables are properly set
  console.log('Environment variables:');
  console.log('- SUPABASE_URL:', !!supabaseUrl);
  console.log('- SUPABASE_ANON_KEY:', !!supabaseAnonKey);
  
  // Check initial session
  console.log('\n📋 Checking initial session...');
  const { data: { session }, error: sessionError } = await supabase.auth.getSession();
  
  if (sessionError) {
    console.error('❌ Session error:', sessionError);
  } else {
    console.log('✅ Session:', session ? 'Found' : 'None');
    if (session) {
      console.log('- User ID:', session.user.id);
      console.log('- Email:', session.user.email);
      console.log('- Expires at:', new Date(session.expires_at * 1000));
      console.log('- Access token (first 20 chars):', session.access_token.substring(0, 20) + '...');
    }
  }
  
  // Set up auth state listener
  console.log('\n👂 Setting up auth state listener...');
  const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
    console.log(`🔄 Auth state changed: ${event}`);
    if (session) {
      console.log('- User:', session.user.email);
      console.log('- Session expires:', new Date(session.expires_at * 1000));
    } else {
      console.log('- No session');
    }
  });
  
  return subscription;
}

export { debugAuth }; 