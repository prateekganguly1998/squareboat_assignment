from squareboat_social import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), unique= True, nullable = False)
    email = db.Column(db.String(120), unique= True, nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'profile.png')
    password = db.Column(db.String(160), nullable = False)
    post = db.relationship('Post', backref = 'author', lazy = True)


    def __repr__(self):
        return f"User('{self.username}','{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    created_on = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    description = db.Column(db.Text, nullable = False)
    image = db.Column(db.String(20), nullable = False, default = 'landscape.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)



    def __repr__(self):
        return f"Post('{self.title}','{self.created_on}')"
