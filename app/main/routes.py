from flask import render_template, request, Blueprint, g, current_app, url_for
from flask_login import login_required, current_user

from app.models import Post
from app.main.forms import SearchForm
import os

# main blueprint
main = Blueprint('main', __name__)

@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        '''
            This g variable provided by Flask is a place where the application can store data
            that needs to persist through the life of a request.
        '''
        g.search_form = SearchForm()

@main.route('/')
@main.route('/home')
def home():
    page_no = request.args.get('page', 1, type=int)
    all_posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page_no, per_page=current_app.config['POSTS_PER_PAGE'])
    return render_template('home.html', posts=all_posts)

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/search')
@login_required
def search():

    if not g.search_form.validate():
        return redirect(url_for('main.home'))

    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('main.search', q=g.search_form.q.data, page=page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None

    prev_url = url_for('main.search', q=g.search_form.q.data, page=page-1) \
        if page > 1 else None
    
    return render_template('search.html', title='Search', posts=posts, next_url=next_url, prev_url=prev_url)