// HeartSeg AI v2 · Result page scripts

// ── Animate confidence bars on page load ─────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Reset bars to 0 then animate to target width
  const fills  = document.querySelectorAll('.confidence-fill');
  const probBars = document.querySelectorAll('.prob-bar');

  fills.forEach(el => {
    const target = el.style.width;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = target; }, 100);
  });

  probBars.forEach(el => {
    const parent = el.parentElement;
    // Width is set inline on el via parent row's prob percentage
    const targetPct = el.style.width;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = targetPct; }, 200);
  });
});
