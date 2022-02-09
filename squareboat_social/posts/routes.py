from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from squareboat_social.posts.forms import PostForm
from squareboat_social.models import User, Post
from squareboat_social import db
from squareboat_social.users.utils import save_picture



posts = Blueprint('posts',__name__)






@posts.route('/post/new', methods = ['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='Create A Post',form = form, legend = 'New Post')

@posts.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post)

@posts.route('/post/<int:post_id>/update', methods = ['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data  = post.title 
        form.description.data  = post.description
    return render_template('create_post.html', title = 'Update your Post', form = form, legend = 'Update Post')

@posts.route('/post/<int:post_id>/delete', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
            abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!!', 'success')
    return redirect(url_for('main.home'))





