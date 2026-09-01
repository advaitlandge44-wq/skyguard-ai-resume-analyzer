/**
 * Resume Upload & Processing Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('resume_file');
  const filePreview = document.getElementById('file-preview');
  const fileNameDisplay = document.getElementById('file-name');
  const fileSizeDisplay = document.getElementById('file-size');
  const removeFileBtn = document.getElementById('remove-file-btn');
  const roleSelect = document.getElementById('target_role_select');
  const customRoleGroup = document.getElementById('custom-role-group');
  const customRoleInput = document.getElementById('custom_role');
  const uploadForm = document.getElementById('resume-upload-form');
  const loadingOverlay = document.getElementById('analysis-loading-overlay');
  const loadingStepText = document.getElementById('loading-step-text');

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
    // Validate file type
    const validExtensions = ['pdf', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      showToast('Please upload a PDF (.pdf) or Plain Text (.txt) file.', 'danger');
      clearSelectedFile();
      return;
    }

    // Validate size (5MB max)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      showToast('File size exceeds the 5MB limit. Please upload a smaller resume.', 'danger');
      clearSelectedFile();
      return;
    }

    // Display preview
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

  // Form Submission with Animated Multi-Step Loader
  if (uploadForm && loadingOverlay) {
    uploadForm.addEventListener('submit', (e) => {
      const selectedRole = (roleSelect && roleSelect.value !== 'custom') ? roleSelect.value : (customRoleInput ? customRoleInput.value.trim() : '');
      if (!selectedRole) {
        e.preventDefault();
        showToast('Please select or specify a target job role.', 'warning');
        return;
      }

      if (!fileInput.files || fileInput.files.length === 0) {
        e.preventDefault();
        showToast('Please select a resume file to analyze.', 'warning');
        return;
      }

      // Show overlay
      loadingOverlay.style.display = 'flex';

      // Step checklist animation (Section 15)
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

      // Step 1 active immediately
      activateStep(0);

      setTimeout(() => activateStep(1), 1200);
      setTimeout(() => activateStep(2), 2400);
      setTimeout(() => activateStep(3), 3600);
    });
  }
});
