from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, logout_user, current_user, login_required

from app import db, bcrypt
from app.users.forms import RegistrationForm, LoginForm, AccountUpdateForm, \
    RequestResetForm, ResetPasswordForm
from app.models import User, Post
from app.users.utils import save_picture, send_password_reset_email

# creating a users blueprint
users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pwd)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Your account has been created, You will be able to login now!', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title="Register", form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login Unsuccessful, Please try again', 'danger')

    return render_template('login.html', title="Login", form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountUpdateForm()
    
    if form.validate_on_submit():
        if form.pfp.data:
            pfp_filename = save_picture(form.pfp.data, form.username.data)
            current_user.image_file = pfp_filename

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account info has been updated', 'success')
        return redirect(url_for('users.account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    pfp_url = url_for('static', filename=f"images/profile_imgs/{current_user.image_file}")
    return render_template('account.html', title='Account', pfp_url=pfp_url, form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page_no = request.args.get('page', 1, type=int)
    
    # getting user
    user = User.query.filter_by(username=username).first_or_404()
    
    # getting all the posts by that user
    user_posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page_no, per_page=current_app.config['POSTS_PER_PAGE'])
    
    return render_template('user_posts.html', posts=user_posts, user=user)

@users.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_password_reset_email(user)
        flash('Please check your email for instructions to reset your password!', 'info')
        return redirect(url_for('users.login'))

    return render_template('request_reset_password.html', title="Request Reset password", form=form)

@users.route('/reset-password<string:token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
         return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash("The token is either Invalid or expired", "warning")
        return redirect(url_for('users.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    
        user.password = hashed_pwd
        db.session.commit()

        flash(f'Your account\'s password has been updated, Please login to continue', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_password.html', title="Reset password", user=user)
