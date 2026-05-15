// HeartSeg AI v2 · Login page scripts

// ── Canvas dot-grid background ──────────────────────────────
(function () {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let w, h, dots = [];

  function resize() {
    w = canvas.width  = window.innerWidth;
    h = canvas.height = window.innerHeight;
    buildDots();
  }

  function buildDots() {
    dots = [];
    const spacing = 40;
    for (let x = 0; x < w + spacing; x += spacing) {
      for (let y = 0; y < h + spacing; y += spacing) {
        dots.push({ x, y, base: Math.random() * Math.PI * 2 });
      }
    }
  }

  function draw(t) {
    ctx.clearRect(0, 0, w, h);
    const time = t * 0.0005;
    dots.forEach(d => {
      const pulse = 0.5 + 0.5 * Math.sin(d.base + time);
      const r = 1 + pulse * 1.5;
      ctx.beginPath();
      ctx.arc(d.x, d.y, r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 77, 109, ${0.1 + pulse * 0.15})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(draw);
})();

// ── Toggle password visibility ───────────────────────────────
function togglePw() {
  const input = document.getElementById('password');
  const icon  = document.getElementById('eye-icon');
  if (input.type === 'password') {
    input.type = 'text';
    icon.innerHTML = `
      <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
      <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
    `;
  } else {
    input.type = 'password';
    icon.innerHTML = `
      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
      <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
    `;
  }
}
