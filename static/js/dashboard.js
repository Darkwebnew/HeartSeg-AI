// HeartSeg AI v2 · Dashboard Scripts

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active');
}

// Animate confidence bars on load
document.addEventListener('DOMContentLoaded', () => {
  const bars = document.querySelectorAll('.confidence-fill-sm');
  bars.forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => { bar.style.width = target; }, 100);
  });
});