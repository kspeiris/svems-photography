from pymongo import MongoClient
import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/svems_photography')

def seed_database():
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    
    # 1. Clear Existing Gallery
    print("Clearing existing gallery data...")
    db.gallery.delete_many({})
    
    # 2. Add Professional Portfolio Items
    print("Adding professional portfolio items...")
    
    portfolio_items = [
        {
            'title': 'Golden Hour Serenity',
            'category': 'landscapes',
            'description': 'A breathtaking sunset over the misty mountain ranges, capturing the soft glow of the sun as it touches the peaks.',
            'filename': 'landscapes/mountain_sunrise.jpg',
            'featured': True,
            'uploaded_at': datetime.now(timezone.utc)
        },
        {
            'title': 'Urban Elegance',
            'category': 'portraits',
            'description': 'Modern portrait photography in a downtown setting, focusing on natural light and urban textures.',
            'filename': 'portraits/urban_portrait.jpg',
            'featured': True,
            'uploaded_at': datetime.now(timezone.utc)
        },
        {
            'title': 'A Promise of Forever',
            'category': 'events',
            'description': 'Elegant wedding photography capturing a candid moment of joy during an outdoor ceremony.',
            'filename': 'events/wedding_candid.jpg',
            'featured': True,
            'uploaded_at': datetime.now(timezone.utc)
        },
        {
            'title': 'Coastal Whispers',
            'category': 'landscapes',
            'description': 'Long exposure shot of the rocky coastline during twilight, creating a dreamy and ethereal effect.',
            'filename': 'landscapes/coastal_twilight.jpg',
            'featured': False,
            'uploaded_at': datetime.now(timezone.utc)
        },
        {
            'title': 'Timeless Grace',
            'category': 'portraits',
            'description': 'Fine art studio portraiture with a focus on dramatic lighting and emotional depth.',
            'filename': 'portraits/studio_portrait.jpg',
            'featured': False,
            'uploaded_at': datetime.now(timezone.utc)
        },
        {
            'title': 'Corporate Dynamics',
            'category': 'events',
            'description': 'Professional coverage of a high-profile corporate event, highlighting key interactions and the general atmosphere.',
            'filename': 'events/corporate_event.jpg',
            'featured': False,
            'uploaded_at': datetime.now(timezone.utc)
        }
    ]
    
    db.gallery.insert_many(portfolio_items)
    
    # 3. Ensure Admin User exists
    print("Ensuring admin user exists...")
    admin_user = db.users.find_one({'username': 'pulindu'})
    if not admin_user:
        db.users.insert_one({
            'username': 'pulindu',
            'email': 'pulindu@svems.com',
            'password_hash': generate_password_hash('admin123', method='scrypt'),
            'created_at': datetime.now(timezone.utc),
            'is_active': True
        })
        print("Admin user 'pulindu' created.")
    else:
        print("Admin user 'pulindu' already exists.")
        
    print("Database seeding complete!")

if __name__ == '__main__':
    seed_database()
