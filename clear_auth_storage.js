// Clear Authentication Storage Script
// Run this in your browser console to clear all authentication data

console.log('🧹 Clearing authentication storage...');

// Clear all localStorage items related to Supabase
const keysToRemove = [];
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  if (key && key.includes('supabase') || key && key.includes('sb-')) {
    keysToRemove.push(key);
  }
}

keysToRemove.forEach(key => {
  console.log('Removing localStorage key:', key);
  localStorage.removeItem(key);
});

// Clear sessionStorage
sessionStorage.clear();
console.log('✅ SessionStorage cleared');

// Clear specific Supabase auth token patterns
const commonKeys = [
  'supabase.auth.token',
  'sb-auth-token',
  'sb-refresh-token',
  'sb-session'
];

commonKeys.forEach(key => {
  localStorage.removeItem(key);
  sessionStorage.removeItem(key);
});

console.log('✅ Authentication storage cleared! Please refresh the page.');
console.log('🔄 You may need to restart your dev server as well.');

// Optional: Reload the page
// window.location.reload(); 