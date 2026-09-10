/**
 * AI Resume Improver Client Script
 * Connected to SkyGuard AI API backend (Render)
 */

document.addEventListener('DOMContentLoaded', () => {
  const improverForm = document.getElementById('bullet-improver-form');
  const bulletInput = document.getElementById('improver-bullet-input');
  const targetRoleInput = document.getElementById('improver-target-role');
  const improveBtn = document.getElementById('improve-btn');
  const improverResultArea = document.getElementById('improver-result-area');
  const originalOutput = document.getElementById('improver-original-text');
  const improvedOutput = document.getElementById('improver-improved-text');
  const whyBetterOutput = document.getElementById('improver-why-better');
  const actionVerbsList = document.getElementById('improver-action-verbs');
  const copyImprovedBtn = document.getElementById('copy-improved-btn');
  const samplePills = document.querySelectorAll('.sample-pill-btn');

  // Quick-pick sample pills
  samplePills.forEach(pill => {
    pill.addEventListener('click', () => {
      const sampleText = pill.getAttribute('data-sample') || '';
      if (bulletInput) {
        bulletInput.value = sampleText;
        bulletInput.focus();
      }
    });
  });

  if (improverForm) {
    improverForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const bulletText = bulletInput ? bulletInput.value.trim() : '';
      const targetRole = targetRoleInput ? targetRoleInput.value.trim() : 'Software Engineer';

      if (!bulletText || bulletText.length < 5) {
        if (window.showToast) window.showToast('Please enter a sentence or project bullet to improve.', 'warning');
        return;
      }

      // Set loading state
      if (improveBtn) {
        improveBtn.disabled = true;
        improveBtn.innerHTML = `
          <svg class="spinner-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
          </svg>
          Improving with AI...
        `;
      }

      try {
        const data = await window.SkyGuardAPI.improver.improve(bulletText, targetRole);

        if (data && data.success) {
          if (originalOutput) originalOutput.textContent = data.original;
          if (improvedOutput) improvedOutput.textContent = data.improved;
          if (whyBetterOutput) whyBetterOutput.textContent = data.why_better;

          // Render action verb badges
          if (actionVerbsList) {
            actionVerbsList.innerHTML = '';
            (data.action_verbs_used || []).forEach(verb => {
              const span = document.createElement('span');
              span.className = 'badge badge-primary';
              span.textContent = `⚡ ${verb}`;
              actionVerbsList.appendChild(span);
            });
          }

          if (improverResultArea) {
            improverResultArea.style.display = 'block';
            improverResultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }

          if (window.showToast) window.showToast('Bullet point improved successfully!', 'success');
        } else {
          if (window.showToast) window.showToast((data && data.error) || 'Failed to improve bullet point.', 'danger');
        }
      } catch (err) {
        if (err.status === 401) {
          if (window.showToast) window.showToast('Please log in to use the AI bullet improver.', 'warning');
        } else {
          const displayMsg = (window.SkyGuardAPI && window.SkyGuardAPI.extractErrorMessage)
            ? window.SkyGuardAPI.extractErrorMessage(err, 'Network error while contacting AI service.')
            : (err.message || 'Network error while contacting AI service.');
          if (window.showToast) window.showToast(displayMsg, 'danger');
        }
      } finally {
        if (improveBtn) {
          improveBtn.disabled = false;
          improveBtn.innerHTML = `<span>✨ Enhance Bullet Point</span>`;
        }
      }
    });
  }

  // Copy improved text
  if (copyImprovedBtn && improvedOutput) {
    copyImprovedBtn.addEventListener('click', () => {
      const text = improvedOutput.textContent;
      if (text) {
        navigator.clipboard.writeText(text).then(() => {
          if (window.showToast) window.showToast('Enhanced bullet copied to clipboard!', 'success');
        });
      }
    });
  }
});
