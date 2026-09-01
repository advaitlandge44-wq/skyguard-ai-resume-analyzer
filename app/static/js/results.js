/**
 * Analysis Results Dashboard Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // Animate Circular Score Gauges
  const gauges = document.querySelectorAll('.gauge-circle-progress');
  gauges.forEach(gauge => {
    const score = parseInt(gauge.getAttribute('data-score') || '0', 10);
    const radius = parseFloat(gauge.getAttribute('r') || '48');
    const circumference = 2 * Math.PI * radius;
    
    gauge.style.strokeDasharray = `${circumference} ${circumference}`;
    gauge.style.strokeDashoffset = circumference;

    const offset = circumference - (score / 100) * circumference;
    
    // Trigger animation
    setTimeout(() => {
      gauge.style.strokeDashoffset = offset;
    }, 200);
  });

  // Animated Count-Up Numbers
  const countUpElements = document.querySelectorAll('.count-up');
  countUpElements.forEach(el => {
    const target = parseInt(el.getAttribute('data-target') || '0', 10);
    let current = 0;
    const increment = Math.ceil(target / 40) || 1;
    const duration = 1200;
    const intervalTime = Math.floor(duration / (target / increment || 1));

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current;
    }, 25);
  });

  // Tab Navigation Handling
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

  // Print / Export trigger
  const printBtn = document.getElementById('export-pdf-btn');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }

  // Copy Buttons
  const copyBtns = document.querySelectorAll('.btn-copy-snippet');
  copyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const textToCopy = btn.getAttribute('data-text') || '';
      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
          showToast('Copied to clipboard!', 'success');
        }).catch(() => {
          showToast('Failed to copy to clipboard.', 'danger');
        });
      }
    });
  });
});
