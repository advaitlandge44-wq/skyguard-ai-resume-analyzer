/**
 * AI Resume Career Assistant Chat Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-input-form');
  const chatInput = document.getElementById('chat-message-input');
  const chatMessages = document.getElementById('chat-messages-container');
  const sendBtn = document.getElementById('chat-send-btn');
  const suggestionChips = document.querySelectorAll('.chat-suggestion-chip');
  const analysisIdMeta = document.getElementById('chat-analysis-id');

  const analysisId = analysisIdMeta ? analysisIdMeta.value : null;

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
  if (chatForm && analysisId) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const message = chatInput ? chatInput.value.trim() : '';
      if (!message) return;

      // Append user bubble
      appendMessage('user', message);
      chatInput.value = '';

      // Typing indicator
      const typingIndicator = appendTypingIndicator();
      scrollToBottom();

      if (sendBtn) sendBtn.disabled = true;

      try {
        const response = await fetch(`/api/chat/${analysisId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        typingIndicator.remove();

        if (response.ok && data.success) {
          appendMessage('assistant', data.reply);
        } else {
          appendMessage('assistant', data.error || 'Sorry, I could not process that request. Please try again.');
        }
      } catch (err) {
        typingIndicator.remove();
        appendMessage('assistant', 'Network error. Please check your connection and try again.');
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

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chat-bubble-content';
    
    // Format line breaks
    bubbleDiv.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');

    msgDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
    return msgDiv;
  }

  function appendTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'chat-bubble-row assistant typing-indicator-msg';
    indicator.innerHTML = `
      <div class="chat-bubble-content" style="opacity: 0.8; font-style: italic;">
        <span style="display:inline-block; animation: pulse 1.5s infinite;">● AI is thinking...</span>
      </div>
    `;
    chatMessages.appendChild(indicator);
    return indicator;
  }

  function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string;
    return div.innerHTML;
  }
});
