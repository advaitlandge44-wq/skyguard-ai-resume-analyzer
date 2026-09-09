/**
 * Resume Upload & Processing Client Script
 * Connected to SkyGuard API backend (Render)
 */

document.addEventListener('DOMContentLoaded', async () => {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('resume_file');
  const filePreview = document.getElementById('file-preview');
  const fileNameDisplay = document.getElementById('file-name');
  const fileSizeDisplay = document.getElementById('file-size');
  const removeFileBtn = document.getElementById('remove-file-btn');
  const roleSelect = document.getElementById('target_role_select');
  const customRoleGroup = document.getElementById('custom-role-group');
  const customRoleInput = document.getElementById('custom_role');
  const jobDescriptionInput = document.getElementById('job_description');
  const uploadForm = document.getElementById('resume-upload-form');
  const loadingOverlay = document.getElementById('analysis-loading-overlay');
  const submitBtn = document.getElementById('upload-submit-btn');

  // Load roles dynamically if needed
  if (roleSelect && roleSelect.options.length <= 2 && window.SkyGuardAPI) {
    try {
      const res = await window.SkyGuardAPI.resume.getRoles();
      if (res && res.categories) {
        roleSelect.innerHTML = '<option value="" disabled selected>-- Select a Target Job Role --</option>';
        Object.entries(res.categories).forEach(([category, roles]) => {
          const optGroup = document.createElement('optgroup');
          optGroup.label = category;
          roles.forEach(role => {
            const opt = document.createElement('option');
            opt.value = role;
            opt.textContent = role;
            optGroup.appendChild(opt);
          });
          roleSelect.appendChild(optGroup);
        });
        const customOpt = document.createElement('option');
        customOpt.value = 'custom';
        customOpt.textContent = '✨ Other (Specify Custom Role Below)...';
        roleSelect.appendChild(customOpt);
      }
    } catch (e) {
      console.log('Roles loaded from static HTML template');
    }
  }

  // Custom role toggle
  if (roleSelect && customRoleGroup) {
    roleSelect.addEventListener('change', () => {
      if (roleSelect.value === 'custom' || roleSelect.value === '') {
        customRoleGroup.style.display = 'block';
        if (customRoleInput) customRoleInput.focus();
      } else {
        customRoleGroup.style.display = 'none';
      }
    });
  }

  // Drag & Drop events
  if (dropZone && fileInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-active');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-active');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        fileInput.files = files;
        handleFileSelection(files[0]);
      }
    });

    dropZone.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files.length > 0) {
        handleFileSelection(fileInput.files[0]);
      }
    });
  }

  // Remove selected file
  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearSelectedFile();
    });
  }

  function handleFileSelection(file) {
    const validExtensions = ['pdf', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      if (window.showToast) window.showToast('Please upload a PDF (.pdf) or Plain Text (.txt) file.', 'danger');
      clearSelectedFile();
      return;
    }

    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      if (window.showToast) window.showToast('File size exceeds the 5MB limit. Please upload a smaller resume.', 'danger');
      clearSelectedFile();
      return;
    }

    if (fileNameDisplay) fileNameDisplay.textContent = file.name;
    if (fileSizeDisplay) fileSizeDisplay.textContent = formatBytes(file.size);
    if (dropZone) dropZone.style.display = 'none';
    if (filePreview) filePreview.style.display = 'flex';
  }

  function clearSelectedFile() {
    if (fileInput) fileInput.value = '';
    if (dropZone) dropZone.style.display = 'flex';
    if (filePreview) filePreview.style.display = 'none';
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Form Submission with Multi-Step Animated Loader & API integration
  if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const selectedRole = (roleSelect && roleSelect.value !== 'custom') ? roleSelect.value : (customRoleInput ? customRoleInput.value.trim() : '');
      if (!selectedRole) {
        if (window.showToast) window.showToast('Please select or specify a target job role.', 'warning');
        return;
      }

      if (!fileInput.files || fileInput.files.length === 0) {
        if (window.showToast) window.showToast('Please select a resume file to analyze.', 'warning');
        return;
      }

      // Show loading overlay
      if (loadingOverlay) loadingOverlay.style.display = 'flex';
      if (submitBtn) submitBtn.disabled = true;

      // Step checklist animation
      const stepElements = [
        document.getElementById('step-1'),
        document.getElementById('step-2'),
        document.getElementById('step-3'),
        document.getElementById('step-4')
      ];

      function activateStep(index) {
        if (index < stepElements.length && stepElements[index]) {
          const el = stepElements[index];
          el.style.color = '#ffffff';
          const icon = el.querySelector('.step-status');
          if (icon) {
            icon.textContent = '✓';
            icon.style.color = 'var(--success-text)';
            icon.style.fontWeight = '700';
          }
        }
      }

      activateStep(0);
      const timer1 = setTimeout(() => activateStep(1), 1200);
      const timer2 = setTimeout(() => activateStep(2), 2400);
      const timer3 = setTimeout(() => activateStep(3), 3600);

      // Build FormData
      const formData = new FormData();
      formData.append('resume_file', fileInput.files[0]);
      formData.append('target_role_select', roleSelect ? roleSelect.value : '');
      formData.append('custom_role', customRoleInput ? customRoleInput.value : '');
      if (jobDescriptionInput) formData.append('job_description', jobDescriptionInput.value);

      try {
        const result = await window.SkyGuardAPI.resume.upload(formData);
        if (result && result.success && result.analysis_id) {
          activateStep(1);
          activateStep(2);
          activateStep(3);
          setTimeout(() => {
            window.location.href = `results.html?id=${result.analysis_id}`;
          }, 600);
        } else {
          throw new Error((result && result.error) || 'Failed to complete resume analysis.');
        }
      } catch (err) {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        if (loadingOverlay) loadingOverlay.style.display = 'none';
        if (submitBtn) submitBtn.disabled = false;
        
        if (err.status === 401) {
          if (window.showToast) window.showToast('Please log in to analyze your resume.', 'warning');
          setTimeout(() => {
            window.location.href = 'login.html?next=upload.html';
          }, 1200);
        } else {
          if (window.showToast) window.showToast(err.message || 'An error occurred during upload. Please try again.', 'danger');
        }
      }
    });
  }
});
