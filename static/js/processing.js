// HeartSeg AI v2 · Processing Animation Scripts

// ── Background particles ────────────────────────────────────
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
    const spacing = 50;
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
      const r = 1 + pulse * 1.2;
      ctx.beginPath();
      ctx.arc(d.x, d.y, r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 77, 109, ${0.08 + pulse * 0.1})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(draw);
})();

// ── Step animation controller ───────────────────────────────
const steps = [
  { id: 'step-1', name: 'Preprocessing', duration: 800 },
  { id: 'step-2', name: 'U-Net Segmentation', duration: 1200 },
  { id: 'step-3', name: 'CNN Classification', duration: 1000 },
  { id: 'step-4', name: 'Grad-CAM Explainability', duration: 900 },
  { id: 'step-5', name: 'Generating Report', duration: 600 },
];

let currentStep = 0;

function updateStep(index, state) {
  const el = document.getElementById(steps[index].id);
  if (!el) return;

  const statusEl = el.querySelector('.step-status');
  const fillEl = el.querySelector('.step-fill');

  if (state === 'running') {
    el.classList.add('active');
    el.classList.remove('complete');
    statusEl.textContent = 'Running…';
    statusEl.dataset.status = 'running';
    fillEl.style.width = '0%';
  } else if (state === 'complete') {
    el.classList.remove('active');
    el.classList.add('complete');
    statusEl.textContent = 'Complete';
    statusEl.dataset.status = 'complete';
    fillEl.style.width = '100%';
  }
}

function animateFill(index, duration) {
  const el = document.getElementById(steps[index].id);
  const fillEl = el.querySelector('.step-fill');
  fillEl.style.transition = `width ${duration}ms linear`;
  fillEl.style.width = '100%';
}

function runSequence() {
  if (currentStep >= steps.length) {
    // All steps done — trigger backend analysis
    triggerAnalysis();
    return;
  }

  updateStep(currentStep, 'running');
  animateFill(currentStep, steps[currentStep].duration);

  setTimeout(() => {
    updateStep(currentStep, 'complete');
    currentStep++;
    runSequence();
  }, steps[currentStep].duration);
}

// ── Trigger actual analysis ─────────────────────────────────
function triggerAnalysis() {
  fetch('/run-analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: JOB_ID })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      window.location.href = '/result';
    } else {
      alert('Analysis failed. Please try again.');
      window.location.href = '/upload';
    }
  })
  .catch(err => {
    console.error(err);
    alert('Network error. Please try again.');
    window.location.href = '/upload';
  });
}

// ── Start on load ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Small delay before starting
  setTimeout(runSequence, 400);
});