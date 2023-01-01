from flask import render_template, request, Blueprint

from app.models import Post

# posts blueprint
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    page_no = request.args.get('page', 1, type=int)
    all_posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page_no, per_page=5)
    return render_template('home.html', posts=all_posts)

@main.route('/about')
def about():
    return render_template('about.html', title='About')