// ============================================================
// UniHelp – Email Generator Page
// Connects to: GET  /api/email/templates
//              POST /api/email/generate
// ============================================================

(function EmailPage() {
  'use strict';

  const { Toast, API, formatTime } = window.UniHelp;

  // ── DOM refs ───────────────────────────────────────────────
  const emailForm        = document.getElementById('emailForm');
  const recipientInput   = document.getElementById('recipient');
  const subjectInput     = document.getElementById('subject');
  const contextInput     = document.getElementById('context');
  const templateChips    = document.getElementById('templateChips');
  const templateSelect   = document.getElementById('templateSelect');
  const generateBtn      = document.getElementById('generateBtn');

  const previewContent   = document.getElementById('previewContent');
  const previewSubject   = document.getElementById('previewSubject');
  const previewSubjectTx = document.getElementById('previewSubjectText');
  const previewMeta      = document.getElementById('previewMeta');
  const previewMetaTo    = document.getElementById('previewMetaTo');
  const previewMetaTime  = document.getElementById('previewMetaTime');
  const previewActions   = document.getElementById('previewActions');
  const previewLoading   = document.getElementById('previewLoading');
  const copyBtn          = document.getElementById('copyBtn');
  const downloadBtn      = document.getElementById('downloadBtn');

  // ── State ──────────────────────────────────────────────────
  let selectedTemplate = '';
  let generatedContent = '';

  // ── Load templates from API ────────────────────────────────
  async function loadTemplates() {
    try {
      const data = await API.get('/api/email/templates');
      const templates = data.templates || [];

      renderTemplateChips(templates);
      renderTemplateSelect(templates);
    } catch (err) {
      console.warn('[Email] Could not load templates:', err);
      // Fallback to hardcoded templates
      const fallback = [
        { id: 'professional', label: 'Professionnel' },
        { id: 'friendly',     label: 'Amical' },
        { id: 'formal',       label: 'Formel' },
      ];
      renderTemplateChips(fallback);
      renderTemplateSelect(fallback);
    }
  }

  function renderTemplateChips(templates) {
    if (!templateChips || templates.length === 0) return;
    templateChips.innerHTML = '';

    templates.forEach(tpl => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'template-chip';
      chip.textContent = tpl.label || tpl.id || tpl;
      chip.dataset.id  = tpl.id || tpl;

      chip.addEventListener('click', () => selectTemplate(chip.dataset.id, chip));
      templateChips.appendChild(chip);
    });
  }

  function renderTemplateSelect(templates) {
    if (!templateSelect) return;
    // Clear existing dynamic options (keep first placeholder)
    while (templateSelect.options.length > 1) templateSelect.remove(1);

    templates.forEach(tpl => {
      const opt   = document.createElement('option');
      opt.value   = tpl.id || tpl;
      opt.textContent = tpl.label || tpl.id || tpl;
      templateSelect.appendChild(opt);
    });

    templateSelect.addEventListener('change', () => {
      selectedTemplate = templateSelect.value;
      // Sync chip selection
      document.querySelectorAll('.template-chip').forEach(c => {
        c.classList.toggle('selected', c.dataset.id === selectedTemplate);
      });
    });
  }

  function selectTemplate(id, chipEl) {
    selectedTemplate = id;
    document.querySelectorAll('.template-chip').forEach(c => c.classList.remove('selected'));
    if (chipEl) chipEl.classList.add('selected');
    if (templateSelect) templateSelect.value = id;
  }

  // ── Generate email ─────────────────────────────────────────
  async function generateEmail() {
    const recipient = recipientInput?.value.trim() || '';
    const subject   = subjectInput?.value.trim()   || '';
    const context   = contextInput?.value.trim()   || '';

    if (!context) { Toast.error('Le contexte est requis.'); contextInput?.focus(); return; }
    if (!subject)  { Toast.error("L'objet est requis."); subjectInput?.focus(); return; }

    setGenerating(true);
    showPreviewLoading(true);

    try {
      const data = await API.post('/api/email/generate', {
        recipient,
        subject,
        context,
        template: selectedTemplate || null,
      });

      generatedContent = data.email_content || '';

      showGeneratedEmail(data);
      Toast.success('Email généré !');

    } catch (err) {
      showPreviewLoading(false);
      Toast.error(`Échec : ${err.message}`);
    } finally {
      setGenerating(false);
    }
  }

  // ── Render generated email ─────────────────────────────────
  function showGeneratedEmail(data) {
    showPreviewLoading(false);

    // Subject strip
    if (previewSubject && previewSubjectTx) {
      previewSubjectTx.textContent = data.subject || '';
      previewSubject.classList.toggle('visible', !!data.subject);
    }

    // Meta tags
    if (previewMeta) {
      if (previewMetaTo)   previewMetaTo.querySelector('span').textContent   = data.recipient || 'Non spécifié';
      if (previewMetaTime) previewMetaTime.querySelector('span').textContent = formatTime(new Date(data.created_at || Date.now()));
      previewMeta.classList.add('visible');
    }

    // Content
    if (previewContent) {
      previewContent.innerHTML = '';
      previewContent.textContent = generatedContent;
    }

    if (previewActions) previewActions.classList.add('visible');
  }

  function showPreviewLoading(show) {
    if (previewLoading) previewLoading.classList.toggle('visible', show);
    if (previewContent && show) previewContent.textContent = '';
    if (previewActions && show) previewActions.classList.remove('visible');
  }

  // ── Copy to clipboard ──────────────────────────────────────
  async function copyToClipboard() {
    if (!generatedContent) return;
    try {
      await navigator.clipboard.writeText(generatedContent);
      if (copyBtn) {
        const orig = copyBtn.textContent;
        copyBtn.textContent = '✓ Copié !';
        setTimeout(() => { copyBtn.textContent = orig; }, 2000);
      }
      Toast.success('Copié dans le presse-papier.');
    } catch (_) {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = generatedContent;
      ta.style.position = 'fixed';
      ta.style.opacity  = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      Toast.success('Copié.');
    }
  }

  // ── Download as .txt ───────────────────────────────────────
  function downloadEmail() {
    if (!generatedContent) return;
    const subject = subjectInput?.value.trim().replace(/[^a-z0-9]/gi, '_') || 'email';
    const blob = new Blob([generatedContent], { type: 'text/plain;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `${subject}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── UI state ───────────────────────────────────────────────
  function setGenerating(state) {
    if (!generateBtn) return;
    generateBtn.disabled = state;
    generateBtn.innerHTML = state
      ? `<div class="spinner"></div><span>Génération…</span>`
      : `<span>Générer l'Email</span><span>✨</span>`;
  }

  // ── Event listeners ────────────────────────────────────────
  if (emailForm) {
    emailForm.addEventListener('submit', (e) => { e.preventDefault(); generateEmail(); });
  }

  if (copyBtn)     copyBtn.addEventListener('click', copyToClipboard);
  if (downloadBtn) downloadBtn.addEventListener('click', downloadEmail);

  // ── Init ───────────────────────────────────────────────────
  loadTemplates();

})();