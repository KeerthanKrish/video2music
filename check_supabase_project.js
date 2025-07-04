// Comprehensive Supabase Project Health Check
// Run this in browser console to check project status

const { createClient } = require('@supabase/supabase-js');

// Load from environment variables
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://your-project.supabase.co';
const ANON_KEY = process.env.SUPABASE_ANON_KEY || '';

if (!ANON_KEY) {
  console.error('❌ SUPABASE_ANON_KEY environment variable is not set');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, ANON_KEY);

console.log('🏥 Starting Supabase Project Health Check...');

async function checkProjectHealth() {
  const results = {};
  
  // Test 1: Basic connectivity
  console.log('\n🔌 Testing basic connectivity...');
  try {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/`, {
      headers: { 'apikey': ANON_KEY }
    });
    results.connectivity = { status: response.status, ok: response.ok };
    console.log(response.ok ? '✅ Basic connectivity: OK' : '❌ Basic connectivity: Failed');
  } catch (error) {
    results.connectivity = { error: error.message };
    console.log('❌ Basic connectivity: Failed -', error.message);
  }

  // Test 2: Auth service
  console.log('\n🔑 Testing auth service...');
  try {
    const response = await fetch(`${SUPABASE_URL}/auth/v1/settings`, {
      headers: { 'apikey': ANON_KEY }
    });
    const data = await response.json();
    results.auth = { status: response.status, settings: data };
    console.log(response.ok ? '✅ Auth service: OK' : '❌ Auth service: Failed');
    console.log('- Signup enabled:', data.disable_signup === false);
    console.log('- Email confirmation:', data.mailer_autoconfirm === false ? 'Required' : 'Auto');
  } catch (error) {
    results.auth = { error: error.message };
    console.log('❌ Auth service: Failed -', error.message);
  }

  // Test 3: Edge Functions
  console.log('\n⚡ Testing Edge Functions...');
  try {
    const response = await fetch(`${SUPABASE_URL}/functions/v1/`, {
      headers: { 'apikey': ANON_KEY }
    });
    results.functions = { status: response.status, ok: response.ok };
    console.log(response.ok ? '✅ Edge Functions: OK' : '❌ Edge Functions: Failed');
  } catch (error) {
    results.functions = { error: error.message };
    console.log('❌ Edge Functions: Failed -', error.message);
  }

  // Test 4: Database (PostgREST)
  console.log('\n🗄️ Testing database access...');
  try {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/`, {
      headers: { 
        'apikey': ANON_KEY,
        'Accept': 'application/json'
      }
    });
    results.database = { status: response.status, ok: response.ok };
    console.log(response.ok ? '✅ Database access: OK' : '❌ Database access: Failed');
  } catch (error) {
    results.database = { error: error.message };
    console.log('❌ Database access: Failed -', error.message);
  }

  // Test 5: Test sign-in with wrong credentials (should fail gracefully)
  console.log('\n🧪 Testing auth endpoint with wrong credentials...');
  try {
    const response = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
      method: 'POST',
      headers: {
        'apikey': ANON_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: 'test@wrong.com',
        password: 'wrongpassword'
      })
    });
    const data = await response.json();
    results.authTest = { status: response.status, response: data };
    
    if (response.status === 400 && data.error_description?.includes('Invalid')) {
      console.log('✅ Auth endpoint: Working (correctly rejected wrong credentials)');
    } else {
      console.log('❌ Auth endpoint: Unexpected response');
      console.log('- Status:', response.status);
      console.log('- Response:', data);
    }
  } catch (error) {
    results.authTest = { error: error.message };
    console.log('❌ Auth endpoint test: Failed -', error.message);
  }

  console.log('\n📋 Health Check Summary:');
  console.table(results);
  
  return results;
}

// Run the health check
checkProjectHealth(); 