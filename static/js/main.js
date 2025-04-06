// Main JavaScript for AI Interview Simulator

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
      var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
      tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }
  
    // Add event listeners for field and position inputs to validate and enable/disable start button
    const fieldInput = document.getElementById('field');
    const positionInput = document.getElementById('position');
    const startButton = document.querySelector('button[type="submit"]');
  
    if (fieldInput && positionInput && startButton) {
      const validateInputs = () => {
        if (fieldInput.value.trim() && positionInput.value.trim()) {
          startButton.disabled = false;
        } else {
          startButton.disabled = true;
        }
      };
  
      fieldInput.addEventListener('input', validateInputs);
      positionInput.addEventListener('input', validateInputs);
      validateInputs(); // Initial check
    }
  
    // Set year in footer copyright if exists
    const yearElement = document.querySelector('.copyright-year');
    if (yearElement) {
      yearElement.textContent = new Date().getFullYear();
    }
  });
  
  /**
   * Utility function to create a modal dialog
   * @param {string} title - The modal title
   * @param {string} body - The modal body content
   * @param {string} primaryButtonText - Text for the primary button (optional)
   * @param {Function} primaryButtonCallback - Callback for primary button click (optional)
   */
  function showModal(title, body, primaryButtonText = null, primaryButtonCallback = null) {
    // Create modal elements
    const modalWrapper = document.createElement('div');
    modalWrapper.className = 'modal fade';
    modalWrapper.id = 'dynamicModal';
    modalWrapper.setAttribute('tabindex', '-1');
    modalWrapper.setAttribute('aria-hidden', 'true');
    
    modalWrapper.innerHTML = `
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">${title}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ${body}
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            ${primaryButtonText ? `<button type="button" class="btn btn-primary" id="modalPrimaryBtn">${primaryButtonText}</button>` : ''}
          </div>
        </div>
      </div>
    `;
    
    // Add to body
    document.body.appendChild(modalWrapper);
    
    // Create modal instance
    const modalElement = document.getElementById('dynamicModal');
    const modal = new bootstrap.Modal(modalElement);
    
    // Add event listener for primary button if provided
    if (primaryButtonText && primaryButtonCallback) {
      document.getElementById('modalPrimaryBtn').addEventListener('click', primaryButtonCallback);
    }
    
    // Show the modal
    modal.show();
    
    // Add event listener to remove from DOM when hidden
    modalElement.addEventListener('hidden.bs.modal', function () {
      document.body.removeChild(modalWrapper);
    });
    
    return modal;
  }
  
  /**
   * Utility function to show error messages
   * @param {string} message - The error message
   */
  function showError(message) {
    showModal('Error', `<div class="alert alert-danger">${message}</div>`);
  }