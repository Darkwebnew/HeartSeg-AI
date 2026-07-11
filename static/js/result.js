// HeartSeg AI v2 · Result Page Scripts (Advanced)

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active');
}

// ── Animate confidence gauges on page load ───────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Animate linear confidence bars
  const fills = document.querySelectorAll('.confidence-fill');
  const probBars = document.querySelectorAll('.prob-bar');

  fills.forEach(el => {
    const target = el.style.width;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = target; }, 100);
  });

  probBars.forEach(el => {
    const targetPct = el.style.width;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = targetPct; }, 200);
  });

  // Animate circular gauge
  const cgFill = document.getElementById('cg-fill');
  const cgPct = document.getElementById('cg-pct');
  if (cgFill && typeof CONFIDENCE_VALUE !== 'undefined') {
    const circumference = 326.73; // 2 * PI * 52
    const offset = circumference - (CONFIDENCE_VALUE / 100) * circumference;
    
    // Start at 0
    cgFill.style.strokeDashoffset = circumference;
    
    // Animate to value
    setTimeout(() => {
      cgFill.style.strokeDashoffset = offset;
    }, 300);

    // Animate number
    if (cgPct) {
      let current = 0;
      const target = Math.round(CONFIDENCE_VALUE);
      const duration = 1500;
      const step = target / (duration / 16);
      
      function animateNumber() {
        current += step;
        if (current >= target) {
          cgPct.textContent = target + '%';
          return;
        }
        cgPct.textContent = Math.round(current) + '%';
        requestAnimationFrame(animateNumber);
      }
      setTimeout(animateNumber, 300);
    }
  }

  // Animate risk gauge needle
  const needle = document.getElementById('gauge-needle');
  if (needle && typeof SEVERITY_LEVEL !== 'undefined') {
    const angles = {
      'none': -60,
      'medium': -15,
      'high': 30,
      'critical': 75
    };
    const targetAngle = angles[SEVERITY_LEVEL] || -90;
    
    setTimeout(() => {
      needle.style.transform = `rotate(${targetAngle}deg)`;
    }, 500);
  }
});