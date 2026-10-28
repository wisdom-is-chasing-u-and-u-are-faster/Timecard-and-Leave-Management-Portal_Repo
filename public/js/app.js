/**
 * Enterprise HRMS UI Controller & State Manager
 */
document.addEventListener('DOMContentLoaded', async () => {
  console.log('⚡ Enterprise HRMS UI Initialized');

  // Verify backend health
  try {
    const health = await HRMS_API.getHealth();
    console.log('Backend Health Status:', health.status);
    const badge = document.getElementById('health-badge');
    if (badge) {
      badge.textContent = `Cloud Run: ${health.status.toUpperCase()}`;
      badge.className = 'badge badge-success';
    }
  } catch (err) {
    console.error('Health check failed:', err);
    const badge = document.getElementById('health-badge');
    if (badge) {
      badge.textContent = 'Service Disconnected';
      badge.className = 'badge badge-danger';
    }
  }

  // Load User Profile in Header
  try {
    const user = await HRMS_API.getMe();
    const userDisplay = document.getElementById('user-display');
    if (userDisplay) {
      userDisplay.textContent = `${user.name} (${user.role})`;
    }
  } catch (e) {
    console.warn('Could not load user profile', e);
  }
});

// Modal helpers
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('active');
}

window.openModal = openModal;
window.closeModal = closeModal;
