
(function ChatPage() {
  'use strict';

  const { Toast, API, formatTime } = window.UniHelp;

  // ── DOM refs ───────────────────────────────────────────────
  const statusBadge   = document.getElementById('index-status');
  const chatMessages  = document.getElementById('chatMessages');
  const chatForm      = document.getElementById('chatForm');
  const questionInput = document.getElementById('questionInput');
  const sendBtn       = document.getElementById('sendBtn');
  const emptyState    = document.getElementById('emptyState');

  // ── State ──────────────────────────────────────────────────
  let isIndexReady = false;
  let isWaiting    = false;
  let sessionId    = null;
  let typingEl     = null;

  // ── Index status ───────────────────────────────────────────
  async function checkIndexStatus() {
    try {
      const data = await API.get('/api/chat/index-status');
      isIndexReady = data.is_ready;

      if (isIndexReady) {
        statusBadge.className   = 'status-badge ready';
        statusBadge.textContent = '✓ Index prêt';
        questionInput.disabled  = false;
        sendBtn.disabled        = false;
      } else {
        statusBadge.className   = 'status-badge loading';
        statusBadge.textContent = 'Index non construit';
        questionInput.disabled  = true;
        sendBtn.disabled        = true;
      }
    } catch (err) {
      statusBadge.className   = 'status-badge error';
      statusBadge.textContent = '✗ Hors ligne';
      console.error('[Chat] index-status error:', err);
    }
  }

  // ── Send message ───────────────────────────────────────────
  async function sendMessage(question) {
    if (!question.trim() || isWaiting || !isIndexReady) return;

    hideEmptyState();
    addMessage(question, 'user');
    questionInput.value = '';
    questionInput.style.height = 'auto';

    setWaiting(true);
    showTyping();

    try {
      const data = await API.post('/api/chat/ask', {
        question,
        session_id: sessionId,
      });

      sessionId = data.session_id || sessionId;
      removeTyping();
      addMessage(data.answer || '(Réponse vide)', 'assistant', data.sources || []);

    } catch (err) {
      removeTyping();
      addMessage(`Erreur : ${err.message}`, 'error');
      Toast.error('Échec de la requête.');
    } finally {
      setWaiting(false);
    }
  }

  // ── Add message to DOM ─────────────────────────────────────
  function addMessage(content, role, sources = []) {
    const wrapper = document.createElement('div');
    wrapper.className = `message ${role}`;

    const avatarMap = { user: '👤', assistant: '🤖', system: '📢', error: '⚠' };

    if (role !== 'error') {
      const avatar = document.createElement('div');
      avatar.className = 'msg-avatar';
      avatar.textContent = avatarMap[role] || '?';
      wrapper.appendChild(avatar);
    }

    const body = document.createElement('div');
    body.className = 'msg-body';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.textContent = content;
    body.appendChild(bubble);

    // Sources accordion
    if (sources.length > 0) {
      const toggle = document.createElement('button');
      toggle.className = 'sources-toggle';
      toggle.innerHTML = `<span>📎 ${sources.length} source${sources.length > 1 ? 's' : ''}</span><span class="chevron">▾</span>`;

      const list = document.createElement('div');
      list.className = 'sources-list';
      sources.forEach(src => {
        const item = document.createElement('div');
        item.className = 'source-item';
        item.textContent = src.filename || src.source || src;
        list.appendChild(item);
      });

      toggle.addEventListener('click', () => {
        const isOpen = list.classList.toggle('visible');
        toggle.classList.toggle('open', isOpen);
      });

      body.appendChild(toggle);
      body.appendChild(list);
    }

    // Timestamp
    if (role === 'user' || role === 'assistant') {
      const time = document.createElement('span');
      time.className = 'msg-time';
      time.textContent = formatTime();
      body.appendChild(time);
    }

    wrapper.appendChild(body);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
  }

  // ── Typing indicator ───────────────────────────────────────
  function showTyping() {
    typingEl = document.createElement('div');
    typingEl.className = 'message assistant typing-indicator';
    typingEl.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-body">
        <div class="msg-bubble">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>`;
    chatMessages.appendChild(typingEl);
    scrollToBottom();
  }

  function removeTyping() {
    if (typingEl) { typingEl.remove(); typingEl = null; }
  }

  // ── UI helpers ─────────────────────────────────────────────
  function setWaiting(state) {
    isWaiting              = state;
    sendBtn.disabled       = state;
    questionInput.disabled = state || !isIndexReady;

    sendBtn.innerHTML = state
      ? '<div class="spinner"></div>'
      : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
           <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
         </svg>`;
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function hideEmptyState() {
    if (emptyState) emptyState.style.display = 'none';
  }

  // ── Suggestion chips ───────────────────────────────────────
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      if (!isIndexReady) return;
      questionInput.value = chip.textContent.trim();
      questionInput.focus();
    });
  });

  // ── Auto-resize textarea ───────────────────────────────────
  questionInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 130) + 'px';
  });

  // ── Submit on Enter (Shift+Enter = newline) ────────────────
  questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // ── Form submit ────────────────────────────────────────────
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(questionInput.value.trim());
  });

  // ── Init ───────────────────────────────────────────────────
  checkIndexStatus();

  // Re-check when tab regains focus
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) checkIndexStatus();
  });

})();