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
(function () {
    function initOpenSubtitlesModal() {
        // Wait until Bootstrap's JS is actually available
        if (!window.bootstrap || !bootstrap.Modal) {
            setTimeout(initOpenSubtitlesModal, 100);
            return;
        }

        // Try to find the OpenSubtitles modal by id containing "opensubtitles"
        var osModalEl = document.querySelector('.modal[id*="opensubtitles"]');
        if (!osModalEl || !osModalEl.id) {
            return;
        }

        var modalId = '#' + osModalEl.id;

        // Find any trigger elements that target this modal
        var triggers = Array.prototype.slice.call(
            document.querySelectorAll(
                '[data-bs-target="' + modalId + '"], ' +
                '[href="' + modalId + '"], ' +
                '[data-target="' + modalId + '"]'
            )
        );

        if (!triggers.length) {
            return;
        }

        // Remove Bootstrap's automatic data-API attributes to avoid double control
        triggers.forEach(function (el) {
            el.removeAttribute('data-bs-toggle');
            el.removeAttribute('data-bs-target');
            el.removeAttribute('data-target');
        });

        // Create or reuse a single Bootstrap modal instance
        var osModal = bootstrap.Modal.getOrCreateInstance(osModalEl, {
            backdrop: true,
            keyboard: true,
            focus: true
        });

        // Attach our own click handlers to open the modal
        triggers.forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                osModal.show();
            });
        });
    }

    document.addEventListener('DOMContentLoaded', initOpenSubtitlesModal);
})();
