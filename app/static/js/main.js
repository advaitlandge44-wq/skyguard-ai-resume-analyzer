/**
 * SkyGuard AI - Master Client Interactions & Cinematic FX
 * 
 * Includes:
 * - Magnetic Button Attractions
 * - Neural Network Background Canvas
 * - Sequential AI Scanner Status Ticker
 * - Animated Score Numbers & Circular Progress Meters
 * - Section Highlight Handlers
 * - Navigation & Alert Utilities
 */

document.addEventListener('DOMContentLoaded', () => {
  const isTouchDevice = window.matchMedia('(hover: none) or (pointer: coarse)').matches;
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ========================================================
     1. NEURAL NETWORK CANVAS BACKGROUND
     ======================================================== */
  const neuralCanvas = document.getElementById('neural-bg-canvas');
  if (neuralCanvas && !prefersReducedMotion) {
    const ctx = neuralCanvas.getContext('2d');
    let width = neuralCanvas.width = window.innerWidth;
    let height = neuralCanvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      width = neuralCanvas.width = window.innerWidth;
      height = neuralCanvas.height = window.innerHeight;
    });

    const nodeCount = isTouchDevice ? 25 : 55;
    const nodes = [];

    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        radius: Math.random() * 1.8 + 1
      });
    }

    function drawNeuralNetwork() {
      ctx.clearRect(0, 0, width, height);

      // Draw connections
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 140) {
            const alpha = (1 - dist / 140) * 0.22;
            ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
            ctx.lineWidth = 0.75;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw and update nodes
      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        ctx.fillStyle = 'rgba(0, 240, 255, 0.45)';
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fill();

        n.x += n.vx;
        n.y += n.vy;

        if (n.x < 0 || n.x > width) n.vx *= -1;
        if (n.y < 0 || n.y > height) n.vy *= -1;
      }

      requestAnimationFrame(drawNeuralNetwork);
    }
    drawNeuralNetwork();
  }

  /* ========================================================
     3. MAGNETIC CTA BUTTONS
     ======================================================== */
  if (!isTouchDevice && !prefersReducedMotion) {
    const magneticButtons = document.querySelectorAll('.btn-cyan, .btn-primary, .btn-magnetic');
    magneticButtons.forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.22}px, ${y * 0.22}px)`;
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translate(0px, 0px)';
      });
    });
  }

  /* ========================================================
     4. SEQUENTIAL AI SCANNER STATUS TICKER
     ======================================================== */
  const scanSteps = document.querySelectorAll('.scan-step-item');
  if (scanSteps.length > 0) {
    let currentStep = 0;
    setInterval(() => {
      scanSteps.forEach((step, idx) => {
        if (idx < currentStep) {
          step.className = 'scan-step-item completed';
        } else if (idx === currentStep) {
          step.className = 'scan-step-item active';
        } else {
          step.className = 'scan-step-item';
        }
      });
      currentStep = (currentStep + 1) % (scanSteps.length + 2);
    }, 1800);
  }

  /* ========================================================
     5. ANIMATED SCORE COUNTERS & CIRCULAR PROGRESS METERS
     ======================================================== */
  const countUpElements = document.querySelectorAll('.count-up');
  if ('IntersectionObserver' in window && countUpElements.length > 0) {
    const scoreObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          if (el.classList.contains('count-up')) {
            const target = parseInt(el.getAttribute('data-target') || el.textContent, 10);
            if (!isNaN(target)) animateCount(el, 0, Math.max(0, Math.min(100, target)), 1200);
          }
          scoreObserver.unobserve(el);
        }
      });
    }, { threshold: 0.2 });

    countUpElements.forEach(el => scoreObserver.observe(el));
  }

  // Scoped landing circular meters
  const landingMeters = document.querySelectorAll('.meter-progress-circle.gauge-circle-progress');
  if (landingMeters.length > 0) {
    landingMeters.forEach(el => {
      let score = parseInt(el.getAttribute('data-score') || '80', 10);
      if (isNaN(score)) score = 80;
      score = Math.max(0, Math.min(100, score));
      const radius = parseFloat(el.getAttribute('r') || '42');
      const circumference = 2 * Math.PI * radius;
      const offset = circumference - (score / 100) * circumference;
      el.style.strokeDasharray = `${circumference}`;
      el.style.strokeDashoffset = `${offset}`;
    });
  }

  function animateCount(element, start, end, duration) {
    let startTimestamp = null;
    function step(timestamp) {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      element.textContent = Math.floor(progress * (end - start) + start);
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        element.textContent = end;
      }
    }
    window.requestAnimationFrame(step);
  }

  /* ========================================================
     6. NAVIGATION TOGGLES & ALERT DISMISSALS
     ======================================================== */
  const publicToggle = document.getElementById('public-mobile-toggle');
  const publicNavLinks = document.getElementById('public-nav-links');
  if (publicToggle && publicNavLinks) {
    publicToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      publicNavLinks.classList.toggle('open');
    });
  }

  const sidebarToggle = document.getElementById('sidebar-toggle-btn');
  const appSidebar = document.getElementById('app-sidebar');
  if (sidebarToggle && appSidebar) {
    sidebarToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      appSidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!appSidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        appSidebar.classList.remove('open');
      }
    });
  }

  const alertCloseBtns = document.querySelectorAll('.alert-close');
  alertCloseBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const alert = e.target.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });
});

/**
 * Gets the CSRF token from the meta tag
 */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

/**
 * Displays a toast notification in the UI
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.bottom = '24px';
    container.style.right = '24px';
    container.style.zIndex = '99999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '8px';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `alert alert-${type}`;
  toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.6)';
  toast.style.margin = '0';
  toast.innerHTML = `
    <span>${message}</span>
    <button type="button" class="alert-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}
