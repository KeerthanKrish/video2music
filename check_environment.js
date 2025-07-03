// Environment Check Script
// Run this in your browser console to check environment configuration

console.log('🔍 Checking environment configuration...');

// Check if environment variables exist
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

console.log('\n📋 Environment Variables:');
console.log('- VITE_SUPABASE_URL:', !!supabaseUrl ? '✅ Set' : '❌ Missing');
console.log('- VITE_SUPABASE_ANON_KEY:', !!supabaseAnonKey ? '✅ Set' : '❌ Missing');

if (supabaseUrl) {
  console.log('- URL format valid:', supabaseUrl.includes('supabase.co') ? '✅ Yes' : '❌ No');
  console.log('- URL preview:', supabaseUrl.substring(0, 30) + '...');
}

if (supabaseAnonKey) {
  console.log('- Key length:', supabaseAnonKey.length > 50 ? '✅ Valid length' : '❌ Too short');
  console.log('- Key preview:', supabaseAnonKey.substring(0, 20) + '...');
}

// Test basic Supabase connection
console.log('\n🔌 Testing Supabase connection...');
try {
  // This should be available if Supabase is imported correctly
  if (typeof supabase !== 'undefined') {
    console.log('✅ Supabase client available');
    
    supabase.auth.getSession().then(({data, error}) => {
      if (error) {
        console.log('❌ Connection test failed:', error.message);
      } else {
        console.log('✅ Connection test successful');
      }
    }).catch(err => {
      console.log('❌ Connection test error:', err.message);
    });
  } else {
    console.log('❌ Supabase client not available in global scope');
  }
} catch (error) {
  console.log('❌ Error testing connection:', error.message);
}

// Show common issues and solutions
console.log('\n🛠️ Common Issues & Solutions:');
console.log('1. Missing .env file → Create frontend/.env with your Supabase credentials');
console.log('2. Wrong variable names → Use VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY');
console.log('3. Dev server not restarted → Restart npm run dev after adding .env');
console.log('4. Wrong URL format → Should be https://your-project.supabase.co');
console.log('5. Wrong key → Use anon/public key, not service role key for frontend');

if (!supabaseUrl || !supabaseAnonKey) {
  console.log('\n❌ ENVIRONMENT VARIABLES ARE MISSING!');
  console.log('Create a .env file in your frontend directory with:');
  console.log('VITE_SUPABASE_URL=https://your-project.supabase.co');
  console.log('VITE_SUPABASE_ANON_KEY=your-anon-key-here');
  console.log('Then restart your dev server!');
} 