from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from squareboat_social.config import Config
from flask_migrate import Migrate
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    print(app.config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    from squareboat_social.users.routes import users
    from squareboat_social.posts.routes import posts
    from squareboat_social.main.routes import main
    from squareboat_social.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    return app

