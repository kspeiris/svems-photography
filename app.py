from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort, session, Response
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
import csv
import io
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
DEFAULT_SETTINGS = {
    'site_title': 'Svems',
    'hero_subtitle': 'The Art of Visual Storytelling',
    'contact_email': 'pulindu@svems.com',
    'contact_phone': '+94 77 123 4567',
    'contact_address': 'Colombo, Sri Lanka',
    'instagram_url': '',
    'facebook_url': '',
    'twitter_url': '',
    'linkedin_url': '',
    'portfolio_intro': 'Each image reflects a balance of composition, natural light, and emotional detail drawn from life itself.',
    'about_intro': 'From intimate portraits to expansive landscapes - my approach blends editorial composition with genuine human emotion.',
    'contact_response_time': '24h'
}
ADMIN_PER_PAGE_OPTIONS = (10, 25, 50, 100)
ADMIN_GALLERY_SORT_FIELDS = {
    'uploaded_at': 'uploaded_at',
    'title': 'title',
    'category': 'category',
    'featured': 'featured'
}
ADMIN_MESSAGES_SORT_FIELDS = {
    'submitted_at': 'submitted_at',
    'name': 'name',
    'email': 'email',
    'read': 'read'
}

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

def get_site_settings():
    try:
        settings = mongo.db.settings.find_one({}) or {}
    except Exception:
        settings = {}
    return {**DEFAULT_SETTINGS, **settings}

def parse_object_ids(values):
    ids = []
    for value in values:
        try:
            ids.append(ObjectId(value))
        except Exception:
            continue
    return ids

def parse_admin_pagination(default_per_page=25):
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    if page < 1:
        page = 1

    try:
        per_page = int(request.args.get('per_page', default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page
    if per_page not in ADMIN_PER_PAGE_OPTIONS:
        per_page = default_per_page

    return page, per_page

def load_admin_preferences(section):
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(current_user.id)}, {'admin_preferences': 1}) or {}
        return user.get('admin_preferences', {}).get(section, {})
    except Exception:
        return {}

def save_admin_preferences(section, data):
    try:
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': {f'admin_preferences.{section}': data}}
        )
    except Exception:
        pass

def clear_admin_preferences(section):
    try:
        mongo.db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$unset': {f'admin_preferences.{section}': ''}}
        )
    except Exception:
        pass

def parse_sorting(preferred_by, preferred_dir, allowed_fields, default_by):
    sort_by = (request.args.get('sort_by') if 'sort_by' in request.args else preferred_by or default_by)
    if sort_by not in allowed_fields:
        sort_by = default_by

    sort_dir = (request.args.get('sort_dir') if 'sort_dir' in request.args else preferred_dir or 'desc').lower()
    if sort_dir not in {'asc', 'desc'}:
        sort_dir = 'desc'
    return sort_by, sort_dir

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
        featured_count = mongo.db.gallery.count_documents({'featured': True})
        category_counts = list(
            mongo.db.gallery.aggregate([
                {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ])
        )
        stats = {
            'total_images': mongo.db.gallery.count_documents({}),
            'featured_images': featured_count,
            'unread_messages': mongo.db.contacts.count_documents({'read': False}),
            'total_contacts': mongo.db.contacts.count_documents({}),
            'recent_messages': list(mongo.db.contacts.find().sort('submitted_at', -1).limit(5)),
            'recent_images': list(mongo.db.gallery.find().sort('uploaded_at', -1).limit(6)),
            'categories': category_counts
        }
    except Exception:
        stats = {
            'total_images': 0,
            'featured_images': 0,
            'unread_messages': 0,
            'total_contacts': 0,
            'recent_messages': [],
            'recent_images': [],
            'categories': []
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
    
    if request.args.get('reset') == '1':
        clear_admin_preferences('gallery')
        return redirect(url_for('admin_gallery'))

    try:
        prefs = load_admin_preferences('gallery')
        search_term = (request.args.get('q') if 'q' in request.args else prefs.get('q', '')).strip()
        category_filter = (request.args.get('category') if 'category' in request.args else prefs.get('category', '')).strip().lower()
        featured_filter = (request.args.get('featured') if 'featured' in request.args else prefs.get('featured', '')).strip().lower()
        sort_by, sort_dir = parse_sorting(
            preferred_by=prefs.get('sort_by', 'uploaded_at'),
            preferred_dir=prefs.get('sort_dir', 'desc'),
            allowed_fields=ADMIN_GALLERY_SORT_FIELDS,
            default_by='uploaded_at'
        )
        preferred_per_page = prefs.get('per_page', 25)
        if preferred_per_page not in ADMIN_PER_PAGE_OPTIONS:
            preferred_per_page = 25
        page, per_page = parse_admin_pagination(default_per_page=preferred_per_page)

        query = {}
        if search_term:
            query['$or'] = [
                {'title': {'$regex': search_term, '$options': 'i'}},
                {'description': {'$regex': search_term, '$options': 'i'}}
            ]
        if category_filter and category_filter in ALLOWED_IMAGE_CATEGORIES:
            query['category'] = category_filter
        if featured_filter == 'yes':
            query['featured'] = True
        elif featured_filter == 'no':
            query['featured'] = False

        total_items = mongo.db.gallery.count_documents(query)
        total_pages = max(1, (total_items + per_page - 1) // per_page)
        if page > total_pages:
            page = total_pages

        skip = (page - 1) * per_page
        sort_field = ADMIN_GALLERY_SORT_FIELDS.get(sort_by, 'uploaded_at')
        sort_direction = 1 if sort_dir == 'asc' else -1
        images = list(
            mongo.db.gallery.find(query)
            .sort([(sort_field, sort_direction), ('_id', -1)])
            .skip(skip)
            .limit(per_page)
        )
        categories = mongo.db.gallery.distinct('category')
        start_item = skip + 1 if total_items > 0 else 0
        end_item = min(skip + len(images), total_items)

        if any(key in request.args for key in ('q', 'category', 'featured', 'per_page', 'sort_by', 'sort_dir')):
            save_admin_preferences('gallery', {
                'q': search_term,
                'category': category_filter,
                'featured': featured_filter,
                'per_page': per_page,
                'sort_by': sort_by,
                'sort_dir': sort_dir
            })
    except Exception:
        images = []
        categories = []
        search_term = ''
        category_filter = ''
        featured_filter = ''
        sort_by = 'uploaded_at'
        sort_dir = 'desc'
        page = 1
        per_page = 25
        total_items = 0
        total_pages = 1
        start_item = 0
        end_item = 0
    
    return render_template(
        'admin/gallery.html',
        images=images,
        categories=categories,
        filters={
            'q': search_term,
            'category': category_filter,
            'featured': featured_filter
        },
        sorting={
            'sort_by': sort_by,
            'sort_dir': sort_dir
        },
        pagination={
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'start_item': start_item,
            'end_item': end_item,
            'has_prev': page > 1,
            'has_next': page < total_pages
        },
        per_page_options=ADMIN_PER_PAGE_OPTIONS
    )

@app.route('/admin/gallery/update/<image_id>', methods=['POST'])
@login_required
def update_image(image_id):
    validate_csrf()
    title = (request.form.get('title') or '').strip()
    category = (request.form.get('category') or '').strip().lower()
    description = (request.form.get('description') or '').strip()

    if not title or len(title) < 2:
        flash('Image title must be at least 2 characters', 'error')
        return redirect(url_for('admin_gallery'))
    if category not in ALLOWED_IMAGE_CATEGORIES:
        flash('Invalid image category', 'error')
        return redirect(url_for('admin_gallery'))

    try:
        result = mongo.db.gallery.update_one(
            {'_id': ObjectId(image_id)},
            {'$set': {'title': title, 'category': category, 'description': description}}
        )
        if result.matched_count:
            flash('Image details updated', 'success')
        else:
            flash('Image not found', 'error')
    except Exception:
        flash('Unable to update image', 'error')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/toggle-featured/<image_id>', methods=['POST'])
@login_required
def toggle_image_featured(image_id):
    validate_csrf()
    try:
        image = mongo.db.gallery.find_one({'_id': ObjectId(image_id)})
        if not image:
            flash('Image not found', 'error')
            return redirect(url_for('admin_gallery'))
        new_featured_state = not bool(image.get('featured'))
        mongo.db.gallery.update_one(
            {'_id': ObjectId(image_id)},
            {'$set': {'featured': new_featured_state}}
        )
        flash('Featured status updated', 'success')
    except Exception:
        flash('Unable to update featured status', 'error')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/bulk-action', methods=['POST'])
@login_required
def gallery_bulk_action():
    validate_csrf()
    action = (request.form.get('action') or '').strip().lower()
    image_ids = parse_object_ids(request.form.getlist('image_ids'))
    if not image_ids:
        flash('Select at least one image first', 'error')
        return redirect(url_for('admin_gallery'))

    try:
        if action == 'feature':
            mongo.db.gallery.update_many({'_id': {'$in': image_ids}}, {'$set': {'featured': True}})
            flash('Selected images marked as featured', 'success')
        elif action == 'unfeature':
            mongo.db.gallery.update_many({'_id': {'$in': image_ids}}, {'$set': {'featured': False}})
            flash('Selected images removed from featured', 'success')
        elif action == 'delete':
            images = list(mongo.db.gallery.find({'_id': {'$in': image_ids}}))
            for image in images:
                if image.get('filename'):
                    delete_image_file(image['filename'])
            mongo.db.gallery.delete_many({'_id': {'$in': image_ids}})
            flash('Selected images deleted', 'success')
        else:
            flash('Invalid bulk action', 'error')
    except Exception:
        flash('Bulk operation failed', 'error')
    return redirect(url_for('admin_gallery'))

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


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        validate_csrf()
        settings_data = {
            'site_title': (request.form.get('site_title') or DEFAULT_SETTINGS['site_title']).strip(),
            'hero_subtitle': (request.form.get('hero_subtitle') or DEFAULT_SETTINGS['hero_subtitle']).strip(),
            'contact_email': (request.form.get('contact_email') or DEFAULT_SETTINGS['contact_email']).strip(),
            'contact_phone': (request.form.get('contact_phone') or DEFAULT_SETTINGS['contact_phone']).strip(),
            'contact_address': (request.form.get('contact_address') or DEFAULT_SETTINGS['contact_address']).strip(),
            'instagram_url': (request.form.get('instagram_url') or '').strip(),
            'facebook_url': (request.form.get('facebook_url') or '').strip(),
            'twitter_url': (request.form.get('twitter_url') or '').strip(),
            'linkedin_url': (request.form.get('linkedin_url') or '').strip(),
            'portfolio_intro': (request.form.get('portfolio_intro') or DEFAULT_SETTINGS['portfolio_intro']).strip(),
            'about_intro': (request.form.get('about_intro') or DEFAULT_SETTINGS['about_intro']).strip(),
            'contact_response_time': (request.form.get('contact_response_time') or DEFAULT_SETTINGS['contact_response_time']).strip()
        }
        try:
            mongo.db.settings.update_one({}, {'$set': settings_data}, upsert=True)
            flash('Settings updated successfully', 'success')
        except Exception:
            flash('Error updating settings', 'error')
        return redirect(url_for('admin_settings'))
    settings = get_site_settings()
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/messages')
@login_required
def admin_messages():
    try:
        if request.args.get('reset') == '1':
            clear_admin_preferences('messages')
            return redirect(url_for('admin_messages'))

        prefs = load_admin_preferences('messages')
        search_term = (request.args.get('q') if 'q' in request.args else prefs.get('q', '')).strip()
        status_filter = (request.args.get('status') if 'status' in request.args else prefs.get('status', '')).strip().lower()
        sort_by, sort_dir = parse_sorting(
            preferred_by=prefs.get('sort_by', 'submitted_at'),
            preferred_dir=prefs.get('sort_dir', 'desc'),
            allowed_fields=ADMIN_MESSAGES_SORT_FIELDS,
            default_by='submitted_at'
        )
        preferred_per_page = prefs.get('per_page', 25)
        if preferred_per_page not in ADMIN_PER_PAGE_OPTIONS:
            preferred_per_page = 25
        page, per_page = parse_admin_pagination(default_per_page=preferred_per_page)

        query = {}
        if search_term:
            query['$or'] = [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'email': {'$regex': search_term, '$options': 'i'}},
                {'message': {'$regex': search_term, '$options': 'i'}}
            ]
        if status_filter == 'read':
            query['read'] = True
        elif status_filter == 'unread':
            query['read'] = False

        total_items = mongo.db.contacts.count_documents(query)
        total_pages = max(1, (total_items + per_page - 1) // per_page)
        if page > total_pages:
            page = total_pages

        skip = (page - 1) * per_page
        sort_field = ADMIN_MESSAGES_SORT_FIELDS.get(sort_by, 'submitted_at')
        sort_direction = 1 if sort_dir == 'asc' else -1
        messages = list(
            mongo.db.contacts.find(query)
            .sort([(sort_field, sort_direction), ('_id', -1)])
            .skip(skip)
            .limit(per_page)
        )
        start_item = skip + 1 if total_items > 0 else 0
        end_item = min(skip + len(messages), total_items)

        if any(key in request.args for key in ('q', 'status', 'per_page', 'sort_by', 'sort_dir')):
            save_admin_preferences('messages', {
                'q': search_term,
                'status': status_filter,
                'per_page': per_page,
                'sort_by': sort_by,
                'sort_dir': sort_dir
            })
    except Exception:
        messages = []
        search_term = ''
        status_filter = ''
        sort_by = 'submitted_at'
        sort_dir = 'desc'
        page = 1
        per_page = 25
        total_items = 0
        total_pages = 1
        start_item = 0
        end_item = 0
    return render_template(
        'admin/messages.html',
        messages=messages,
        filters={
            'q': search_term,
            'status': status_filter
        },
        sorting={
            'sort_by': sort_by,
            'sort_dir': sort_dir
        },
        pagination={
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'start_item': start_item,
            'end_item': end_item,
            'has_prev': page > 1,
            'has_next': page < total_pages
        },
        per_page_options=ADMIN_PER_PAGE_OPTIONS
    )

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

@app.route('/admin/mark-unread/<message_id>', methods=['POST'])
@login_required
def mark_message_unread(message_id):
    validate_csrf()
    try:
        result = mongo.db.contacts.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'read': False}}
        )
        if result.matched_count:
            flash('Message marked as unread', 'success')
        else:
            flash('Message not found', 'error')
    except Exception:
        flash('Error marking message as unread', 'error')
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

@app.route('/admin/messages/bulk-action', methods=['POST'])
@login_required
def messages_bulk_action():
    validate_csrf()
    action = (request.form.get('action') or '').strip().lower()
    message_ids = parse_object_ids(request.form.getlist('message_ids'))
    if not message_ids:
        flash('Select at least one message first', 'error')
        return redirect(url_for('admin_messages'))

    try:
        if action == 'mark_read':
            mongo.db.contacts.update_many({'_id': {'$in': message_ids}}, {'$set': {'read': True}})
            flash('Selected messages marked as read', 'success')
        elif action == 'mark_unread':
            mongo.db.contacts.update_many({'_id': {'$in': message_ids}}, {'$set': {'read': False}})
            flash('Selected messages marked as unread', 'success')
        elif action == 'delete':
            mongo.db.contacts.delete_many({'_id': {'$in': message_ids}})
            flash('Selected messages deleted', 'success')
        else:
            flash('Invalid bulk action', 'error')
    except Exception:
        flash('Bulk action failed', 'error')
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/export')
@login_required
def export_messages():
    try:
        rows = list(mongo.db.contacts.find().sort('submitted_at', -1))
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['name', 'email', 'message', 'read', 'submitted_at'])
        for item in rows:
            writer.writerow([
                item.get('name', ''),
                item.get('email', ''),
                item.get('message', ''),
                bool(item.get('read', False)),
                item.get('submitted_at').isoformat() if isinstance(item.get('submitted_at'), datetime) else ''
            ])
        content = buffer.getvalue()
    except Exception:
        flash('Could not export messages', 'error')
        return redirect(url_for('admin_messages'))

    return Response(
        content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=contact_messages.csv'}
    )

@app.route('/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    validate_csrf()
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.context_processor
def inject_current_year():
    settings = get_site_settings()
    return {
        'current_year': datetime.now(timezone.utc).year,
        'csrf_token': generate_csrf_token,
        'site_settings': settings
    }

if __name__ == '__main__':
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
