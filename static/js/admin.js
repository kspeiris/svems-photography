document.addEventListener('DOMContentLoaded', function() {
    // Upload Area Handling
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('imageFile');
    const preview = document.getElementById('uploadPreview');

    if (uploadArea && fileInput) {
        // Open file input when the upload area is clicked
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag Over Effect for upload area
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover'); // Highlight upload area on drag
        });

        // Remove drag over effect when dragging leaves the upload area
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        // Handle drop event to select files for upload
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        // Handle file input change (e.g., file selection through file dialog)
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    // Function to display image preview after file selection
    function handleFileSelect(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview" class="preview-img">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `<p class="error-text">Please upload a valid image file.</p>`;
        }
    }

    // Delete Item with Confirmation
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Mark Message as Read
    const markReadButtons = document.querySelectorAll('.mark-read-btn');
    markReadButtons.forEach(button => {
        button.addEventListener('click', function() {
            const messageId = this.dataset.messageId;
            fetch(`/admin/mark-read/${messageId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.closest('.message-item').classList.remove('unread'); // Remove unread class
                        this.remove(); // Remove the "mark read" button
                        alert("Message marked as read!");
                    } else {
                        alert("Failed to mark as read. Please try again.");
                    }
                })
                .catch(error => {
                    console.error("Error marking message as read:", error);
                    alert("An error occurred. Please try again.");
                });
        });
    });

    // Accessibility Enhancements
    const imagePreview = document.querySelector('.preview-img');
    if (imagePreview) {
        // Add alt text for accessibility purposes
        imagePreview.alt = "Uploaded image preview";
    }

    // Adding focus state for interactive elements (e.g., buttons)
    const interactiveElements = document.querySelectorAll('a, button');
    interactiveElements.forEach(element => {
        element.addEventListener('focus', () => {
            element.classList.add('focused');
        });
        element.addEventListener('blur', () => {
            element.classList.remove('focused');
        });
    });

    // Smooth Scroll to Top for better UX (optional)
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) {
        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Optional: Add smooth transition to file upload area and buttons
    if (uploadArea) {
        uploadArea.classList.add('transition-all');
    }
    if (fileInput) {
        fileInput.classList.add('transition-all');
    }
    document.querySelectorAll('.delete-btn, .mark-read-btn').forEach(button => {
        button.classList.add('transition-all');
    });

    // Make sure preview area fades in smoothly
    if (preview) {
        preview.classList.add('fade-in');
    }
});
