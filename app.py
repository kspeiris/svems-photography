from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort, session
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask.json.provider import DefaultJSONProvider
from PIL import Image
import os
import secrets
import hmac
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message_category = 'info'
ALLOWED_IMAGE_CATEGORIES = {'portraits', 'landscapes', 'events', 'weddings', 'commercial'}

class User(UserMixin):
    def __init__(self, user_data):
        if user_data:
            self.id = str(user_data['_id'])
            self.username = user_data['username']
            self.email = user_data['email']
            self.password_hash = user_data['password_hash']
        else:
            self.id = None
            self.username = None
            self.email = None
            self.password_hash = None

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    except Exception:
        return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def save_image(file, category='general'):
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        if not original_filename:
            return None

        file_ext = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        category_folder = secure_filename((category or 'general').lower()) or 'general'
        upload_path = os.path.join('static/uploads', category_folder)
        
        os.makedirs(upload_path, exist_ok=True)
        filepath = os.path.join(upload_path, unique_filename)
        
        try:
            img = Image.open(file)
            img.thumbnail((1200, 1200))
            img.save(filepath, optimize=True, quality=85)
            return f"{category_folder}/{unique_filename}"
        except Exception as exc:
            print(f"Error processing image: {exc}")
            return None
    return None

def delete_image_file(filename):
    try:
        file_path = os.path.join('static/uploads', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as exc:
        print(f"Error deleting image: {exc}")
    return False

def validate_contact_form(name, email, message):
    if not name or len(name.strip()) < 2:
        return False, "Please enter a valid name (at least 2 characters)"
    if not email or '@' not in email:
        return False, "Please enter a valid email address"
    if not message or len(message.strip()) < 10:
        return False, "Please enter a message with at least 10 characters"
    return True, ""

def generate_csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token

def validate_csrf():
    token = request.form.get('csrf_token')
    session_token = session.get('_csrf_token')
    if not token or not session_token or not hmac.compare_digest(token, session_token):
        abort(400)

class MongoJSONProvider(DefaultJSONProvider):
    """Serialize Mongo ObjectId and datetime in Flask JSON responses."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json = MongoJSONProvider(app)

# ===== MAIN ROUTES =====
@app.route('/')
def home():
    try:
        featured_images = list(mongo.db.gallery.find().sort('uploaded_at', -1).limit(6))
    except Exception:
        featured_images = []
    return render_template('index.html', images=featured_images)

@app.route('/portfolio')
def portfolio():
    try:
        images = list(mongo.db.gallery.find().sort('uploaded_at', -1))
        categories = mongo.db.gallery.distinct('category')
    except Exception:
        images = []
        categories = []
    return render_template('portfolio.html', images=images, categories=categories)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        is_valid, error_message = validate_contact_form(name, email, message)
        if not is_valid:
            flash(error_message, 'error')
            return render_template('contact.html')
        
        contact_data = {
            'name': name,
            'email': email,
            'message': message,
            'submitted_at': datetime.now(timezone.utc),
            'read': False
        }
        
        mongo.db.contacts.insert_one(contact_data)
        flash('Thank you for your message! I will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# ===== ADMIN ROUTES =====
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        validate_csrf()
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user_data = mongo.db.users.find_one({'username': username})
            
            if user_data:
                user_obj = User(user_data)
                password_valid = check_password_hash(user_obj.password_hash, password)
                
                if password_valid:
                    login_user(user_obj, remember=True)
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid username or password', 'error')
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as exc:
            print(f"Login error: {exc}")
            flash('Login error. Please try again.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        stats = {
            'total_images': mongo.db.gallery.count_documents({}),
            'unread_messages': mongo.db.contacts.count_documents({'read': False}),
            'total_contacts': mongo.db.contacts.count_documents({}),
            'recent_messages': list(mongo.db.contacts.find().sort('submitted_at', -1).limit(5))
        }
    except Exception:
        stats = {
            'total_images': 0,
            'unread_messages': 0,
            'total_contacts': 0,
            'recent_messages': []
        }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/gallery', methods=['GET', 'POST'])
@login_required
def admin_gallery():
    if request.method == 'POST':
        validate_csrf()
        title = request.form.get('title')
        category = (request.form.get('category') or '').strip().lower()
        description = request.form.get('description')
        image_file = request.files.get('image')
        featured = bool(request.form.get('featured'))

        if not title or len(title.strip()) < 2:
            flash('Please provide a valid image title', 'error')
            return redirect(url_for('admin_gallery'))
        if category not in ALLOWED_IMAGE_CATEGORIES:
            flash('Please select a valid category', 'error')
            return redirect(url_for('admin_gallery'))
        
        if not image_file or not allowed_file(image_file.filename):
            flash('Please select a valid image file (PNG, JPG, JPEG, GIF, WEBP)', 'error')
            return redirect(url_for('admin_gallery'))
        
        filename = save_image(image_file, category)
        if filename:
            image_data = {
                'title': title,
                'category': category,
                'description': description,
                'filename': filename,
                'featured': featured,
                'uploaded_at': datetime.now(timezone.utc)
            }
            mongo.db.gallery.insert_one(image_data)
            flash('Image uploaded successfully!', 'success')
        else:
            flash('Error uploading image. Please try again.', 'error')
        
        return redirect(url_for('admin_gallery'))
    
    try:
        images = list(mongo.db.gallery.find().sort('uploaded_at', -1))
        categories = mongo.db.gallery.distinct('category')
    except Exception:
        images = []
        categories = []
    
    return render_template('admin/gallery.html', images=images, categories=categories)

@app.route('/admin/delete-image/<image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    validate_csrf()
    try:
        image = mongo.db.gallery.find_one({'_id': ObjectId(image_id)})
        if image:
            delete_image_file(image['filename'])
            mongo.db.gallery.delete_one({'_id': ObjectId(image_id)})
            flash('Image deleted successfully!', 'success')
        else:
            flash('Image not found', 'error')
    except Exception:
        flash('Error deleting image', 'error')
    
    return redirect(url_for('admin_gallery'))

@app.route('/admin/messages')
@login_required
def admin_messages():
    try:
        messages = list(mongo.db.contacts.find().sort('submitted_at', -1))
    except Exception:
        messages = []
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/mark-read/<message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    validate_csrf()
    try:
        result = mongo.db.contacts.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'read': True}}
        )
        if result.matched_count:
            flash('Message marked as read', 'success')
        else:
            flash('Message not found', 'error')
    except Exception:
        flash('Error marking message as read', 'error')
    return redirect(url_for('admin_messages'))

@app.route('/admin/delete-message/<message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    validate_csrf()
    try:
        result = mongo.db.contacts.delete_one({'_id': ObjectId(message_id)})
        if result.deleted_count:
            flash('Message deleted successfully', 'success')
        else:
            flash('Message not found', 'error')
    except Exception:
        flash('Error deleting message', 'error')
    return redirect(url_for('admin_messages'))

@app.route('/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    validate_csrf()
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

# ===== UTILITY ROUTES =====
@app.route('/debug')
def debug_info():
    """Debug route to check database status"""
    if not app.debug and not app.testing:
        abort(404)

    info = {
        'mongo_connected': False,
        'users_count': 0,
        'users': [],
        'database_name': 'svems_photography',
        'collections': [],
        'status': 'checking...'
    }
    
    try:
        info['mongo_connected'] = True
        info['users_count'] = mongo.db.users.count_documents({})
        
        users_data = list(mongo.db.users.find({}, {'password_hash': 0}))
        for user in users_data:
            user['_id'] = str(user['_id'])
            if 'created_at' in user and isinstance(user['created_at'], datetime):
                user['created_at'] = user['created_at'].isoformat()
        
        info['users'] = users_data
        info['collections'] = mongo.db.list_collection_names()
        info['status'] = 'success'
        print(f"Database check: {info['users_count']} users found")
        
    except Exception as exc:
        info['error'] = str(exc)
        info['status'] = 'error'
        print(f"Database error: {exc}")
    
    return jsonify(info)

@app.route('/create-test-user')
def create_test_user():
    """Route to create a test user if needed"""
    if not app.debug and not app.testing:
        abort(404)

    try:
        mongo.db.users.delete_one({'username': 'pulindu'})
        
        test_user = {
            'username': 'pulindu',
            'email': 'pulindu@svems.com',
            'password_hash': generate_password_hash('admin123', method='scrypt'),
            'created_at': datetime.now(timezone.utc),
            'is_active': True
        }
        
        result = mongo.db.users.insert_one(test_user)
        
        return jsonify({
            'success': True,
            'message': 'Test user created successfully!',
            'username': 'pulindu',
            'password': 'admin123',
            'user_id': str(result.inserted_id)
        })
        
    except Exception as exc:
        return jsonify({
            'success': False,
            'error': str(exc)
        })

@app.route('/fix-password-hash')
def fix_password_hash():
    """Fix the password hash to use scrypt method"""
    if not app.debug and not app.testing:
        abort(404)

    try:
        user = mongo.db.users.find_one({'username': 'pulindu'})
        if user:
            mongo.db.users.update_one(
                {'username': 'pulindu'},
                {'$set': {
                    'password_hash': generate_password_hash('admin123', method='scrypt'),
                    'created_at': datetime.now(timezone.utc)
                }}
            )
            return jsonify({
                'success': True,
                'message': 'Password hash updated to scrypt method!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            })
    except Exception as exc:
        return jsonify({
            'success': False,
            'error': str(exc)
        })

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.context_processor
def inject_current_year():
    return {
        'current_year': datetime.now(timezone.utc).year,
        'csrf_token': generate_csrf_token
    }

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/uploads/portraits', exist_ok=True)
    os.makedirs('static/uploads/landscapes', exist_ok=True)
    os.makedirs('static/uploads/events', exist_ok=True)
    
    print("=" * 60)
    print("Svems Photography Application Starting...")
    print("Debug route (dev only): http://localhost:5000/debug")
    print("Fix password hash (dev only): http://localhost:5000/fix-password-hash")
    print("Create test user (dev only): http://localhost:5000/create-test-user")
    print("Admin login: http://localhost:5000/admin/login")
    print("   Username: pulindu")
    print("   Password: admin123")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
