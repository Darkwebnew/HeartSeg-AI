// HeartSeg AI v2 · Settings Scripts

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active');
}

// ── Theme selector ───────────────────────────────────────────
document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// ── Show saved toast ─────────────────────────────────────────
function showSaved() {
  const toast = document.getElementById('save-toast');
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// ── Reset defaults ───────────────────────────────────────────
function resetDefaults() {
  // Reset theme
  document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-theme="dark"]').classList.add('active');
  
  // Reset toggles
  document.querySelectorAll('.toggle-switch input').forEach(toggle => {
    toggle.checked = false;
  });
  
  // Reset first two toggles to true
  const toggles = document.querySelectorAll('.toggle-switch input');
  if (toggles[0]) toggles[0].checked = true;
  if (toggles[2]) toggles[2].checked = true;
  if (toggles[3]) toggles[3].checked = true;
  if (toggles[4]) toggles[4].checked = true;
  
  // Reset inputs
  document.querySelectorAll('.settings-input').forEach(input => {
    if (input.type === 'number') {
      if (input.value > 50) input.value = 85;
      else input.value = 30;
    }
  });
  
  showSaved();
}

// ── Toggle sidebar on mobile ────────────────────────────────
window.toggleSidebar = toggleSidebar;