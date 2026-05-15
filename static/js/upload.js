// HeartSeg AI v2 · Upload page scripts

const dropZone   = document.getElementById('drop-zone');
const fileInput  = document.getElementById('file-input');
const dzIdle     = document.getElementById('dz-idle');
const dzPreview  = document.getElementById('dz-preview');
const previewImg = document.getElementById('preview-img');
const prevName   = document.getElementById('preview-name');
const prevSize   = document.getElementById('preview-size');
const btnAnalyse = document.getElementById('btn-analyse');
const form       = document.getElementById('upload-form');
const btnText    = form.querySelector('.btn-text');
const btnLoader  = form.querySelector('.btn-loader');

// ── File size formatter ──────────────────────────────────────
function formatSize(bytes) {
  if (bytes < 1024)        return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ── Show preview ─────────────────────────────────────────────
function showPreview(file) {
  if (!file || !file.type.startsWith('image/')) {
    alert('Please upload a PNG or JPG image file.');
    return;
  }
  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    prevName.textContent = file.name;
    prevSize.textContent = formatSize(file.size);
    dzIdle.hidden    = true;
    dzPreview.hidden = false;
    btnAnalyse.disabled = false;
  };
  reader.readAsDataURL(file);
}

// ── Clear file ───────────────────────────────────────────────
function clearFile() {
  fileInput.value    = '';
  previewImg.src     = '';
  dzIdle.hidden      = false;
  dzPreview.hidden   = true;
  btnAnalyse.disabled = true;
}
window.clearFile = clearFile;

// ── File input change ────────────────────────────────────────
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showPreview(fileInput.files[0]);
});

// ── Drag and drop ────────────────────────────────────────────
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) {
    // Create a DataTransfer to assign file to input
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    showPreview(file);
  }
});

// Click on idle zone triggers browse
dropZone.addEventListener('click', e => {
  if (dzPreview.hidden === false) return; // don't trigger when preview shown
  fileInput.click();
});

// ── Form submit — show loading state ─────────────────────────
form.addEventListener('submit', () => {
  btnText.hidden   = true;
  btnLoader.hidden = false;
  btnAnalyse.disabled = true;
});
