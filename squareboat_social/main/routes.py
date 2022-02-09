from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from squareboat_social.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from squareboat_social.users.forms import EmptyForm


main = Blueprint('main',__name__)



@main.route('/')
@main.route('/home')
@login_required
def home():
    users = list()
    form = EmptyForm()
    if current_user.is_authenticated:
        _following = [_user.id for _user in current_user.followed]
        _following.append(current_user.id)
        users = User.query.filter(User.id.not_in(tuple(_following)))
    return render_template('home.html',posts = current_user.followed_posts(), users = users, form = form)

@main.route('/about')
def about():
    return render_template('about.html',title = 'About')

