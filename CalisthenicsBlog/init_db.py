# CalisthenicsBlog/init_db.py
from CalisthenicsBlog import db, app, bcrypt
from CalisthenicsBlog.models import User, Category, Tag, Post
import os

def init_db():
    with app.app_context():
        # Create static directories if they don't exist
        os.makedirs('CalisthenicsBlog/static/profile_pics', exist_ok=True)
        os.makedirs('CalisthenicsBlog/static/post_images', exist_ok=True)
        
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create default categories
        categories = [
            Category(name='Beginner Tutorials', description='Guides for those starting with calisthenics'),
            Category(name='Advanced Techniques', description='Complex movements and skills'),
            Category(name='Workout Plans', description='Training programs and routines'),
            Category(name='Nutrition', description='Diet and supplementation advice'),
            Category(name='Progress Stories', description='Community success stories and transformations')
        ]
        
        # Create default tags
        tags = [
            Tag(name='Pull-ups'),
            Tag(name='Push-ups'),
            Tag(name='Muscle-ups'),
            Tag(name='Handstand'),
            Tag(name='Core'),
            Tag(name='Mobility'),
            Tag(name='Recovery')
        ]
        
        # Add categories and tags
        db.session.add_all(categories)
        db.session.add_all(tags)
        
        # Create admin user
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            username='admin',
            email='admin@example.com',
            password=hashed_password,
            role='admin'
        )
        db.session.add(admin)
        
        # Create a sample post
        sample_post = Post(
            title='Welcome to Kingdom Calisthenics',
            content='This is your first post. Edit or delete it to start blogging!',
            author=admin,
            category=categories[0],  # Assign to first category
            tags=[tags[0], tags[1]]  # Assign some tags
        )
        db.session.add(sample_post)
        
        # Commit changes
        db.session.commit()
        
        print("Database initialized successfully!")
        print("Admin credentials:")
        print("Email: admin@example.com")
        print("Password: admin123")

if __name__ == '__main__':
    init_db()