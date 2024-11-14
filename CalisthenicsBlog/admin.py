# CalisthenicsBlog/admin.py
from flask import url_for, redirect, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user
from wtforms import TextAreaField, SelectField
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
import os
from .models import User, Post, Category, Tag  # Import models only, not db or app
from flask_admin.actions import action

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class CustomAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        stats = {
            'total_posts': Post.query.count(),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
            'total_tags': Tag.query.count(),
            'recent_posts': Post.query.order_by(Post.date_posted.desc()).limit(5).all(),
            'recent_users': User.query.order_by(User.id.desc()).limit(5).all()
        }
        return self.render('admin/index.html', stats=stats)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == 'admin'

class UserAdmin(SecureModelView):
    column_exclude_list = ['password']
    column_searchable_list = ['username', 'email']
    column_filters = ['username', 'email', 'role']
    form_excluded_columns = ['password']
    can_create = False
    can_delete = False
    column_list = ['username', 'email', 'image_file', 'posts', 'role', 'is_writer_applicant']
    

    form_overrides = {
            'role': SelectField
        }
    form_args = {
        'role': {
            'choices': [('reader', 'Reader'), ('writer', 'Writer'), ('admin', 'Admin')]
        }
    }

    # Action to approve writer application
    @action('approve_writer', 'Approve Writer', 'Are you sure you want to approve the writer application?')
    def action_approve_writer(self, ids):
        for user_id in ids:
            user = User.query.get(user_id)
            if user:
                user.role = 'writer'
                user.is_writer_applicant = False
                db.session.commit()
                flash(f"Approved {user.username}'s writer application.")

    # Action to reject writer application
    @action('reject_writer', 'Reject Application', 'Are you sure you want to reject the application?')
    def action_reject_writer(self, ids):
        for user_id in ids:
            user = User.query.get(user_id)
            if user:
                user.is_writer_applicant = False
                db.session.commit()
                flash(f"Rejected {user.username}'s writer application.")

    def is_accessible(self):
            return current_user.is_authenticated and current_user.is_admin()


    def _list_thumbnail(view, context, model, name):
        if not model.image_file:
            return ''
        return f'<img src="{url_for("static", filename="profile_pics/" + model.image_file)}" width="50">'
    
    column_formatters = {
        'image_file': _list_thumbnail
    }



class PostAdmin(SecureModelView):
    form_base_class = SecureForm
    can_view_details = True
    column_searchable_list = ['title', 'content']
    column_filters = ['date_posted', 'category', 'author']
    column_list = ['title', 'category', 'author', 'date_posted', 'is_published', 'views']
    form_columns = ['title', 'content', 'category', 'tags', 'featured_image', 'excerpt', 'is_published']
    
    form_overrides = {
        'content': CKEditorField,
        'excerpt': TextAreaField
    }
    
    form_widget_args = {
        'excerpt': {
            'rows': 3
        }
    }
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.author = current_user

class CategoryAdmin(SecureModelView):
    column_searchable_list = ['name']
    column_filters = ['name']
    form_columns = ['name', 'description']
    column_list = ['name', 'description', 'post_count']
    
    def _post_count(view, context, model, name):
        return len(model.posts)
    
    column_formatters = {
        'post_count': _post_count
    }

class TagAdmin(SecureModelView):
    column_searchable_list = ['name']
    column_filters = ['name']
    form_columns = ['name']
    column_list = ['name', 'post_count']
    
    def _post_count(view, context, model, name):
        return len(model.posts)
    
    column_formatters = {
        'post_count': _post_count
    }

