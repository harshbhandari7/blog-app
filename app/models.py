from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
import jwt
from flask import current_app

from app import db, login_manager
from app.search import add_to_index, remove_from_index, query_index

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

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)

        if total == 0:
            return cls.query.filter_by(id=0), 0
        
        res = []
        leng = len(ids)
        for i in range(leng):
            res.append((ids[i], i))
        
        # converting id into respective objects
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(res, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        # add
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        # update
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        
        # delete
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        
        session._changes = None
    
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

class Post(SearchableMixin, db.Model):
    ''' below class attribute lists the field 
        which needs to be included in index by elastic search ''' 
    __searchable__ = ['content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') ,nullable=False)

    def __repr__(self):
        return f"Post({self.id}, {self.title}, {self.date_posted})"

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
