// ============================================================
// UniHelp – Documents Page
// Connects to: GET  /api/documents/status
//              POST /api/documents/build-index
//              POST /api/documents/load-index
//              POST /api/documents/upload  (if endpoint added)
// ============================================================

(function DocumentsPage() {
  'use strict';

  const { Toast, API, formatBytes } = window.UniHelp;

  // ── DOM refs ───────────────────────────────────────────────
  const docList         = document.getElementById('docList');
  const docCountBadge   = document.getElementById('docCountBadge');
  const statDocCount    = document.getElementById('statDocCount');
  const statIndexStatus = document.getElementById('statIndexStatus');
  const uploadArea      = document.getElementById('uploadArea');
  const fileInput       = document.getElementById('fileInput');
  const progressWrap    = document.getElementById('progressWrap');
  const progressFill    = document.getElementById('progressFill');
  const progressText    = document.getElementById('progressText');
  const buildBtn        = document.getElementById('buildIndexBtn');
  const loadBtn         = document.getElementById('loadIndexBtn');
  const buildProgress   = document.getElementById('buildProgress');
  const refreshBtn      = document.getElementById('refreshBtn');

  // ── Fetch and render status ────────────────────────────────
  async function loadStatus() {
    try {
      const data = await API.get('/api/documents/status');

      const count = data.document_count || 0;

      if (statDocCount) statDocCount.textContent = count;

      if (statIndexStatus) {
        statIndexStatus.textContent = data.is_ready ? 'Prêt' : 'Non construit';
        statIndexStatus.className   = data.is_ready ? 'stat-value text-success' : 'stat-value';
        statIndexStatus.style.color = data.is_ready ? '#4ade80' : 'var(--text-primary)';
      }

      if (docCountBadge) docCountBadge.textContent = `${count} doc${count !== 1 ? 's' : ''}`;

      renderDocList(count);
    } catch (err) {
      console.error('[Documents] status error:', err);
      Toast.error('Impossible de charger le statut.');
    }
  }

  // ── Render document list (placeholder names from count) ────
  function renderDocList(count) {
    if (!docList) return;
    docList.innerHTML = '';

    if (count === 0) {
      docList.innerHTML = `
        <div class="list-placeholder">
          <div class="list-placeholder-icon">📂</div>
          <p>Aucun document indexé.<br>Uploadez des PDFs et construisez l'index.</p>
        </div>`;
      return;
    }

    // The backend doesn't expose individual filenames currently,
    // so we show a summary row. Extend this when a /list endpoint is added.
    for (let i = 0; i < count; i++) {
      const item = createDocItem(`Document ${i + 1}`, 'PDF', '');
      docList.appendChild(item);
    }
  }

  function createDocItem(name, type, meta) {
    const div = document.createElement('div');
    div.className = 'doc-item';
    div.innerHTML = `
      <div class="doc-file-icon">PDF</div>
      <div class="doc-details">
        <div class="doc-name">${escapeHTML(name)}</div>
        ${meta ? `<div class="doc-meta">${escapeHTML(meta)}</div>` : ''}
      </div>`;
    return div;
  }

  // ── Build index ────────────────────────────────────────────
  async function buildIndex() {
    if (!buildBtn) return;
    buildBtn.disabled = true;

    if (buildProgress) buildProgress.classList.add('visible');

    try {
      const data = await API.post('/api/documents/build-index', {});
      Toast.success(`Index construit — ${data.document_count || 0} document(s).`);
      await loadStatus();
    } catch (err) {
      Toast.error(`Échec : ${err.message}`);
    } finally {
      buildBtn.disabled = false;
      if (buildProgress) buildProgress.classList.remove('visible');
    }
  }

  // ── Load existing index ────────────────────────────────────
  async function loadIndex() {
    if (!loadBtn) return;
    loadBtn.disabled = true;
    try {
      const data = await API.post('/api/documents/load-index', {});
      if (data.status === 'success') {
        Toast.success(data.message);
        await loadStatus();
      } else {
        Toast.info(data.message || 'Aucun index existant trouvé.');
      }
    } catch (err) {
      Toast.error(`Échec : ${err.message}`);
    } finally {
      loadBtn.disabled = false;
    }
  }

  // ── File upload (drag-and-drop + click) ───────────────────
  function handleFiles(files) {
    const pdfs = Array.from(files).filter(f => f.type === 'application/pdf');
    if (pdfs.length === 0) { Toast.error('Seuls les fichiers PDF sont acceptés.'); return; }
    uploadFiles(pdfs);
  }

  async function uploadFiles(files) {
    if (progressWrap) progressWrap.classList.add('visible');
    setProgress(0, `Upload de ${files.length} fichier(s)…`);

    let uploaded = 0;
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        // Note: add /api/documents/upload endpoint on backend to enable this
        await fetch('/api/documents/upload', {
          method: 'POST',
          body: formData,
        });

        uploaded++;
        setProgress((uploaded / files.length) * 100, `${uploaded}/${files.length} — ${file.name}`);
      } catch (err) {
        Toast.error(`Échec upload : ${file.name}`);
      }
    }

    setProgress(100, `${uploaded} fichier(s) uploadé(s).`);
    setTimeout(() => {
      if (progressWrap) progressWrap.classList.remove('visible');
      setProgress(0, '');
    }, 2000);

    if (uploaded > 0) {
      Toast.success(`${uploaded} PDF(s) uploadé(s) avec succès.`);
      await loadStatus();
    }
  }

  function setProgress(pct, text) {
    if (progressFill) progressFill.style.width = `${pct}%`;
    if (progressText) progressText.textContent  = text;
  }

  // ── Drag-and-drop listeners ────────────────────────────────
  if (uploadArea) {
    uploadArea.addEventListener('click', () => fileInput && fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) handleFiles(fileInput.files);
    });
  }

  // ── Button listeners ───────────────────────────────────────
  if (buildBtn)   buildBtn.addEventListener('click', buildIndex);
  if (loadBtn)    loadBtn.addEventListener('click', loadIndex);
  if (refreshBtn) refreshBtn.addEventListener('click', loadStatus);

  // ── Utility ────────────────────────────────────────────────
  function escapeHTML(str) {
    return str.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // ── Init ───────────────────────────────────────────────────
  loadStatus();

})();