from flask import Blueprint, render_template, url_for, redirect, flash, request, abort
from CalisthenicsBlog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from CalisthenicsBlog.models import User, Post, Tag, db, Category
from CalisthenicsBlog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import os
import secrets
from PIL import Image

# posts = [
#     {
#         'author': 'Jose',
#         'title': 'Blog Post 1',
#         'content': 'First post content',
#         'date_posted': 'April 20, 2018'
#     },
#     {
#         'author': 'AufWiederhoren',
#         'title': 'Blog Post 2',
#         'content': 'Second post content',
#         'date_posted': 'April 21, 2018'
#     }
# ]

@app.route("/")
@app.route("/home")
def home():
    category_id = request.args.get('category', type=int)
    tag_id = request.args.get('tag', type=int)
    page = request.args.get('page', 1, type=int)
    
    # Base query for posts
    query = Post.query.order_by(Post.date_posted.desc())
    
    # Filter by category if provided
    if category_id:
        query = query.filter(Post.category_id == category_id)
    
    # Filter by tag if provided
    if tag_id:
        query = query.join(Post.tags).filter(Tag.id == tag_id)
    
    # Paginate results
    posts = query.paginate(page=page, per_page=5)  # Adjust `per_page` as needed
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('home.html', posts=posts, categories=categories, tags=tags, int=int)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if 'next' in request.args:
                return redirect(request.args.get('next')) 
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('home'))
    # return render_template('logout.html', title='Logout')



@app.route("/explore_people")
@login_required
def explore_people():
    page = request.args.get('page', 1, type=int)
    users = User.query.filter(User.id != current_user.id).paginate(page=page, per_page=5)
    return render_template('explore_people.html', users=users)


@app.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)



# List to store subscriber emails
subscribers = []

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    subscribers.append(email)
    # You can also add logic to store the email in a database or send a confirmation email
    return redirect(url_for('about'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        try:
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating account: {}'.format(str(e)), 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', 
                            image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_writer() or current_user.is_admin():
        form = PostForm()
        if form.validate_on_submit():
            # Retrieve selected tag IDs from the form
            selected_tag_ids = request.form.getlist('tags')

            # Query the Tag model to get Tag objects based on selected IDs
            selected_tags = Tag.query.filter(Tag.id.in_(selected_tag_ids)).all()
            
            
            post = Post(title=form.title.data, 
                content=form.content.data, 
                category=form.category.data,
                tags=selected_tags,
                author=current_user,
                user_id=current_user.id
                )
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!','success')
            return redirect(url_for('home'))
        return render_template('create_post.html', title='New Post', form=form)
    else:
        flash('You need to be a writer to create a post.', 'danger')
        return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    print(post)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = form.category.data.id  # Update category
        
        # Update tags
        selected_tag_ids = request.form.getlist('tags')
        selected_tags = Tag.query.filter(Tag.id.in_(selected_tag_ids)).all()
        post.tags = selected_tags  # Update the tags relationship
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category  # Pre-select the current category
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) #forbidden route  
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

                                                                              


@app.route('/user_role_change/<int:user_id>', methods=['POST'])
@login_required
def user_role_change(user_id):
    if not current_user.is_admin():
        abort(403)
    user = User.query.get(user_id)
    new_role = request.form.get('role')
    if user and new_role in ['reader', 'writer', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f"{user.username}'s role changed to {new_role}.", "success")
    return redirect(url_for('admin.index'))

@app.route("/admin/user/<int:user_id>/approve_writer", methods=["POST"])
@login_required
def approve_writer(user_id):
    if not current_user.is_admin():
        abort(403)
    user = User.query.get(user_id)
    if user and user.is_writer_applicant:
        user.role = 'writer'
        user.is_writer_applicant = False
        db.session.commit()
        flash(f"{user.username} has been approved as a writer.", "success")
    return redirect(url_for('admin.index'))

@app.route("/admin/user/<int:user_id>/reject_writer", methods=["POST"])
@login_required
def reject_writer(user_id):
    if not current_user.is_admin():
        abort(403)
    user = User.query.get(user_id)
    if user and user.is_writer_applicant:
        user.is_writer_applicant = False
        db.session.commit()
        flash(f"{user.username}'s writer application was rejected.", "danger")
    return redirect(url_for('admin.index'))