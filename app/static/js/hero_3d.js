/**
 * SkyGuard AI - Interactive 3D Hero Visualization
 * Procedural 3D floating resume, animated AI laser scan beam, floating metric pills,
 * and mouse-responsive isometric parallax.
 */

(function () {
  document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('hero-3d-visual');
    if (!container) return;

    // Check for prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // If Three.js is not loaded, gracefully fallback
    if (typeof THREE === 'undefined') {
      console.warn('Three.js not loaded, using CSS fallback for 3D visual.');
      return;
    }

    let scene, camera, renderer, documentGroup, scanLine, particles;
    let width = container.clientWidth || 520;
    let height = container.clientHeight || 460;
    let mouseX = 0, mouseY = 0;
    let targetRotationX = 0.12, targetRotationY = -0.22;
    let isVisible = true;

    // 1. Initialize Scene & Camera
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8.5);

    // 2. Initialize WebGL Renderer
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance'
      });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setClearColor(0x000000, 0);
      container.appendChild(renderer.domElement);
    } catch (e) {
      console.warn('WebGL initialization failed:', e);
      return;
    }

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambientLight);

    const cyanPointLight = new THREE.PointLight(0x00f0ff, 2.4, 20);
    cyanPointLight.position.set(4, 5, 5);
    scene.add(cyanPointLight);

    const bluePointLight = new THREE.PointLight(0x3b82f6, 1.8, 20);
    bluePointLight.position.set(-4, -4, 4);
    scene.add(bluePointLight);

    const purpleBackLight = new THREE.PointLight(0x8b5cf6, 1.2, 15);
    purpleBackLight.position.set(0, 0, -4);
    scene.add(purpleBackLight);

    // 4. Create Document Group (Hierarchy)
    documentGroup = new THREE.Group();
    scene.add(documentGroup);

    // 5. Generate Procedural High-Res Canvas Texture for Resume
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 1440;
    const ctx = canvas.getContext('2d');

    // Document Card Background
    const bgGrad = ctx.createLinearGradient(0, 0, 1024, 1440);
    bgGrad.addColorStop(0, '#0f172a');
    bgGrad.addColorStop(1, '#090d16');
    ctx.fillStyle = bgGrad;
    ctx.beginPath();
    ctx.roundRect(0, 0, 1024, 1440, 36);
    ctx.fill();

    // Subtle border
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
    ctx.lineWidth = 6;
    ctx.stroke();

    // Header Area: Avatar + Name + Title
    ctx.fillStyle = '#00f0ff';
    ctx.beginPath();
    ctx.arc(100, 120, 42, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px Inter, sans-serif';
    ctx.fillText('ALEX MORGAN', 170, 110);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 24px Inter, sans-serif';
    ctx.fillText('Senior Python Developer • San Francisco, CA', 170, 145);

    // Divider
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(60, 200);
    ctx.lineTo(964, 200);
    ctx.stroke();

    // ATS Score Card Header Inside Texture
    ctx.fillStyle = 'rgba(16, 185, 129, 0.15)';
    ctx.beginPath();
    ctx.roundRect(60, 230, 904, 100, 16);
    ctx.fill();
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)';
    ctx.stroke();

    ctx.fillStyle = '#34d399';
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillText('✓ ATS COMPATIBILITY AUDIT: 86/100 (HIGH PARSABILITY)', 95, 290);

    // Section 1: Technical Skills Bar
    ctx.fillStyle = '#06b6d4';
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillText('CORE TECHNICAL COMPETENCIES', 60, 390);

    // Simulated Skill Badges
    const skills = ['Python', 'Flask', 'PostgreSQL', 'Docker', 'RESTful APIs', 'Git', 'Redis', 'AWS'];
    let skillX = 60, skillY = 425;
    skills.forEach(skill => {
      ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.5)';
      ctx.lineWidth = 2;
      const textWidth = ctx.measureText(skill).width + 36;
      ctx.beginPath();
      ctx.roundRect(skillX, skillY, textWidth, 48, 12);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#f8fafc';
      ctx.font = '600 20px Inter, sans-serif';
      ctx.fillText(skill, skillX + 18, skillY + 31);
      skillX += textWidth + 16;
    });

    // Section 2: Experience Lines
    ctx.fillStyle = '#6366f1';
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillText('PROFESSIONAL EXPERIENCE', 60, 550);

    // Simulated Experience Bullets
    const bulletLines = [
      '• Engineered scalable microservices with Python, handling 1.5M+ requests/day',
      '• Architected asynchronous message pipelines with Redis & Celery workers',
      '• Reduced database query response times by 42% through query indexing',
      '• Implemented OAuth2 and JWT token authentication protocols'
    ];

    ctx.fillStyle = '#cbd5e1';
    ctx.font = '400 22px Inter, sans-serif';
    let lineY = 600;
    bulletLines.forEach(line => {
      ctx.fillText(line, 60, lineY);
      lineY += 50;
    });

    // Section 3: Projects
    ctx.fillStyle = '#06b6d4';
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillText('KEY PROJECTS & CAPSTONES', 60, 860);

    const projectLines = [
      '• SkyGuard Real-Time Analyzer: Automated ATS parser and scoring engine',
      '• Distributed Task Scheduler: Resilient background queuing architecture',
      '• Cloud Native Deployment: Dockerized container cluster deployed on AWS'
    ];

    ctx.fillStyle = '#94a3b8';
    ctx.font = '400 22px Inter, sans-serif';
    lineY = 910;
    projectLines.forEach(line => {
      ctx.fillText(line, 60, lineY);
      lineY += 50;
    });

    // Section 4: Education
    ctx.fillStyle = '#8b5cf6';
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillText('EDUCATION & CREDENTIALS', 60, 1120);

    ctx.fillStyle = '#e2e8f0';
    ctx.font = '600 22px Inter, sans-serif';
    ctx.fillText('B.S. in Computer Science • University Engineering Dept', 60, 1170);
    ctx.fillStyle = '#64748b';
    ctx.font = '400 20px Inter, sans-serif';
    ctx.fillText('Graduated with Honors • GPA: 3.8 / 4.0', 60, 1205);

    // Create 3D Texture from Canvas
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;

    // 6. Build 3D Document Mesh with Thickness
    const docWidth = 3.3;
    const docHeight = 4.6;
    const docGeometry = new THREE.PlaneGeometry(docWidth, docHeight, 32, 32);

    const docMaterial = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.25,
      metalness: 0.15,
      transparent: true,
      opacity: 0.96,
      side: THREE.DoubleSide
    });

    const docMesh = new THREE.Mesh(docGeometry, docMaterial);
    documentGroup.add(docMesh);

    // Back glowing plate (Subtle Glass Layer)
    const backGeometry = new THREE.PlaneGeometry(docWidth + 0.1, docHeight + 0.1);
    const backMaterial = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      transparent: true,
      opacity: 0.08,
      side: THREE.BackSide
    });
    const backMesh = new THREE.Mesh(backGeometry, backMaterial);
    backMesh.position.z = -0.05;
    documentGroup.add(backMesh);

    // 7. AI Scanning Laser Line (Sweeping Beam)
    const scanGeometry = new THREE.PlaneGeometry(docWidth + 0.3, 0.08);
    const scanMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });
    scanLine = new THREE.Mesh(scanGeometry, scanMaterial);
    scanLine.position.z = 0.04;
    documentGroup.add(scanLine);

    // Secondary scan glow halo
    const glowGeometry = new THREE.PlaneGeometry(docWidth + 0.3, 0.45);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      transparent: true,
      opacity: 0.25,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });
    const scanGlow = new THREE.Mesh(glowGeometry, glowMaterial);
    scanGlow.position.z = 0.03;
    scanLine.add(scanGlow);

    // 8. Ambient 3D Particle Cloud
    const particleCount = 75;
    const particleGeometry = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      particlePositions[i] = (Math.random() - 0.5) * 12;
      particlePositions[i + 1] = (Math.random() - 0.5) * 10;
      particlePositions[i + 2] = (Math.random() - 0.5) * 8 - 1;
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

    const particleMaterial = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.045,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // Initial Isometric Orientation
    documentGroup.rotation.x = targetRotationX;
    documentGroup.rotation.y = targetRotationY;
    documentGroup.position.set(0.1, 0, 0);

    // 9. Interactive Mouse Parallax Listener
    const heroSection = container.closest('section') || window;
    heroSection.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - (rect.left + rect.width / 2)) / (rect.width / 2);
      const y = (e.clientY - (rect.top + rect.height / 2)) / (rect.height / 2);

      mouseX = Math.max(-1, Math.min(1, x));
      mouseY = Math.max(-1, Math.min(1, y));

      targetRotationY = -0.22 + mouseX * 0.18;
      targetRotationX = 0.12 - mouseY * 0.15;
    }, { passive: true });

    // 10. Visibility Observer for Rendering Optimization
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          isVisible = entry.isIntersecting;
        });
      }, { threshold: 0.1 });
      observer.observe(container);
    }

    // 11. Responsive Resize Handler
    function handleResize() {
      if (!container) return;
      width = container.clientWidth || 520;
      height = container.clientHeight || 460;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    }
    window.addEventListener('resize', handleResize);

    // 12. Main Animation Loop
    let clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      if (!isVisible) return;

      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      if (!prefersReducedMotion) {
        // Floating sinusoidal bobbing
        documentGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.12;

        // Smooth rotation lerping towards mouse target
        documentGroup.rotation.x += (targetRotationX - documentGroup.rotation.x) * 0.06;
        documentGroup.rotation.y += (targetRotationY - documentGroup.rotation.y) * 0.06;

        // Scan Line Sweep up and down (from +2.1 to -2.1)
        const scanY = Math.sin(elapsedTime * 1.6) * (docHeight / 2 - 0.2);
        scanLine.position.y = scanY;

        // Subtle particle drift
        if (particles) {
          particles.rotation.y = elapsedTime * 0.02;
          particles.rotation.x = Math.sin(elapsedTime * 0.03) * 0.05;
        }
      }

      renderer.render(scene, camera);
    }

    animate();
  });
})();
