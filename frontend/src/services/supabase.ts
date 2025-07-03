import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Please check your .env file.');
}

console.log('🔧 Supabase: Initializing client...');
console.log('- URL configured:', !!supabaseUrl);
console.log('- Anon key configured:', !!supabaseAnonKey);

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    flowType: 'pkce'
  },
  global: {
    headers: {
      'X-Client-Info': 'video2music-frontend'
    }
  }
});

supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    console.log('✅ Supabase: Token refreshed at', new Date().toISOString());
  } else if (event === 'SIGNED_OUT') {
    console.log('🚪 Supabase: User signed out at', new Date().toISOString());
  }
});

export default supabase; 