from app import app, mongo
from models import User

def init_database():
    with app.app_context():
        # Create admin user if it doesn't exist
        admin_exists = mongo.db.users.find_one({'username': 'pulindu'})
        if not admin_exists:
            User.create_user(mongo.db, 'pulindu', 'pulindu@svems.com', 'admin123')
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
