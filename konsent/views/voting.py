from sqlalchemy import and_
from flask import Blueprint, render_template, session, redirect, request, url_for
from flask_login import current_user, login_required

from konsent import union_required
from konsent.models import db, Post, Vote, Comment
from konsent.forms import VetoForm


view = Blueprint('voting', __name__)


# vote on comment
@view.route('/post/vote/<int:comment_id>/<int:post_id>')
@login_required
@union_required
def vote_comment(comment_id, post_id):

    # check if user already voted
    result = Vote.query.filter(
        and_(
            Vote.comment_id == comment_id,
            Vote.author_id == current_user.id,
        )
    ).first()

    if result is not None:
        error = 'You\'ve already voted.'
        return render_template('index.html', error=error)
    else:
        comment = Comment.query.get(comment_id)
        comment.votes_count += 1
        db.session.add(comment)
        vote = Vote(current_user.id, comment)
        db.session.add(vote)
        db.session.commit()

    return redirect("/phase2/post/{0}".format(post_id))


# remove vote on comments
@view.route('/post/unvote/<int:comment_id>/<int:post_id>')
@login_required
@union_required
def unvote_comment(comment_id, post_id):
    # check if user already voted
    result = Vote.query.filter(
        and_(
            Vote.comment_id == comment_id,
            Vote.author_id == current_user.id,
        )
    ).first()

    if result is not None:
        comment = Comment.query.get(comment_id)
        comment.votes_count -= 1
        db.session.add(comment)
        vote = Vote.query.filter(
            and_(
                Vote.author_id == current_user.id,
                Vote.comment_id == comment_id
            )
        ).first()
        db.session.delete(vote)
        db.session.commit()
    else:
        error = 'You have not voted yet.'
        return render_template('index.html', error=error)

    return redirect("/phase2/post/{0}".format(post_id))


# veto a solution
@view.route('/veto/<int:post_id>', methods=['GET', 'POST'])
@login_required
@union_required
def veto(post_id):

    form = VetoForm(request.form, meta={'csrf_context': session})

    if request.method == 'POST' and form.validate():
        # find and update post
        post = Post.query.get(post_id)
        if post.phase != 3:
            return render_template('index.html', error='This post cant be vetoed right now')
        post.vetoed_by_id = current_user.id

        # commit to database and close connection
        db.session.add(post)
        db.session.commit()

        msg = 'Youve successfully blocked the solution'
        return redirect(url_for("other.vetoed"))

    return render_template('veto.html', id=post_id, form=form)


