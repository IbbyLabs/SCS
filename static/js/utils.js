// Common utility functions

/**
 * Show a Bootstrap toast notification
 * @param {string} message - The message to display
 * @param {string} category - Bootstrap color category (success, danger, info, warning)
 */
function showToast(message, category = 'success') {
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${category} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
// Manual control for OpenSubtitles modal to prevent Bootstrap double-binding

document.addEventListener('DOMContentLoaded', function () {
    if (!window.bootstrap) {
        console.warn('Bootstrap JS not found; modal fix not applied.');
        return;
    }

    var osModalEl = document.getElementById('opensubtitlesModal');
    if (!osModalEl) {
        return;
    }

    var osTrigger = document.querySelector('[data-bs-target="#opensubtitlesModal"]');

    if (osTrigger) {
        osTrigger.removeAttribute('data-bs-toggle');
        osTrigger.removeAttribute('data-bs-target');
    }

    var osModal = bootstrap.Modal.getOrCreateInstance(osModalEl, {
        backdrop: true,
        keyboard: true,
        focus: true
    });

    if (osTrigger) {
        osTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            osModal.show();
        });
    }
});
