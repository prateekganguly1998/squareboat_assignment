from flask import Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from squareboat_social.models import User, Post
from flask import render_template, url_for, flash, redirect, request, abort
from squareboat_social.users.forms import RegisterForm, LoginForm, UpdateAccountForm, EmptyForm, ResetRequestForm, ResetPasswordForm
from squareboat_social import db,bcrypt
from squareboat_social.users.utils import save_picture, send_reset_email


users = Blueprint('users',__name__)



@users.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Succesfully created an account for {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title = 'Sign Up', form = form)

@users.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
            user = User.query.filter_by(email = form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login failed, you sure you entered YOUR credentials ?', 'danger')
    return render_template('login.html', title = 'Log In', form = form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))



@users.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, type='profile')
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Hurray!! Your account is now updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email 
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title = 'User Info',
                            image_file = image_file, 
                            form = form )


#follow/unfollow post request endpoint
@users.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.home'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('users.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('users.user', username=username))
    else:
        return redirect(url_for('main.home'))


@users.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.home'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('users.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('users.user', username=username))
    else:
        return redirect(url_for('main.home'))


# User profile post for others 
@users.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user.html', user=user, form=form)



@users.route('/reset_password', methods = ['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email corresponding to your reset request has been sent.', 'info')
        return redirect(url_for('users.login'))
    return render_template('request_reset.html', title = 'Reset Password', form = form)


@users.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_token(token)
    if user is None:
        flash("That is an invalid or expired token","warning")
        return redirect(url_for('users.request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Congrats!! You updated your password! Log in Now!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)