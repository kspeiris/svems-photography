document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            let isValid = true;
            const errorMessages = [];
            
            // Name validation
            if (name.length < 2) {
                isValid = false;
                errorMessages.push('Please enter a valid name (at least 2 characters)');
                highlightError('name');
            }
            
            // Email validation
            if (!isValidEmail(email)) {
                isValid = false;
                errorMessages.push('Please enter a valid email address');
                highlightError('email');
            }
            
            // Message validation
            if (message.length < 10) {
                isValid = false;
                errorMessages.push('Please enter a message with at least 10 characters');
                highlightError('message');
            }
            
            if (!isValid) {
                e.preventDefault();
                showFormErrors(errorMessages);
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.classList.remove('loading');
                    submitButton.textContent = 'Send Message';
                }
            } else if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add('loading');
                submitButton.textContent = 'Sending...';
            }
        });
        
        // Remove error highlight when user starts typing
        const inputs = contactForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('error');
                hideFormErrors();
            });
        });
    }
    
    // Improved email validation pattern
    function isValidEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    }
    
    // Highlight error input field
    function highlightError(inputId) {
        const input = document.getElementById(inputId);
        if (input) {
            input.classList.add('error');
        }
    }

    // Show multiple error messages
    function showFormErrors(messages) {
        let errorDiv = document.getElementById('formError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'formError';
            errorDiv.className = 'form-error';
            errorDiv.setAttribute('role', 'alert');
            contactForm.prepend(errorDiv);
        }
        
        errorDiv.innerHTML = messages.join('<br>'); // Display all error messages
        errorDiv.style.display = 'block';
    }

    // Hide error message
    function hideFormErrors() {
        const errorDiv = document.getElementById('formError');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }
});
