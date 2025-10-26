from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from datetime import datetime
import sys

def create_admin_user():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['svems_photography']
        
        # Check if admin already exists
        existing_user = db.users.find_one({'username': 'pulindu'})
        if existing_user:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = {
            'username': 'pulindu',
            'email': 'pulindu@svems.com',
            'password_hash': generate_password_hash('admin123'),
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        result = db.users.insert_one(admin_user)
        if result.inserted_id:
            print("✅ Admin user created successfully!")
            print("Username: pulindu")
            print("Password: admin123")
            print("Email: pulindu@svems.com")
        else:
            print("❌ Failed to create admin user")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        print("Make sure MongoDB is running!")

if __name__ == '__main__':
    create_admin_user()