from datetime import datetime, timezone

from pymongo import MongoClient
from werkzeug.security import generate_password_hash


def create_admin_user():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['svems_photography']

        existing_user = db.users.find_one({'username': 'pulindu'})
        if existing_user:
            print("Admin user already exists!")
            return

        admin_user = {
            'username': 'pulindu',
            'email': 'pulindu@svems.com',
            'password_hash': generate_password_hash('admin123', method='scrypt'),
            'created_at': datetime.now(timezone.utc),
            'is_active': True
        }

        result = db.users.insert_one(admin_user)
        if result.inserted_id:
            print("Admin user created successfully!")
            print("Username: pulindu")
            print("Password: admin123")
            print("Email: pulindu@svems.com")
        else:
            print("Failed to create admin user")
    except Exception as exc:
        print(f"Error creating admin user: {exc}")
        print("Make sure MongoDB is running!")


if __name__ == '__main__':
    create_admin_user()
