import re

def validate_contact_form(name, email, message):
    """Validate contact form data"""
    if not name or len(name.strip()) < 2:
        return False, "Please enter a valid name (at least 2 characters)"
    
    if not is_valid_email(email):
        return False, "Please enter a valid email address"
    
    if not message or len(message.strip()) < 10:
        return False, "Please enter a message with at least 10 characters"
    
    return True, ""

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_image_upload(file):
    """Validate uploaded image file"""
    if not file:
        return False, "No file selected"
    
    if file.filename == '':
        return False, "No file selected"
    
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return False, "Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, WEBP"
    
    # Check file size (16MB max)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Seek back to start
    
    if file_size > 16 * 1024 * 1024:
        return False, "File size too large. Maximum size is 16MB"
    
    return True, ""