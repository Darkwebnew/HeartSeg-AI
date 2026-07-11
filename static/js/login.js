// HeartSeg AI v2 · Login page scripts

// ── Constellation Canvas Background ─────────────────────────
(function () {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let w, h, dots = [];
  const DOT_COUNT = 80;
  const CONNECTION_DIST = 120;
  const MOUSE_DIST = 150;

  let mouse = { x: null, y: null };

  function resize() {
    w = canvas.width  = window.innerWidth;
    h = canvas.height = window.innerHeight;
    initDots();
  }

  function initDots() {
    dots = [];
    for (let i = 0; i < DOT_COUNT; i++) {
      dots.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 1.5 + 0.5,
        base: Math.random() * Math.PI * 2
      });
    }
  }

  function draw(t) {
    ctx.clearRect(0, 0, w, h);
    const time = t * 0.001;

    // Update positions
    dots.forEach(d => {
      d.x += d.vx;
      d.y += d.vy;

      // Bounce off edges
      if (d.x < 0 || d.x > w) d.vx *= -1;
      if (d.y < 0 || d.y > h) d.vy *= -1;

      // Pulse radius
      const pulse = 0.5 + 0.5 * Math.sin(d.base + time);
      const r = d.r * (0.8 + pulse * 0.4);

      // Draw dot
      ctx.beginPath();
      ctx.arc(d.x, d.y, r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 77, 109, ${0.15 + pulse * 0.25})`;
      ctx.fill();
    });

    // Draw connections
    for (let i = 0; i < dots.length; i++) {
      for (let j = i + 1; j < dots.length; j++) {
        const dx = dots[i].x - dots[j].x;
        const dy = dots[i].y - dots[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECTION_DIST) {
          const opacity = (1 - dist / CONNECTION_DIST) * 0.12;
          ctx.beginPath();
          ctx.moveTo(dots[i].x, dots[i].y);
          ctx.lineTo(dots[j].x, dots[j].y);
          ctx.strokeStyle = `rgba(255, 77, 109, ${opacity})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }

      // Mouse connection
      if (mouse.x !== null) {
        const mdx = dots[i].x - mouse.x;
        const mdy = dots[i].y - mouse.y;
        const mDist = Math.sqrt(mdx * mdx + mdy * mdy);

        if (mDist < MOUSE_DIST) {
          const opacity = (1 - mDist / MOUSE_DIST) * 0.25;
          ctx.beginPath();
          ctx.moveTo(dots[i].x, dots[i].y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(61, 130, 247, ${opacity})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });
  window.addEventListener('mouseleave', () => {
    mouse.x = null;
    mouse.y = null;
  });

  resize();
  requestAnimationFrame(draw);
})();

// ── Floating Particles ─────────────────────────────────────
(function () {
  const container = document.getElementById('particles');
  if (!container) return;

  const PARTICLE_COUNT = 15;

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    
    const size = Math.random() * 4 + 2;
    const left = Math.random() * 100;
    const duration = Math.random() * 10 + 10;
    const delay = Math.random() * 10;
    
    p.style.width = `${size}px`;
    p.style.height = `${size}px`;
    p.style.left = `${left}%`;
    p.style.animationDuration = `${duration}s`;
    p.style.animationDelay = `${delay}s`;
    p.style.background = Math.random() > 0.5 ? 'var(--accent)' : 'var(--accent-2)';
    
    container.appendChild(p);
  }
})();

// ── Toggle Password Visibility ─────────────────────────────
function togglePw() {
  const input = document.getElementById('password');
  const icon  = document.getElementById('eye-icon');
  
  if (!input || !icon) return;

  if (input.type === 'password') {
    input.type = 'text';
    icon.innerHTML = `
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94l9.88 9.88z"></path>
      <path d="M9.9 4.24A9.93 9.93 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19l-6.72-6.72z"></path>
      <line x1="1" y1="1" x2="23" y2="23"></line>
    `;
  } else {
    input.type = 'password';
    icon.innerHTML = `
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
      <circle cx="12" cy="12" r="3"></circle>
    `;
  }
}

// ── Form Loading State ─────────────────────────────────────
(function () {
  const form = document.getElementById('login-form');
  const btn = document.getElementById('btn-login');
  
  if (form && btn) {
    form.addEventListener('submit', () => {
      btn.classList.add('loading');
      btn.disabled = true;
    });
  }
})();

// ── Input Focus Effects ────────────────────────────────────
(function () {
  const inputs = document.querySelectorAll('.input-wrap input');
  
  inputs.forEach(input => {
    input.addEventListener('focus', () => {
      input.closest('.field-group').style.transform = 'scale(1.01)';
      input.closest('.field-group').style.transition = 'transform 0.2s ease';
    });
    
    input.addEventListener('blur', () => {
      input.closest('.field-group').style.transform = 'scale(1)';
    });
  });
})();