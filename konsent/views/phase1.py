import datetime

from flask import Blueprint, render_template, redirect, request, session, url_for
from sqlalchemy import and_
from flask_login import current_user, login_required

import konsent
from konsent import union_required, REQUIRED_VOTES_DIVISOR, NO_RESULTS_ERROR
from konsent.models import db, User, Post, Vote
from konsent.forms import UpvoteForm


view = Blueprint('phase1', __name__)


# phase 1, issues
@view.route('/phase1')
@login_required
@union_required
def get():
    # find posts
    posts = Post.query.filter(
        and_(
            Post.union_id == current_user.union_id,
            Post.phase == 1)).all()

    if posts:
        return render_template('phase1.html', posts=posts)
    else:
        return render_template('phase1.html', msg=NO_RESULTS_ERROR)


# single post, phase 1
@view.route('/phase1/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@union_required
def post(post_id):
    form = UpvoteForm(request.form, meta={'csrf_context': session})
    post_data = {}
    # find posts
    post = Post.query.get(post_id)
    voted = False
    # check if user already voted
    vote = Vote.query.filter(
        and_(
            Vote.author_id == session["user_id"],
            Vote.post == post)
    ).first()
    if vote is not None:
        voted = True
    post_data['voted'] = voted

    # count total votes
    post_data['votes'] = len(post.votes)

    # if user submitted a vote request
    if request.method == 'POST' and form.validate():

        # if user has already voted, remove his vote
        if post_data['voted']:
            # decrement vote value
            post.votes_count -= 1
            # delete relevant entry in votes
            db.session.delete(vote)

            # commit to database
            db.session.add(post)
            db.session.commit()

            # redirect user
            return redirect(url_for('phase1.get'))

        # if user hasn't already voted, count his vote
        else:
            # increment vote value
            post.votes_count += 1
            # count that this user has now voted
            vote = Vote(current_user.id, post)
            db.session.add(vote)
            # count union members
            union_members = User.query.filter(
                User.union_id == current_user.union_id).count()

            # update vote count variable
            post_data['votes'] = len(post.votes)

            # if enough union members have voted, move this post to phase 2
            if post_data['votes'] >= union_members / REQUIRED_VOTES_DIVISOR:
                # reset create_date
                post.create_date = datetime.datetime.now()
                # increment phase value
                post.phase += 1

            # commit changes to database
            db.session.add(post)
            db.session.commit()

            # redirect user
            return redirect(url_for('phase1.get'))

    return render_template(
        'post.html', post_data=post_data, post=post, phase=1, form=form
    )
