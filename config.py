import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/svems_photography'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    IMAGE_SIZES = {
        'thumbnail': (300, 300),
        'medium': (800, 800),
        'large': (1200, 1200)
    }
    
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@svems.com'