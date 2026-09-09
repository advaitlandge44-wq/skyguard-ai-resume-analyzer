/**
 * SkyGuard AI - Cinematic 3D AI Resume & Career Engine
 * 
 * Features:
 * - High-Fidelity Procedural 3D Resume Mesh with multi-pass canvas texture
 * - Dynamic AI Laser Scan with localized illumination
 * - Orbiting Holographic Scanner Rings and Data Rings
 * - Floating 3D Data Nodes and Quantum Particle Cloud
 * - Fluid Isometric Mouse Parallax & Scroll-Linked Depth
 * - Performance optimized: Framerate throttling offscreen via IntersectionObserver,
 *   pixel ratio clamped, low poly geometry, and reduced-motion support.
 */

(function () {
  document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('hero-3d-visual');
    if (!container) return;

    // Check for prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // If Three.js is not loaded, gracefully fallback
    if (typeof THREE === 'undefined') {
      console.warn('Three.js not loaded, using fallback visual.');
      return;
    }

    let scene, camera, renderer, masterGroup, documentGroup, ringsGroup, dataNodesGroup, scanBeam, scanLight, particles;
    let width = container.clientWidth || 560;
    let height = container.clientHeight || 500;
    let mouseX = 0, mouseY = 0;
    let targetRotationX = 0.1, targetRotationY = -0.2;
    let scrollYOffset = 0;
    let isVisible = true;
    let clock = new THREE.Clock();

    // 1. Initialize Scene & Perspective Camera
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(0, 0, 9.2);

    // 2. Initialize WebGL Renderer
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance'
      });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setClearColor(0x000000, 0);
      renderer.outputEncoding = THREE.sRGBEncoding || 3001;
      container.appendChild(renderer.domElement);
    } catch (e) {
      console.warn('WebGL initialization failed:', e);
      return;
    }

    // 3. Cinematic Lighting System (Luxury Dark Studio)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const cyanKeyLight = new THREE.PointLight(0x00f0ff, 2.8, 25);
    cyanKeyLight.position.set(5, 6, 6);
    scene.add(cyanKeyLight);

    const blueFillLight = new THREE.PointLight(0x3b82f6, 2.2, 25);
    blueFillLight.position.set(-5, -4, 5);
    scene.add(blueFillLight);

    const purpleRimLight = new THREE.PointLight(0x8b5cf6, 1.8, 20);
    purpleRimLight.position.set(0, -3, -4);
    scene.add(purpleRimLight);

    // 4. Master Hierarchical Groups
    masterGroup = new THREE.Group();
    scene.add(masterGroup);

    documentGroup = new THREE.Group();
    masterGroup.add(documentGroup);

    ringsGroup = new THREE.Group();
    masterGroup.add(ringsGroup);

    dataNodesGroup = new THREE.Group();
    masterGroup.add(dataNodesGroup);

    // 5. Generate Procedural High-Res Canvas Texture for Resume
    const canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 1680;
    const ctx = canvas.getContext('2d');

    // Document Card Background with Glass Obsidian Gradient
    const bgGrad = ctx.createLinearGradient(0, 0, 1200, 1680);
    bgGrad.addColorStop(0, '#0c1220');
    bgGrad.addColorStop(0.5, '#070a12');
    bgGrad.addColorStop(1, '#05070d');
    ctx.fillStyle = bgGrad;
    ctx.beginPath();
    ctx.roundRect(0, 0, 1200, 1680, 40);
    ctx.fill();

    // Precision Cyber Accent Border
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.45)';
    ctx.lineWidth = 6;
    ctx.stroke();

    // Top Subtle Gradient Highlight Line
    const topGrad = ctx.createLinearGradient(0, 0, 1200, 0);
    topGrad.addColorStop(0, 'rgba(0, 240, 255, 0)');
    topGrad.addColorStop(0.5, 'rgba(0, 240, 255, 0.8)');
    topGrad.addColorStop(1, 'rgba(99, 102, 241, 0)');
    ctx.strokeStyle = topGrad;
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.moveTo(80, 6);
    ctx.lineTo(1120, 6);
    ctx.stroke();

    // SECTION A: Profile Header Area
    // Profile Glow Ring Avatar
    ctx.save();
    ctx.fillStyle = '#00f0ff';
    ctx.beginPath();
    ctx.arc(120, 130, 48, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#070a12';
    ctx.font = 'bold 36px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('AM', 120, 142);
    ctx.restore();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 42px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('ALEX MORGAN', 190, 122);

    ctx.fillStyle = '#38bdf8';
    ctx.font = '600 24px Inter, sans-serif';
    ctx.fillText('Senior Python & AI Systems Engineer', 190, 158);

    ctx.fillStyle = '#64748b';
    ctx.font = '500 20px Inter, sans-serif';
    ctx.fillText('alex.morgan@domain.com • San Francisco, CA • github.com/alexm', 190, 190);

    // Divider
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(70, 230);
    ctx.lineTo(1130, 230);
    ctx.stroke();

    // Live ATS Audit Score Banner inside Resume
    ctx.fillStyle = 'rgba(16, 185, 129, 0.12)';
    ctx.beginPath();
    ctx.roundRect(70, 260, 1060, 100, 18);
    ctx.fill();
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.45)';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#34d399';
    ctx.font = 'bold 26px Inter, sans-serif';
    ctx.fillText('⚡ ATS PARSING OPTIMIZED: 86/100 (HIGH RECRUITER VISIBILITY)', 110, 322);

    // SECTION B: Skills Section
    ctx.fillStyle = '#00f0ff';
    ctx.font = 'bold 28px Inter, sans-serif';
    ctx.fillText('CORE TECHNICAL SKILLS', 70, 430);

    const skillsList = ['Python', 'SQL', 'Flask', 'Docker', 'AWS', 'REST APIs', 'PostgreSQL', 'Redis', 'OpenAI API'];
    let skX = 70, skY = 465;
    skillsList.forEach(skill => {
      ctx.font = '600 20px Inter, sans-serif';
      const textW = ctx.measureText(skill).width;
      const pillW = textW + 36;
      if (skX + pillW > 1130) {
        skX = 70;
        skY += 56;
      }
      ctx.fillStyle = 'rgba(0, 240, 255, 0.12)';
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(skX, skY, pillW, 46, 12);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#f8fafc';
      ctx.fillText(skill, skX + 18, skY + 29);
      skX += pillW + 14;
    });

    // SECTION C: Experience Section
    ctx.fillStyle = '#6366f1';
    ctx.font = 'bold 28px Inter, sans-serif';
    ctx.fillText('PROFESSIONAL EXPERIENCE', 70, 650);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 24px Inter, sans-serif';
    ctx.fillText('Senior Backend Developer — CloudScale Systems', 70, 695);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 20px Inter, sans-serif';
    ctx.fillText('2022 – Present • High-Throughput Distributed Services', 70, 725);

    const expBullets = [
      '• Architected asynchronous Python & Flask microservices handling 2.5M+ daily requests with 99.98% SLA.',
      '• Engineered automated query caching pipeline with Redis & Celery, reducing latency by 42%.',
      '• Implemented OAuth2 & JWT session management with strict role-based access control (RBAC).',
      '• Led CI/CD containerization pipeline migrating monolithic workflows into Docker on AWS ECS.'
    ];

    ctx.fillStyle = '#cbd5e1';
    ctx.font = '400 21px Inter, sans-serif';
    let lineY = 770;
    expBullets.forEach(b => {
      ctx.fillText(b, 70, lineY);
      lineY += 44;
    });

    // SECTION D: Projects Section
    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 28px Inter, sans-serif';
    ctx.fillText('KEY PROJECTS & AI SYSTEMS', 70, 1020);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 24px Inter, sans-serif';
    ctx.fillText('SkyGuard AI Real-Time ATS Diagnostic Engine', 70, 1065);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '400 21px Inter, sans-serif';
    ctx.fillText('• Developed real-time resume parsing engine using PyMuPDF and LLM scoring models.', 70, 1105);
    ctx.fillText('• Built career roadmap generator aligning missing skill competencies with industry benchmarks.', 70, 1145);

    // SECTION E: Education Section
    ctx.fillStyle = '#8b5cf6';
    ctx.font = 'bold 28px Inter, sans-serif';
    ctx.fillText('EDUCATION & CREDENTIALS', 70, 1260);

    ctx.fillStyle = '#f8fafc';
    ctx.font = '600 24px Inter, sans-serif';
    ctx.fillText('B.S. in Computer Science — State University Institute of Tech', 70, 1305);
    ctx.fillStyle = '#64748b';
    ctx.font = '500 20px Inter, sans-serif';
    ctx.fillText('Dean’s Honors List • Focus: Distributed Systems & Machine Intelligence', 70, 1340);

    // Section F: Scanning Overlay Grid watermark
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.04)';
    ctx.lineWidth = 1;
    for (let x = 70; x <= 1130; x += 60) {
      ctx.beginPath();
      ctx.moveTo(x, 260);
      ctx.lineTo(x, 1400);
      ctx.stroke();
    }

    // Create CanvasTexture
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;

    // 6. Build 3D Document Mesh with Multi-Layered Glass Aesthetics
    const docWidth = 3.6;
    const docHeight = 5.0;
    const docGeometry = new THREE.PlaneGeometry(docWidth, docHeight, 32, 32);

    const docMaterial = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.2,
      metalness: 0.25,
      transparent: true,
      opacity: 0.98,
      side: THREE.DoubleSide
    });

    const docMesh = new THREE.Mesh(docGeometry, docMaterial);
    documentGroup.add(docMesh);

    // Back Plate (Deep Glass Chamber)
    const backGeometry = new THREE.PlaneGeometry(docWidth + 0.15, docHeight + 0.15);
    const backMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.08,
      side: THREE.BackSide
    });
    const backMesh = new THREE.Mesh(backGeometry, backMaterial);
    backMesh.position.z = -0.06;
    documentGroup.add(backMesh);

    // Ambient Glass Border Glow Frame
    const frameGeometry = new THREE.PlaneGeometry(docWidth + 0.04, docHeight + 0.04);
    const frameMaterial = new THREE.MeshBasicMaterial({
      color: 0x3b82f6,
      transparent: true,
      opacity: 0.2,
      wireframe: true
    });
    const frameMesh = new THREE.Mesh(frameGeometry, frameMaterial);
    frameMesh.position.z = -0.02;
    documentGroup.add(frameMesh);

    // 7. Dynamic AI Laser Scanning Beam
    const scanGeometry = new THREE.PlaneGeometry(docWidth + 0.5, 0.09);
    const scanMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });
    scanBeam = new THREE.Mesh(scanGeometry, scanMaterial);
    scanBeam.position.z = 0.05;
    documentGroup.add(scanBeam);

    // Laser Halo Glow
    const haloGeometry = new THREE.PlaneGeometry(docWidth + 0.5, 0.6);
    const haloMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.28,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });
    const scanHalo = new THREE.Mesh(haloGeometry, haloMaterial);
    scanHalo.position.z = 0.04;
    scanBeam.add(scanHalo);

    // Localized moving scan point light
    scanLight = new THREE.PointLight(0x00f0ff, 1.8, 5);
    scanLight.position.set(0, 0, 0.3);
    scanBeam.add(scanLight);

    // 8. Orbiting Holographic Scanner Rings (Cinematic AI Scanner)
    const ring1Geo = new THREE.RingGeometry(3.3, 3.34, 64);
    const ring1Mat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.45,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending
    });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 3;
    ringsGroup.add(ring1);

    const ring2Geo = new THREE.RingGeometry(3.8, 3.83, 64);
    const ring2Mat = new THREE.MeshBasicMaterial({
      color: 0x6366f1,
      transparent: true,
      opacity: 0.35,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.y = Math.PI / 4;
    ring2.rotation.x = -Math.PI / 6;
    ringsGroup.add(ring2);

    const ring3Geo = new THREE.RingGeometry(4.2, 4.22, 64);
    const ring3Mat = new THREE.MeshBasicMaterial({
      color: 0x8b5cf6,
      transparent: true,
      opacity: 0.25,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending
    });
    const ring3 = new THREE.Mesh(ring3Geo, ring3Mat);
    ring3.rotation.z = Math.PI / 5;
    ringsGroup.add(ring3);

    // 9. Floating 3D Data Nodes (Holographic Nodes around Resume)
    const nodeGeometry = new THREE.SphereGeometry(0.065, 16, 16);
    const nodePositions = [
      { x: -2.4, y: 1.8, z: 0.8, color: 0x00f0ff },
      { x: 2.5, y: 1.5, z: 0.6, color: 0x10b981 },
      { x: -2.6, y: -1.2, z: 1.0, color: 0x3b82f6 },
      { x: 2.4, y: -1.6, z: 0.7, color: 0x8b5cf6 },
      { x: 0, y: 2.8, z: -0.5, color: 0x00f0ff },
      { x: -1.8, y: -2.6, z: -0.4, color: 0xf59e0b }
    ];

    const dataNodes = [];
    nodePositions.forEach(pos => {
      const nodeMat = new THREE.MeshBasicMaterial({
        color: pos.color,
        transparent: true,
        opacity: 0.85
      });
      const nodeMesh = new THREE.Mesh(nodeGeometry, nodeMat);
      nodeMesh.position.set(pos.x, pos.y, pos.z);
      nodeMesh.userData = { initialY: pos.y, speed: 0.8 + Math.random() * 0.8, offset: Math.random() * Math.PI };
      dataNodesGroup.add(nodeMesh);
      dataNodes.push(nodeMesh);
    });

    // 10. Ambient 3D Particle Cloud
    const particleCount = 100;
    const particleGeometry = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      particlePositions[i] = (Math.random() - 0.5) * 14;
      particlePositions[i + 1] = (Math.random() - 0.5) * 12;
      particlePositions[i + 2] = (Math.random() - 0.5) * 9 - 1;
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

    const particleMaterial = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.05,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // Initial Isometric Orientation
    documentGroup.rotation.x = targetRotationX;
    documentGroup.rotation.y = targetRotationY;
    documentGroup.position.set(0.1, 0, 0);

    // 11. Interactive Mouse Parallax
    const heroSection = container.closest('section') || window;
    heroSection.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - (rect.left + rect.width / 2)) / (rect.width / 2);
      const y = (e.clientY - (rect.top + rect.height / 2)) / (rect.height / 2);

      mouseX = Math.max(-1, Math.min(1, x));
      mouseY = Math.max(-1, Math.min(1, y));

      targetRotationY = -0.2 + mouseX * 0.22;
      targetRotationX = 0.1 - mouseY * 0.18;
    }, { passive: true });

    // 12. Scroll-Linked Transformation
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY || window.pageYOffset;
      scrollYOffset = Math.min(scrollY / window.innerHeight, 1.5);
    }, { passive: true });

    // 13. Visibility Observer for High-Efficiency Rendering
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          isVisible = entry.isIntersecting;
        });
      }, { threshold: 0.05 });
      observer.observe(container);
    }

    // 14. Responsive Resize Handler
    function handleResize() {
      if (!container) return;
      width = container.clientWidth || 560;
      height = container.clientHeight || 500;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    }
    window.addEventListener('resize', handleResize);

    // 15. Main Animation Loop
    function animate() {
      requestAnimationFrame(animate);

      if (!isVisible) return;

      const elapsedTime = clock.getElapsedTime();

      if (!prefersReducedMotion) {
        // Floating Sinusoidal Bobbing
        documentGroup.position.y = Math.sin(elapsedTime * 1.4) * 0.14 - (scrollYOffset * 0.4);

        // Smooth Lerp Rotation
        documentGroup.rotation.x += (targetRotationX - documentGroup.rotation.x) * 0.05;
        documentGroup.rotation.y += (targetRotationY - documentGroup.rotation.y) * 0.05;

        // Laser Scan Sweep (top to bottom of resume)
        const scanY = Math.sin(elapsedTime * 1.5) * (docHeight / 2 - 0.25);
        scanBeam.position.y = scanY;

        // Holographic Rings Rotation
        if (ringsGroup) {
          ring1.rotation.z = elapsedTime * 0.25;
          ring2.rotation.y = elapsedTime * -0.2;
          ring3.rotation.x = elapsedTime * 0.15;
          ringsGroup.rotation.y = Math.sin(elapsedTime * 0.5) * 0.1;
        }

        // Floating Data Nodes Animation
        dataNodes.forEach(node => {
          node.position.y = node.userData.initialY + Math.sin(elapsedTime * node.userData.speed + node.userData.offset) * 0.15;
        });

        // Ambient Particle Field Drift
        if (particles) {
          particles.rotation.y = elapsedTime * 0.025;
          particles.rotation.x = Math.sin(elapsedTime * 0.04) * 0.06;
        }
      }

      renderer.render(scene, camera);
    }

    animate();
  });
})();
