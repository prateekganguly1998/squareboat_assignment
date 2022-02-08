
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from squareboat_social import app, db, bcrypt, mail
from squareboat_social.forms import RegisterForm, LoginForm, UpdateAccountForm, PostForm, EmptyForm, ResetRequestForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from squareboat_social.models import User, Post
from flask_mail import Message



@app.route('/')
@app.route('/home')
@login_required
def home():
    print(os.environ.get('EMAIL_USER'))
    users = list()
    form = EmptyForm()
    if current_user.is_authenticated:
        _following = [_user.id for _user in current_user.followed]
        _following.append(current_user.id)
        users = User.query.filter(User.id.not_in(tuple(_following)))
    return render_template('home.html',posts = current_user.followed_posts(), users = users, form = form)

@app.route('/about')
def about():
    return render_template('about.html',title = 'About')


@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Succesfully created an account for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Sign Up', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
            user = User.query.filter_by(email = form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login failed, you sure you entered YOUR credentials ?', 'danger')
    return render_template('login.html', title = 'Log In', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture, type):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = str()
    if type == 'profile':
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
        output_size = (125,125)
        i = Image.open(form_picture) 
        i.thumbnail(output_size)
        i.save(picture_path)
    else:
        picture_path = os.path.join(app.root_path, 'static/post_pictures', picture_fn)
        form_picture.save(picture_path)

    return picture_fn



@app.route('/account', methods = ['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email 
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title = 'User Info',
                            image_file = image_file, 
                            form = form )



@app.route('/post/new', methods = ['GET', 'POST'])
@login_required
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        print(form.title.data, form.image.data)
        post = Post(title=form.title.data, description = form.description.data, author = current_user)
        if form.image.data:
            picture_file = save_picture(form.image.data, type='post')
            print(picture_file)
            post.image = picture_file
        db.session.add(post)
        db.session.commit()
        flash('Hurray!! Your Post has been uploaded', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Create A Post',form = form, legend = 'New Post')

@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post)

@app.route('/post/<int:post_id>/update', methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data, type='post')
            post.image = picture_file
        post.title = form.title.data
        post.description = form.description.data
        db.session.commit()
        flash('Hurray!! Your post has been updated', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data  = post.title 
        form.description.data  = post.description
    return render_template('create_post.html', title = 'Update your Post', form = form, legend = 'Update Post')

@app.route('/post/<int:post_id>/delete', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
            abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!!', 'success')
    return redirect(url_for('home'))



#follow/unfollow post request endpoint
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('home'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('home'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


# User profile post for others 
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user.html', user=user, form=form)


# Reset password Logic

def send_reset_email(user):
    token = user.get_token()
    message = Message('Did you request a password reset??',
     sender='noreply@sbassignment.com',
    recipients=[user.email])
    message.body = f'''To reset your password visit the following link:
    {url_for('reset_password', token = token, _external = True)}


    Please ignore if you did not make this request   
    
    '''
    mail.send(message)


@app.route('/reset_password', methods = ['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email corresponding to your reset request has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('request_reset.html', title = 'Reset Password', form = form)


@app.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_token(token)
    if user is None:
        flash("That is an invalid or expired token","warning")
        return redirect(url_for('request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Congrats!! You updated your password! Log in Now!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)