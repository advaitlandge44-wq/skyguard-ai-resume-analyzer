/**
 * Analysis Results Dashboard Client Script
 * Connected to SkyGuard AI API backend (Render)
 */

document.addEventListener('DOMContentLoaded', async () => {
  const usp = new URLSearchParams(window.location.search);
  const analysisId = usp.get('id');
  const isDemo = usp.get('demo') === 'true' || window.location.pathname.includes('demo');

  // If page content needs dynamic hydration from Render backend API
  const dynamicContainer = document.getElementById('dynamic-results-view');
  if (dynamicContainer && (analysisId || isDemo)) {
    try {
      let analysisData = null;
      if (isDemo) {
        const demoRes = await window.SkyGuardAPI.demo.getData();
        if (demoRes && demoRes.analysis) {
          analysisData = demoRes.analysis;
        }
      } else if (analysisId) {
        const res = await window.SkyGuardAPI.analysis.get(analysisId);
        if (res && res.analysis) {
          analysisData = res.analysis;
        }
      }

      if (analysisData) {
        renderDynamicResults(analysisData);
      }
    } catch (err) {
      console.error('Failed to load analysis data:', err);
      if (err.status === 401) {
        if (window.showToast) window.showToast('Please log in to view this analysis report.', 'warning');
        setTimeout(() => {
          window.location.href = `login.html?next=results.html?id=${analysisId}`;
        }, 1500);
      } else if (dynamicContainer) {
        dynamicContainer.innerHTML = `
          <div class="empty-placeholder" style="margin-top: 3rem;">
            <div class="empty-placeholder-icon">⚠️</div>
            <h3>Analysis Report Not Found</h3>
            <p>${err.message || 'Unable to retrieve analysis data. The session may have expired or was removed.'}</p>
            <a href="upload.html" class="btn btn-primary">Scan New Resume</a>
          </div>
        `;
      }
    }
  }

  // Initialize gauges and interactive handlers
  initGauges();
  initCountUps();
  initTabs();
  initPrintAndCopy();
});

function initGauges() {
  const gauges = document.querySelectorAll('.gauge-circle-progress');
  gauges.forEach(gauge => {
    let score = parseInt(gauge.getAttribute('data-score') || '0', 10);
    if (isNaN(score)) score = 0;
    score = Math.max(0, Math.min(100, score));

    const radiusAttr = gauge.getAttribute('r') || (gauge.r && gauge.r.baseVal ? gauge.r.baseVal.value : 48);
    const radius = parseFloat(radiusAttr) || 48;
    const circumference = 2 * Math.PI * radius;
    
    gauge.style.strokeDasharray = `${circumference} ${circumference}`;
    gauge.style.strokeDashoffset = `${circumference}`;

    const offset = circumference - (score / 100) * circumference;
    
    setTimeout(() => {
      gauge.style.strokeDashoffset = `${offset}`;
    }, 150);
  });
}

function initCountUps() {
  const countUpElements = document.querySelectorAll('.count-up');
  countUpElements.forEach(el => {
    const target = parseInt(el.getAttribute('data-target') || '0', 10);
    let current = 0;
    const increment = Math.ceil(target / 40) || 1;
    const duration = 1200;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current;
    }, 25);
  });
}

function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');

      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const activePane = document.getElementById(`tab-${targetTab}`);
      if (activePane) {
        activePane.classList.add('active');
      }
    });
  });
}

function initPrintAndCopy() {
  const printBtn = document.getElementById('export-pdf-btn');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }

  const copyBtns = document.querySelectorAll('.btn-copy-snippet');
  copyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const textToCopy = btn.getAttribute('data-text') || '';
      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
          if (window.showToast) window.showToast('Copied to clipboard!', 'success');
        }).catch(() => {
          if (window.showToast) window.showToast('Failed to copy to clipboard.', 'danger');
        });
      }
    });
  });
}

function renderDynamicResults(analysis) {
  const data = analysis.data || {};
  
  // Set target role badge
  const roleEl = document.getElementById('results-target-role-text');
  if (roleEl) roleEl.textContent = analysis.target_role || 'Target Role';

  // Set score text
  const overallEl = document.getElementById('overall-score-num');
  if (overallEl) overallEl.textContent = analysis.overall_score || 75;

  const atsEl = document.getElementById('ats-score-num');
  if (atsEl) atsEl.textContent = analysis.ats_score || 75;

  const matchEl = document.getElementById('match-score-num');
  if (matchEl) matchEl.textContent = analysis.job_match_score || 70;

  // Set gauges data-score
  const gaugeOverall = document.getElementById('gauge-overall');
  if (gaugeOverall) gaugeOverall.setAttribute('data-score', analysis.overall_score || 75);

  const gaugeAts = document.getElementById('gauge-ats');
  if (gaugeAts) gaugeAts.setAttribute('data-score', analysis.ats_score || 75);

  const gaugeMatch = document.getElementById('gauge-match');
  if (gaugeMatch) gaugeMatch.setAttribute('data-score', analysis.job_match_score || 70);

  // Set Summary
  const summaryEl = document.getElementById('results-summary-text');
  if (summaryEl) summaryEl.textContent = analysis.summary || data.summary || 'Resume analyzed successfully.';

  // Set hidden analysis ID for chat
  const chatMeta = document.getElementById('chat-analysis-id');
  if (chatMeta) chatMeta.value = analysis.id;

  // Re-run gauges animation
  initGauges();
}
