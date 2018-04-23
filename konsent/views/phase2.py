from functools import wraps

from flask import Blueprint, render_template, request, session
from flask_login import current_user, login_required
from sqlalchemy import and_

from konsent import NO_RESULTS_ERROR, union_required
from konsent.models import db, Post, Comment, ExternalDiscussion
from konsent.forms import (CommentForm, DiscussionForm)


view = Blueprint('phase2', __name__)


# phase 2, solution proposals
@view.route('/phase2')
@login_required
@union_required
def get():

    # find posts
    posts = Post.query.filter(
        and_(
            Post.union_id == current_user.union_id,
            Post.phase == 2)).all()

    if posts:
        return render_template('phase2.html', posts=posts)
    else:
        return render_template('phase2.html', msg=NO_RESULTS_ERROR)


# single post, phase 2
@view.route('/phase2/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@union_required
def post(post_id):
    commentForm = CommentForm(request.form, meta={'csrf_context': session})
    discussionForm = DiscussionForm(request.form, meta={'csrf_context': session})

    if request.method == 'POST':
        if commentForm.submit_comment.data and commentForm.validate():
            body = commentForm.body.data
            author = current_user.id
            comment = Comment(
                post_id, author, body, author_name=current_user.username)
            db.session.add(comment)
            db.session.commit()
        elif discussionForm.submit_url.data and discussionForm.validate():
            count = ExternalDiscussion.query.filter(
                ExternalDiscussion.post_id == post_id
            ).count()
            if count > 3:
                error = 'The maximum amount of discussions have already been added.'
                return render_template('index.html', error=error)
            url = discussionForm.url.data
            author = current_user.id
            author_name = current_user.username
            externalDiscussion = ExternalDiscussion(
                author, author_name, url, post_id)
            db.session.add(externalDiscussion)
            db.session.commit()

    # find posts
    post = Post.query.get(post_id)
    # TODO: Check that the post is in the correct Union, return a
    # proper error if not
    if post.union_id != current_user.union_id:
        post = None

    comments = post.list_comments(current_user.username)
    discussions = post.list_external_discussions(post_id)
    return render_template('post.html', post=post, commentForm=commentForm,
                           discussionForm=discussionForm, comments=comments,
                           phase=2, discussions=discussions,
                           discussion_count=len(discussions))
