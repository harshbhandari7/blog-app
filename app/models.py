from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
import jwt
from flask import current_app

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(20), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='avatar.jpg')
    password = db.Column(db.String(60), nullable=False)
    post = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.email}, {self.image_file})"

    def get_reset_token(self, expire_secs=1800):
        encoded_token = jwt.encode({
                "user_id": self.id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expire_secs)
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        return encoded_token

    @staticmethod # class level method, doesn't require self
    def verify_reset_token(token):
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms="HS256"
            )['user_id']
        
        except:
            return None
        
        return User.query.get(user_id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') ,nullable=False)

    def __repr__(self):
        return f"Post({self.id}, {self.title}, {self.date_posted})"

