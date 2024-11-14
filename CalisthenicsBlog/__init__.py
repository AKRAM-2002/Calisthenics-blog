# CalisthenicsBlog/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = '10144b7f46a6c92ec4a320409b47a5b1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['CKEDITOR_PKG_TYPE'] = 'basic'

ckeditor = CKEditor(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models and views here
from .models import User, Post, Category, Tag
from .admin import SecureModelView, CustomAdminIndexView, UserAdmin, PostAdmin, CategoryAdmin, TagAdmin



# Initialize admin
admin = Admin(
    app, 
    name='Kingdom Calisthenics Admin', 
    template_mode='bootstrap4',
    index_view=CustomAdminIndexView()
)

# Create custom ModelView with authentication
class SecureModelView(ModelView):
    def is_accessible(self):
        from flask_login import current_user
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        from flask import redirect, url_for
        return redirect(url_for('login'))


# Add model views
admin.add_view(UserAdmin(User, db.session, name='Users'))
admin.add_view(PostAdmin(Post, db.session, name='Posts'))
admin.add_view(CategoryAdmin(Category, db.session, name='Categories'))
admin.add_view(TagAdmin(Tag, db.session, name='Tags'))

# Add file admin
path = os.path.join(os.path.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/static/', name='Files'))

# Import routes and admin after initializing `db`
from CalisthenicsBlog import routes
from CalisthenicsBlog.admin import Admin