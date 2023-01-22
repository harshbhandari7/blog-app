from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from elasticsearch import Elasticsearch

from app.config import Config 

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

login_manager.login_view = 'users.login'
# setting up message category for login required msg
login_manager.login_message = 'Please login to access the requested page!'
login_manager.login_message_category = 'info' 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db) # migration instance

    # elasticsearch instance
    app.elasticsearch = Elasticsearch(hosts=[app.config['ELASTICSEARCH_URL']], verify_certs=False, basic_auth=('elastic', app.config['ELASTICSEARCH_PASSWORD'])) \
        if app.config['ELASTICSEARCH_URL'] else None

    from app.users.routes import users
    from app.posts.routes import posts
    from app.main.routes import main
    from app.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app
