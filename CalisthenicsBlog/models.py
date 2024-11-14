from datetime import datetime
from CalisthenicsBlog import db, login_manager
from flask_login import UserMixin
from slugify import slugify


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for post tags
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='reader')
    posts = db.relationship('Post', backref='author', lazy=True)
    is_writer_applicant = db.Column(db.Boolean, default=False)  # True if user has applied to be a writer
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}', '{self.image_file}')"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_writer(self):
        return self.role == 'writer' or self.role == 'admin'
    


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    posts = db.relationship('Post', backref='category', lazy=True)

    def __init__(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['slug'] = slugify(kwargs['name'])
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Category('{self.name}')"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['slug'] = slugify(kwargs['name'])
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Tag('{self.name}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(200))
    featured_image = db.Column(db.String(100))
    is_published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
                          backref=db.backref('posts', lazy=True))

    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            kwargs['slug'] = slugify(kwargs['title'])
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"