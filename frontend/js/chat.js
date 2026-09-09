/**
 * AI Resume Career Assistant Chat Client Script
 * Connected to SkyGuard AI API backend (Render)
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-input-form');
  const chatInput = document.getElementById('chat-message-input');
  const chatMessages = document.getElementById('chat-messages-container');
  const sendBtn = document.getElementById('chat-send-btn');
  const suggestionChips = document.querySelectorAll('.chat-suggestion-chip');
  const analysisIdMeta = document.getElementById('chat-analysis-id');

  let analysisId = analysisIdMeta ? analysisIdMeta.value : null;
  if (!analysisId) {
    const usp = new URLSearchParams(window.location.search);
    analysisId = usp.get('id');
  }

  // Auto-scroll chat to bottom
  function scrollToBottom() {
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  scrollToBottom();

  // Suggestion chips
  suggestionChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const question = chip.getAttribute('data-question') || chip.textContent.trim();
      if (chatInput) {
        chatInput.value = question;
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  // Handle message submission
  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const message = chatInput ? chatInput.value.trim() : '';
      if (!message) return;

      if (!analysisId) {
        if (window.showToast) window.showToast('Please select or upload a resume to start chat.', 'warning');
        return;
      }

      // Append user bubble
      appendMessage('user', message);
      chatInput.value = '';

      // Typing indicator
      const typingIndicator = appendTypingIndicator();
      scrollToBottom();

      if (sendBtn) sendBtn.disabled = true;

      try {
        const data = await window.SkyGuardAPI.chat.send(analysisId, message);
        typingIndicator.remove();

        if (data && data.success) {
          appendMessage('assistant', data.reply);
        } else {
          appendMessage('assistant', (data && data.error) || 'Sorry, I could not process that request. Please try again.');
        }
      } catch (err) {
        typingIndicator.remove();
        if (err.status === 401) {
          appendMessage('assistant', 'Session expired. Please log in again.');
        } else {
          appendMessage('assistant', err.message || 'Network error. Please check your connection and try again.');
        }
      } finally {
        if (sendBtn) sendBtn.disabled = false;
        scrollToBottom();
      }
    });
  }

  function appendMessage(role, text) {
    if (!chatMessages) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-bubble-row ${role}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = `chat-avatar-badge ${role}`;
    avatarDiv.textContent = role === 'user' ? 'YOU' : 'AI';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chat-bubble-content';
    bubbleDiv.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
    return msgDiv;
  }

  function appendTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'chat-bubble-row assistant typing-indicator-msg';
    indicator.innerHTML = `
      <div class="chat-avatar-badge assistant">AI</div>
      <div class="chat-bubble-content" style="display: flex; align-items: center; gap: 6px; padding: 0.75rem 1rem;">
        <span class="chat-typing-dot"></span>
        <span class="chat-typing-dot" style="animation-delay: 0.2s;"></span>
        <span class="chat-typing-dot" style="animation-delay: 0.4s;"></span>
      </div>
    `;
    chatMessages.appendChild(indicator);
    return indicator;
  }

  function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string || '';
    return div.innerHTML;
  }
});
