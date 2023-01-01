from flask import render_template, url_for, flash, redirect, abort, Blueprint
from flask_login import current_user, login_required

from app import db
from app.posts.forms import CreatePostForm
from app.models import Post

# posts blueprint
posts = Blueprint('posts', __name__)

@posts.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        flash('Your post has been created!', 'success')
        new_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('main.home'))

    return render_template('create_post.html', title='New Post', form=form, legend='Create Post')

@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title={post.title}, post=post)

@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        abort(403)
    
    form = CreatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    
    form.title.data = post.title
    form.content.data = post.content
    
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash("You post has been deleted", 'success')
    
    return redirect(url_for('main.home'))
