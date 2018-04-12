# coding=iso-8859-1
import argparse
import datetime
from datetime import timedelta
from functools import wraps
from sys import argv

import bcrypt
import click
from sqlalchemy import and_
from flask import Flask, g, render_template, flash, redirect, abort
from flask import url_for, session, logging, request

from .models import db, User, Union, Post, Vote, Comment, ExternalDiscussion
from .forms import (RegisterForm, RegisterUnionForm, ArticleForm,
                    CommentForm, UpvoteForm, VetoForm, DiscussionForm)


# CURRENT VERSION: 0.2a
# config
RESTING_TIME = 666  # resting time in phase 2 and 3 in minutes - 1440 = 2 days
REQUIRED_VOTES_DIVISOR = 2  # divide by this to progress to stage 2
NO_RESULTS_ERROR = 'Nothing to show.'

app = Flask(__name__)


# index
@app.route('/')
def index():
    return render_template('index.html')


# check if logged in
def is_logged_in(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('You dont have access to this area', 'danger')
            return redirect(url_for('index'))
    return wrap


# check if not logged in
def is_not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash('Youre already logged in', 'danger')
            return redirect(url_for('index'))
    return wrap


# phase 1, issues
@app.route('/phase1')
@is_logged_in
def phase1():

    update_phases()

    posts = Post.query.filter(
        Post.union_id == session['connected_union']
    ).filter(
        Post.phase == 1
    ).all()

    if posts:
        return render_template('phase1.html', posts=posts)
    else:
        return render_template('phase1.html', msg=NO_RESULTS_ERROR)


# phase 2, solution proposals
@app.route('/phase2')
@is_logged_in
def phase2():

    update_phases()

    # find posts
    posts = Post.query.filter(
        and_(
            Post.union_id == session['connected_union'],
            Post.phase == 2)).all()


    if posts:
        for post in posts:
            post.progresses_in_minutes = int((post.resting_time / 60) - post.time_since_create['minutes'])
            if post.progresses_in_minutes > 60:
                post.progresses_in_hours = round(post.progresses_in_minutes / 60, 1)
        return render_template('phase2.html', posts=posts)
    else:
        return render_template('phase2.html', msg=NO_RESULTS_ERROR)


# phase 3, solutions
@app.route('/phase3')
@is_logged_in
def phase3():

    update_phases()

    # find posts
    posts = Post.query.filter(
        and_(
            Post.union_id == session['connected_union'],
            Post.phase == 3,
            Post.vetoed_by == None
        )).all()

    if posts:
        for post in posts:
            post.progresses_in_minutes = int((post.resting_time / 60) - post.time_since_create['minutes'])
            if post.progresses_in_minutes > 60:
                post.progresses_in_hours = round(post.progresses_in_minutes / 60, 1)
            app.logger.info(post.progresses_in_minutes)
        return render_template('phase3.html', posts=posts)

    else:
        return render_template('phase3.html', msg=NO_RESULTS_ERROR)


# single post, phase 1
@app.route('/phase1/post/<int:post_id>', methods=['GET', 'POST'])
@is_logged_in
def post1(post_id):
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
            return redirect(url_for('phase1'))

        # if user hasn't already voted, count his vote
        else:
            # increment vote value
            post.votes_count += 1
            # count that this user has now voted
            vote = Vote(session['user_id'], post)
            db.session.add(vote)
            # count union members
            union_members = User.query.filter(
                User.union_id == session['connected_union']).count()

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
            return redirect(url_for('phase1'))

    return render_template(
        'post.html', post_data=post_data, post=post, phase=1, form=form
    )


# single post, phase 2
@app.route('/phase2/post/<int:post_id>', methods=['GET', 'POST'])
@is_logged_in
def post2(post_id):
    commentForm = CommentForm(request.form, meta={'csrf_context': session})
    discussionForm = DiscussionForm(request.form, meta={'csrf_context': session})

    if request.method == 'POST':
        if commentForm.validate():
            body = commentForm.body.data
            author = session['user_id']
            comment = Comment(
                post_id, author, body, author_name=session['username'])
            db.session.add(comment)
            db.session.commit()
        elif discussionForm.validate():
            url = discussionForm.url.data
            author = session['user_id']
            externalDiscussion = ExternalDiscussion(
                url, author, author_name=session['username'],
                post_id=post_id
            )
            db.session.add(discussion)
            db.session.commit()

    # find posts
    post = Post.query.get(post_id)
    # TODO: Check that the post is in the correct Union, return a
    # proper error if not
    if post.union_id != session['connected_union']:
        post = None

    comments = post.list_comments(session['username'])
    externalDiscussions = post.list_external_discussions()
    return render_template('post.html', post=post, commentForm=commentForm,
                           discussionForm=discussionForm, comments=comments,
                           phase=2, externalDiscussions=externalDiscussions)


# single post, phase 3
@app.route('/phase3/post/<int:post_id>')
@is_logged_in
def post3(post_id):

    # find issues
    post = Post.query.get(post_id)
    # TODO: Check that the post is in the correct Union, return a
    # proper error if not
    if post.union_id != session['connected_union']:
        post = None

    return render_template('post.html', post=post,
        comments=post.list_comments(session['username']), phase=3)


# view a single solution that's been confirmed (phase 4)
@app.route('/completed/post/<int:post_id>', methods=['GET'])
@is_logged_in
def post_completed(post_id):
    # find posts
    post = Post.query.get(post_id)
    # TODO: Check that the post is in the correct Union, return a
    # proper error if not
    if post.union_id != session['connected_union']:
        post = None

    return render_template('post.html', post=post,
        comments=post.list_comments(session['username']), phase=4)


# user registration
@app.route('/register', methods=['GET', 'POST'])
@is_not_logged_in
def register():
    form = RegisterForm(request.form)
    form.users_union.choices = Union.list()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        users_union = form.users_union.data
        password = form.password.data
        union_password_candidate = form.union_password.data

        # check if username exists
        user_exists = User.query.filter(User.username == username).first()
        if user_exists is not None:
            error = 'This username has already been taken'
            return render_template('register.html', error=error, form=form)

        # find union
        union = Union.query.filter(Union.union_name == users_union).first()

        if union is not None:
            if check_password(union_password_candidate, union.password):
                # password matches hash
                user = User(username, hash_password(password), union)
                # send to database
                db.session.add(user)
                db.session.commit()
                # redirect user
                msg = 'Youre now signed up and can login.'
                return render_template('login.html', msg=msg)
            else:
                error = 'Wrong password for union.'
                return render_template('register.html', error=error, form=form)
        else:
            error = 'Something mysterious happened.'
            return render_template('register.html', error=error, form=form)

    return render_template('register.html', form=form, unions=Union.list())


# register new unions
@app.route('/register-union', methods=['GET', 'POST'])
@is_not_logged_in
def register_union():
    form = RegisterUnionForm(request.form)
    if request.method == 'POST':
        union_name = form.union_name.data
        password = form.password.data

        union = Union(union_name, hash_password(password))
        db.session.add(union)
        # commit to database
        db.session.commit()

        msg = 'Your union is now registered and can be accessed by other users'
        return render_template('index.html', msg=msg)
    return render_template('register-union.html',
        form=form, unions=Union.print())


# user login
@app.route('/login', methods=['GET', 'POST'])
@is_not_logged_in
def login():
    if request.method == 'POST':
        # save form data
        username = request.form['username']
        password_candidate = request.form['password']

        # find user in database using submitted username
        user = User.query.filter(User.username == username).first()

        if user is not None:
            connected_union_name = user.union.union_name
            connected_union = user.union.id

            # compare password to hash
            if check_password(password_candidate, user.password):
                # that's a match, set session variables
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = user.id
                session['connected_union'] = connected_union
                session['connected_union_name'] = connected_union_name
                flash('Youve been logged in.', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Wrong password'
                return render_template('login.html', error=error)
        else:
            error = 'This user doesnt exist'
            return render_template('login.html', error=error)

    return render_template('login.html')


# sign user out
@app.route('/logout')
def logout():
    session.clear()
    flash('Du er logget ud', 'success')
    return redirect(url_for('login'))



# vote on comment
@app.route('/post/vote/<int:comment_id>/<int:post_id>')
@is_logged_in
def vote_comment(comment_id, post_id):

    # check if user already voted
    result = Vote.query.filter(
        and_(
            Vote.comment_id == comment_id,
            Vote.author_id == session['user_id'],
        )
    ).first()

    if result is not None:
        error = 'You\'ve already voted.'
        return render_template('index.html', error=error)
    else:
        comment = Comment.query.get(comment_id)
        comment.votes_count += 1
        db.session.add(comment)
        vote = Vote(session['user_id'], comment)
        db.session.add(vote)
        db.session.commit()

    return redirect("/phase2/post/{0}".format(post_id))


# remove vote on comments
@app.route('/post/unvote/<int:comment_id>/<int:post_id>')
@is_logged_in
def unvote_comment(comment_id, post_id):
    # check if user already voted
    result = Vote.query.filter(
        and_(
            Vote.comment_id == comment_id,
            Vote.author_id == session['user_id'],
        )
    ).first()

    if result is not None:
        comment = Comment.query.get(comment_id)
        comment.votes_count -= 1
        db.session.add(comment)
        vote = Vote.query.filter(
            and_(
                Vote.author_id == session['user_id'],
                Vote.comment_id == comment_id
            )
        ).first()
        db.session.delete(vote)
        db.session.commit()
    else:
        error = 'You have not voted yet.'
        return render_template('index.html', error=error)

    return redirect("/phase2/post/{0}".format(post_id))

# new post
@app.route('/new-post', methods=['GET', 'POST'])
@is_logged_in
def new_post():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        if request.form['unit'] == 'minutes':
            resting_time = form.resting_time.data * 60
        elif request.form['unit'] == 'hours':
            resting_time = form.resting_time.data * 60 * 60
        elif request.form['unit'] == 'days':
            resting_time = form.resting_time.data * 60 * 60 * 24
        else:
            error = 'An error occurred while trying to submit your post'
            return render_template('index.html', error=error)

        # LIGHT THE FUSES, COMRADES!!!
        post = Post(title, body, session[
                    "connected_union"], session["user_id"], resting_time)
        db.session.add(post)
        db.session.commit()

        flash('Your post have been published', 'success')
        return redirect(url_for('phase1'))
    return render_template('new-post.html', form=form)


# blocked solutions
@app.route('/vetoed')
@is_logged_in
def vetoed():

    update_phases()

    posts = Post.query.filter(
        and_(
            Post.union_id == session['connected_union'],
            Post.vetoed_by_id != None
        )
    ).all()

    if posts:
        return render_template('vetoed.html', posts=posts)
    else:
        return render_template('vetoed.html', msg=NO_RESULTS_ERROR)


# veto a solution
@app.route('/veto/<int:post_id>', methods=['GET', 'POST'])
@is_logged_in
def veto(post_id):

    form = VetoForm(request.form, meta={'csrf_context': session})

    if request.method == 'POST' and form.validate():
        # find and update post
        post = Post.query.get(post_id)
        if post.phase != 3:
            return render_template('index.html', error='This post cant be vetoed right now')
        post.vetoed_by_id = session['user_id']

        # commit to database and close connection
        db.session.add(post)
        db.session.commit()

        msg = 'Youve successfully blocked the solution'
        return redirect(url_for("vetoed"))

    return render_template('veto.html', id=post_id, form=form)


# finished solutions
@app.route('/completed')
@is_logged_in
def completed():
    # Find posts
    posts = Post.query.filter(
        and_(
            Post.phase == 4,
            Post.union_id == session['connected_union'],
            Post.vetoed_by_id == None
        )
    ).all()

    if posts:
        return render_template('completed.html', posts=posts)
    else:
        return render_template('completed.html', msg=NO_RESULTS_ERROR)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/members')
@is_logged_in
def members():
    union = Union.query.filter(Union.id == session['connected_union']).one()
    return render_template('union-members.html', members=union.list_members())


# who voted on this post?
@app.route('/who-voted/<string:what>/<int:id>')
@is_logged_in
def who_voted(what, id):
    if what == 'post':
        cls = Post
    elif what == 'comment':
        cls = Comment
    else:
        abort(404)
    obj = cls.query.filter(cls.id == id).one()
    votes = obj.list_votes()
    return render_template('who-voted.html', votes=votes)

# FUNCTIONS

def hash_password(passwd):
    hashed_passwd = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt())
    return hashed_passwd


def check_password(canditate, stored):
    return bcrypt.checkpw(canditate.encode(), stored.encode())


# move posts on to next phase if ready
def update_phases():
    # find all posts to be moved
    posts = Post.query.filter(Post.union_id == session['connected_union']).all()


    for post in posts:
        # phase 2
        if post.phase == 2 and post.create_date < datetime.datetime.now() - timedelta(minutes = (post.resting_time / 60)):
            solution = Comment.query.filter(
                Comment.post == post
            ).order_by(
                Comment.votes_count.desc()
            ).first()
            # update the post
            if solution is not None:
                post.solution = solution.body
                post.phase = 3
            else:
                app.logger.info(
                    'Post id:{0} didnt find a solution'.format(post.id))
            post.create_date = datetime.datetime.now()
            db.session.add(post)

        # phase 3
        elif post.phase == 3 and post.create_date < datetime.datetime.now() - timedelta(minutes = (post.resting_time / 60)):
            post.create_date = datetime.datetime.now()
            post.phase = 4
            db.session.add(post)
    db.session.commit()


@click.command()
@click.argument('action', type=click.Choice(['runserver', 'createdb']))
@click.option('-d', '--database-name', default='konsent',
              help='Database name')
@click.option('-H', '--database-host', default='127.0.0.1',
              help='Database host')
@click.option('-u', '--database-user', default='root',
              help='Database username')
@click.option('-p', '--database-password', default='',
              help='Database password')
def main(action,
         database_name,
         database_host,
         database_user,
         database_password):

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{username}{sep}{password}@{host}/{database}'.format(
        host=database_host,
        username=database_user,
        sep=':' if len(database_password) else '',
        password=database_password,
        database=database_name
    )

    app.secret_key = 'Ka,SkqNs//'
    db.init_app(app)

    if action == 'runserver':
        app.run(debug=True)
    elif action == 'createdb':
        app.app_context().push()
        db.create_all()


if __name__ == '__main__':
    main()
