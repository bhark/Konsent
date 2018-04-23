from flask_login import current_user, login_required

from sqlalchemy import and_

from konsent import union_required, NO_RESULTS_ERROR
from konsent.models import Post

from flask import Blueprint, render_template


view = Blueprint('phase3', __name__)


# phase 3, solutions
@view.route('/phase3')
@login_required
@union_required
def get():
    # find posts
    posts = Post.query.filter(
        and_(
            Post.union_id == current_user.union_id,
            Post.phase == 3,
            Post.vetoed_by == None
        )).all()

    if posts:
        return render_template('phase3.html', posts=posts)

    else:
        return render_template('phase3.html', msg=NO_RESULTS_ERROR)


# single post, phase 3
@view.route('/phase3/post/<int:post_id>')
@login_required
@union_required
def post(post_id):

    # find issues
    post = Post.query.get(post_id)
    # TODO: Check that the post is in the correct Union, return a
    # proper error if not
    if post.union_id != current_user.union_id:
        post = None

    discussions = post.list_external_discussions(post_id)
    return render_template('post.html', post=post,
                           comments=post.list_comments(current_user.username),
                           phase=3, discussions=discussions)
