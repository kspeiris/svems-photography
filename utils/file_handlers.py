import os
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags
from flask import current_app

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, category='general'):
    """Save and process uploaded image"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        category_folder = category.lower()
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], category_folder)
        
        # Create category directory if it doesn't exist
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        
        try:
            # Open and process image
            img = Image.open(file)
            
            # Handle image orientation based on EXIF data
            img = correct_image_orientation(img)
            
            # Resize image to fit within maximum dimensions
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            
            # Save the image
            img.save(filepath, optimize=True, quality=85)
            
            return f"{category_folder}/{filename}"
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
    
    return None

def correct_image_orientation(img):
    """Correct image orientation based on EXIF data"""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = img._getexif()
        if exif is not None and orientation in exif:
            orientation_value = exif[orientation]
            
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
                
    except (AttributeError, KeyError, IndexError, Exception):
        # No EXIF data or orientation tag, or other error
        pass
    
    return img

def delete_image_file(filename):
    """Delete image file from filesystem"""
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting image file: {str(e)}")
    
    return False