from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime

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

    @staticmethod
    def get_by_username(db, username):
        try:
            user_data = db.users.find_one({'username': username})
            return User(user_data) if user_data else None
        except:
            return None

class Gallery:
    @staticmethod
    def get_all_images(db):
        try:
            return list(db.gallery.find().sort('uploaded_at', -1))
        except:
            return []

    @staticmethod
    def get_categories(db):
        try:
            return db.gallery.distinct('category')
        except:
            return []

class Contact:
    pass