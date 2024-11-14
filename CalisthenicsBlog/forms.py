from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, widgets, ValidationError, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from CalisthenicsBlog.models import User 
from flask_wtf.file import FileAllowed; FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField
from CalisthenicsBlog.models import Category, Tag

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                validators=[DataRequired(), Length(min=3, max=20)], 
                default = 'admin')

    email = StringField('Email', 
                        validators=[DataRequired(), Email()], 
                        default = 'admin@example.com')
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired (), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=3, max=20)])

    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = QuerySelectField('Category', query_factory=lambda: Category.query, get_label='name')
    tags = QuerySelectField('Tags', query_factory=lambda: Tag.query, 
        get_label='name', 
        widget=widgets.ListWidget(prefix_label=False), 
        option_widget=widgets.CheckboxInput(), 
        render_kw={'class': 'form-check-input'}, 
        validators=[DataRequired()])
    submit = SubmitField('Post')