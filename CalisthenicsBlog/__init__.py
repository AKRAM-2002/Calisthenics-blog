from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ckeditor import CKEditor


app = Flask(__name__)
app.config['SECRET_KEY'] = '10144b7f46a6c92ec4a320409b47a5b1'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///site.db'
app.config['CKEDITOR_PKG_TYPE'] = 'basic'


ckeditor = CKEditor(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from CalisthenicsBlog import routes