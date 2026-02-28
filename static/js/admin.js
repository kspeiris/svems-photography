document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;

    // Mobile sidebar toggle for admin layout
    const sidebar = document.getElementById('adminSidebar');
    const sidebarToggle = document.getElementById('adminSidebarToggle');
    const sidebarBackdrop = document.getElementById('adminSidebarBackdrop');

    const closeSidebar = () => {
        body.classList.remove('admin-sidebar-open');
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-expanded', 'false');
        }
    };

    const openSidebar = () => {
        body.classList.add('admin-sidebar-open');
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-expanded', 'true');
        }
    };

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            if (body.classList.contains('admin-sidebar-open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeSidebar);
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeSidebar();
        }
    });

    // Upload area behavior
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('imageFile');
    const preview = document.getElementById('uploadPreview');

    function handleFileSelect(file) {
        if (!preview) {
            return;
        }

        if (!file || !file.type.startsWith('image/')) {
            preview.innerHTML = '<p class="error-text">Please upload a valid image file.</p>';
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            preview.innerHTML = '<p class="error-text">File is too large. Max 16MB.</p>';
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            preview.innerHTML = `<img src="${event.target.result}" alt="Uploaded image preview" class="preview-img">`;
        };
        reader.readAsDataURL(file);
    }

    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (event) => {
            event.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (event) => {
            event.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener('change', (event) => {
            if (event.target.files.length > 0) {
                handleFileSelect(event.target.files[0]);
            }
        });
    }

    // Confirm actions with explicit data-confirm text
    document.querySelectorAll('[data-confirm]').forEach((element) => {
        element.addEventListener('click', (event) => {
            const message = element.getAttribute('data-confirm') || 'Are you sure?';
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Bulk selection and selected-count handling
    document.querySelectorAll('[data-select-all]').forEach((masterCheckbox) => {
        const group = masterCheckbox.getAttribute('data-select-all');
        const items = document.querySelectorAll(`input[type="checkbox"][data-group="${group}"]`);
        const countLabel = document.querySelector(`[data-selected-count="${group}"]`);

        const updateState = () => {
            const checkedCount = Array.from(items).filter((checkbox) => checkbox.checked).length;
            masterCheckbox.checked = checkedCount > 0 && checkedCount === items.length;
            if (countLabel) {
                countLabel.textContent = `${checkedCount} selected`;
            }
        };

        masterCheckbox.addEventListener('change', () => {
            items.forEach((item) => {
                item.checked = masterCheckbox.checked;
            });
            updateState();
        });

        items.forEach((item) => {
            item.addEventListener('change', updateState);
        });

        updateState();
    });

    // Prevent invalid bulk submissions
    document.querySelectorAll('form').forEach((form) => {
        const actionSelect = form.querySelector('select[name="action"]');
        if (!actionSelect) {
            return;
        }

        form.addEventListener('submit', function (event) {
            const selectedAction = (actionSelect.value || '').trim();
            const insideItems = form.querySelectorAll('input[type="checkbox"][name$="_ids"]:checked');
            const linkedItems = form.id
                ? document.querySelectorAll(`input[type="checkbox"][name$="_ids"][form="${form.id}"]:checked`)
                : [];
            const targetCount = insideItems.length + linkedItems.length;

            if (!selectedAction) {
                event.preventDefault();
                alert('Choose a bulk action first.');
                return;
            }

            if (targetCount === 0) {
                event.preventDefault();
                alert('Select at least one item first.');
                return;
            }

            if (selectedAction === 'delete' && !window.confirm('Delete the selected items?')) {
                event.preventDefault();
            }
        });
    });

    // Message full-view modal
    const messageModal = document.getElementById('messageViewModal');
    if (messageModal) {
        const modalName = document.getElementById('modalMessageName');
        const modalEmail = document.getElementById('modalMessageEmail');
        const modalDate = document.getElementById('modalMessageDate');
        const modalBody = document.getElementById('modalMessageBody');

        const openMessageModal = (button) => {
            modalName.textContent = button.getAttribute('data-name') || '-';
            modalEmail.textContent = button.getAttribute('data-email') || '-';
            modalDate.textContent = button.getAttribute('data-submitted') || '-';
            modalBody.textContent = button.getAttribute('data-message') || '';
            messageModal.classList.remove('hidden');
            messageModal.setAttribute('aria-hidden', 'false');
            body.classList.add('admin-modal-open');
        };

        const closeMessageModal = () => {
            messageModal.classList.add('hidden');
            messageModal.setAttribute('aria-hidden', 'true');
            body.classList.remove('admin-modal-open');
        };

        document.querySelectorAll('[data-message-view]').forEach((button) => {
            button.addEventListener('click', () => openMessageModal(button));
        });

        messageModal.querySelectorAll('[data-modal-close]').forEach((element) => {
            element.addEventListener('click', closeMessageModal);
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && messageModal.getAttribute('aria-hidden') === 'false') {
                closeMessageModal();
            }
        });
    }
});
