# coding=iso-8859-1
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, HiddenField, SubmitField, BooleanField, validators
from wtforms.validators import InputRequired, Optional
from passlib.hash import sha256_crypt
from functools import wraps
import datetime

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'konsent'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# settings
resting_time = 1 # resting time in phase 2 and 3 - 1440 = 2 days
required_votes_divisor = 2 # number of members in the union divided by this number is required in order to make the issue progress to stage 2


# index
@app.route('/')
def index():
    return render_template('index.html')

# check if logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Du har ikke adgang til dette område', 'danger')
            return redirect(url_for('index'))
    return wrap

# check if not logged in
def is_not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Du er allerede logget ind', 'danger')
            return redirect(url_for('index'))
    return wrap

# phase 1, issues
@app.route('/phase1')
@is_logged_in
def phase1():

    # create cursor
    cur = mysql.connection.cursor()

    # find post
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "%s" AND phase = "1"' % session['connected_union'])

    posts = cur.fetchall()

    if result > 0:
        for post in posts:

            # tilskriv værdier
            now = datetime.datetime.now()
            create_date = post['create_date']
            time_since = str(now - create_date)[:-10]
            hours = int(time_since[:1])
            minutes = time_since[2:4]
            post['time_since_create_hours'] = hours
            post['time_since_create_minutes'] = minutes

        mysql.connection.commit()
        cur.close()

        return render_template('phase1.html', posts=posts)
    else:
        msg = 'Ingen opslag at vise'
        return render_template('phase1.html', msg=msg)

# phase 2, solution proposals
@app.route('/phase2')
@is_logged_in
def phase2():

    # create cursor
    cur = mysql.connection.cursor()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "{0}" AND phase = "2"'.format(session['connected_union']))

    posts = cur.fetchall()

    if result > 0:
        for post in posts:

            # assign "posted x minutes ago" values
            now = datetime.datetime.now()
            create_date = post['create_date']
            time_since = str(now - create_date)[:10]
            hours = int(time_since[:1])
            minutes = time_since[2:4]

            try:
                if int(minutes) >= resting_time: # if the issue is ready to progress
                    # find comment with the most votes
                    data = cur.execute('SELECT body FROM comments WHERE post_id = "{0}" ORDER BY votes DESC LIMIT 1'.format(post['id'], session['connected_union']))
                    comment = cur.fetchone()
                    if comment:
                        cur.execute('UPDATE posts SET phase = "3" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                        cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                        cur.execute('UPDATE posts SET solution = "{0}" WHERE id = "{1}" AND belongs_to_union = "{2}"'.format(comment['body'], post['id'], session['connected_union']))
                        app.logger.info('Flytter opslag med id {0} til fase 3'.format(post['id']))
                        posts = cur.fetchall()
                    else:
                        app.logger.info('Post with id {0} didnt get a proposal in time. Resetting.'.format(post['id']))
                        cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
            except ValueError:
                days = time_since[:1]
                if int(days) >= 2:
                    # find proposal with most votes
                    data = cur.execute('SELECT body FROM comments WHERE post_id = "{0}" ORDER BY votes DESC LIMIT 1'.format(post['id'], session['connected_union']))
                    comment = cur.fetchone()
                    if comment:
                        cur.execute('UPDATE posts SET phase = "3" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                        cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                        cur.execute('UPDATE posts SET solution = "{0}" WHERE id = "{1}" AND belongs_to_union = "{2}"'.format(comment['body'], post['id'], session['connected_union']))
                        app.logger.info('Flytter opslag med id {0} til fase 3'.format(post['id']))
                        posts = cur.fetchall()
                    else:
                        app.logger.info('Opslag med id {0} fik ikke et løsningsforslag i tide. Nulstiller.'.format(post['id']))
                        cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))

            post['time_since_create_hours'] = hours
            post['time_since_create_minutes'] = minutes

        # commit changes to database and close connection
        mysql.connection.commit()
        cur.close()

        return render_template('phase2.html', posts=posts)
    else:
        msg = 'Ingen opslag at vise'
        return render_template('phase2.html', msg=msg)

# phase 3, solutions
@app.route('/phase3')
@is_logged_in
def phase3():
    # create cursor
    cur = mysql.connection.cursor()

    # check if posts from phase 2 should be moved to phase 3
    # find posts
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "{0}" AND phase = "2"'.format(session['connected_union']))
    posts = cur.fetchall()

    if result > 0:
        for post in posts:

            # assign "posted x minutes/hours ago" values
            now = datetime.datetime.now()
            create_date = post['create_date']
            time_since = str(now - create_date)[:10]
            hours = int(time_since[:1])
            minutes = time_since[2:4]

            try:
                if int(minutes) >= resting_time:
                    # find comment with most votes
                    data = cur.execute('SELECT body FROM comments WHERE post_id = "{0}" ORDER BY votes DESC LIMIT 1'.format(post['id'], session['connected_union']))
                    comment = cur.fetchone()
                    cur.execute('UPDATE posts SET phase = "3" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET solution = "{0}" WHERE id = "{1}" AND belongs_to_union = "{2}"'.format(comment['body'], post['id'], session['connected_union']))
                    app.logger.info('Flytter opslag med id {0} til fase 3 i union {1}'.format(post['id'], session['connected_union']))
            except ValueError:
                days = time_since[:1]
                app.logger.info(days)
                if int(days) >= 2:
                    # find comment with most votes
                    data = cur.execute('SELECT body FROM comments WHERE post_id = "{0}" ORDER BY votes DESC LIMIT 1'.format(post['id'], session['connected_union']))
                    comment = cur.fetchone()
                    cur.execute('UPDATE posts SET phase = "3" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET solution = "{0}" WHERE id = "{1}" AND belongs_to_union = "{2}"'.format(comment['body'], post['id'], session['connected_union']))
                    app.logger.info('Flytter opslag med id {0} til fase 3 i union {1}'.format(post['id'], session['connected_union']))


    # check if solutions from phase 3 should be moved to "finished solutions"
    # find posts
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "{0}" AND phase = "3" AND vetoed_by IS NULL'.format(session['connected_union']))
    posts = cur.fetchall()

    if result > 0:
        for post in posts:

            # assign "posted x minutes/hours ago" values
            now = datetime.datetime.now()
            create_date = post['create_date']
            time_since = str(now - create_date)[:10]
            hours = time_since[:1]
            minutes = time_since[2:4]
            post['time_since_create_hours'] = hours
            post['time_since_create_minutes'] = minutes

            try:
                if int(minutes) >= resting_time:
                    cur.execute('UPDATE posts SET phase = "4" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    app.logger.info('Problemet med id {0} i union {1} er nu løst!'.format(post['id'], session['connected_union']))
            except ValueError:
                days = time_since[:1]
                if int(days) >= 2:
                    cur.execute('UPDATE posts SET phase = "4" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    app.logger.info('Problemet med id {0} i union {1} er nu løst!'.format(post['id'], session['connected_union']))

        # commit to database and close connection
        mysql.connection.commit()
        cur.close()

        return render_template('phase3.html', posts=posts)
    else:
        msg = 'No posts.'
        return render_template('phase3.html', msg=msg)

# single post, phase 1
@app.route('/phase1/post/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def post1(id):
    form = CommentForm(request.form)

    # create cursor
    cur = mysql.connection.cursor()

    if request.method == 'POST' and form.validate():
        body = form.body.data
        author = session['name']
        cur.execute('INSERT INTO comments(body, author, post_id) VALUES("{0}", "{1}", "{2}")'.format(body, author, id))
        mysql.connection.commit()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE id = %s', [id])
    post = cur.fetchone()

    # check if user already voted
    result = cur.execute('SELECT * FROM votes WHERE username = "{0}" AND post_id = "{1}" AND type = "post"'.format(session['username'], id))
    if result:
        post['voted'] = True
    else:
        post['voted'] = False

    cur.close()

    return render_template('post.html', post=post, form=form, phase=1)

# single post, phase 2
@app.route('/phase2/post/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def post2(id):
    form = CommentForm(request.form)

    # create cursor
    cur = mysql.connection.cursor()

    if request.method == 'POST' and form.validate():
        body = form.body.data
        author = session['name']
        cur.execute('INSERT INTO comments(body, author, post_id) VALUES("{0}", "{1}", "{2}")'.format(body, author, id))
        mysql.connection.commit()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(id, session['connected_union']))

    post = cur.fetchone()

    # check if user is an authority
    result = cur.execute('SELECT authority FROM users WHERE username = "{0}"'.format(session['username']))
    authority = cur.fetchone()
    if authority['authority'] == True:
        post['authority'] = True
    else:
        post['authority'] = False

    cur.close()

    return render_template('post.html', post=post, form=form, comments=listComments(id, session['username']), phase=2)

# single issue, phase 3
@app.route('/phase3/post/<string:id>', methods=['GET'])
@is_logged_in
def post3(id):
    form = CommentForm(request.form)

    # create cursor
    cur = mysql.connection.cursor()

    # find issues
    result = cur.execute('SELECT * FROM posts WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(id, session['connected_union']))

    post = cur.fetchone()

    cur.close()

    return render_template('post.html', post=post, form=form, comments=listComments(id, session['username']), phase=3)

# view a single solution that's been confirmed (phase 4)
@app.route('/completed/post/<string:id>', methods=['GET'])
@is_logged_in
def post_completed(id):
    form = CommentForm(request.form)

    # create cursor
    cur = mysql.connection.cursor()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(id, session['connected_union']))
    post = cur.fetchone()

    cur.close()

    return render_template('post.html', post=post, form=form, comments=listComments(id, session['username']), phase=4)


# user registration
@app.route('/register', methods = ['GET', 'POST'])
@is_not_logged_in
def register():
    form = RegisterForm(request.form)
    form.users_union.choices = listUnions()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        users_union = form.users_union.data
        password = sha256_crypt.encrypt(str(form.password.data))
        authority = form.authority.data
        app.logger.info(authority)

        union_password_candidate = form.union_password.data

        # create cursor
        cur = mysql.connection.cursor()

        # find union
        result = cur.execute('SELECT * FROM unions WHERE union_name = "{0}"'.format(users_union))

        if result:
            # find saved hash
            data = cur.fetchone()
            union_password = data['password']

            if sha256_crypt.verify(union_password_candidate, union_password):
                # password matches hash
                cur.execute('INSERT INTO users(name, username, connected_union, password, authority) VALUES(%s, %s, %s, %s, %s)', (name, username, users_union, password, authority))
                # send to database
                mysql.connection.commit()
                # close connection
                cur.close()
                # redirect user
                msg = 'Youre now signed up and can login.'
                return render_template('login.html', msg=msg)
            else:
                error = 'Wrong password for union.'
                return render_template('register.html', error=error, form=form)
        else:
            error = 'Something mysterious happened. If youre seeing this, go beat up the developers.'
            return render_template('register.html', error=error, form=form)

    return render_template('register.html', form=form, unions=listUnions())

# register new unions
@app.route('/register-union', methods = ['GET', 'POST'])
@is_not_logged_in
def register_union():
    form = RegisterUnionForm(request.form)
    if request.method == 'POST':
        union_name = form.union_name.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()

        cur.execute('INSERT INTO unions(union_name, password) VALUES("{0}", "{1}")'.format(union_name, password))

        # commit to database
        mysql.connection.commit()

        # close connection
        cur.close()

        msg = 'Your union is now registered, and can be accessed by other users'
        return render_template('index.html', msg=msg)
    return render_template('register-union.html', form=form, unions=printUnions())

# bruger login
@app.route('/login', methods=['GET', 'POST'])
@is_not_logged_in
def login():
    if request.method == 'POST':
        # save form data
        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor
        cur = mysql.connection.cursor()

        # find user in database using submitted username
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])

        if result > 0:
            # find saved hash
            data = cur.fetchone()
            password = data['password']
            name = data['name']
            username = data['username']
            connected_union = data['connected_union']
            authority = data['authority']

            # compare password to hash
            if sha256_crypt.verify(password_candidate, password):
                # that's a match, set session variables
                session['logged_in'] = True
                session['name'] = name
                session['username'] = username
                session['connected_union'] = connected_union
                session['authority'] = authority
                flash('Youve been logged in.', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Wrong password'
                return render_template('login.html', error=error)
            # luk forbindelsen
            cur.close()
        else:
            error = 'This user doesnt exist'
            return render_template('login.html', error=error)

    return render_template('login.html')

# vote on a post
@app.route('/vote/<string:id>')
def vote(id):

    # create cursor
    cur = mysql.connection.cursor()

    # check if user voted
    result = cur.execute('SELECT * FROM votes WHERE username = "{0}" AND post_id = "{1}" AND type = "post"'.format(session['username'], id))

    if result:
        error = 'Youve already voted on this post'
        return render_template('index.html', error=error)
    else:
        # check if user is an authority
        if session['authority'] == True:
            error = 'You dont have permission to vote, stop messing with things.'
            return render_template('index.html', error=error)

        cur.execute('UPDATE posts SET votes = votes + 1 WHERE id = "{0}"'.format(id))
        cur.execute('INSERT INTO votes(username, post_id) VALUES("{0}", "{1}")'.format(session['username'], id))

        result = cur.execute('SELECT votes FROM posts WHERE id = "{0}"'.format(id))
        data = cur.fetchone()
        votes = data['votes']

        # count union members
        result = cur.execute('SELECT COUNT(*) AS "count" FROM users WHERE connected_union = "{0}"'.format(session['connected_union']))
        union_members = cur.fetchone()

        if votes >= union_members['count']/required_votes_divisor:
            app.logger.info('{0} out of {1} members in the union {2} voted on issue with id {3}, sending issue to phase 2'.format(union_members['count']/2, union_members['count'], session['connected_union'], id))
            cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}"'.format(id))
            cur.execute('UPDATE posts SET phase = phase + 1 WHERE id = "{0}"'.format(id))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('phase1'))

# vote on comment
@app.route('/post/vote/<string:id>/<string:post_id>')
def vote_comment(id, post_id):

    # create cursor
    cur = mysql.connection.cursor()

    # check if user already voted
    result = cur.execute('SELECT * FROM votes WHERE username = "{0}" AND post_id = "{1}" AND type = "comment"'.format(session['username'], id))

    if result:
        error = 'Youve already voted.'
        return render_template('index.html', error=error)
    else:
        # check if user is an authority
        if session['authority'] == True:
            error = 'You dont have permission to vote, stop messing with things!'
            return render_template('index.html', error=error)
        data = cur.execute('UPDATE comments SET votes = votes + 1 WHERE id = "{0}"'.format(id))
        cur.execute('INSERT INTO votes(username, post_id, type) VALUES("{0}", "{1}", "comment")'.format(session['username'], id))

    mysql.connection.commit()
    cur.close()

    return redirect("/phase2/post/{0}".format(post_id))

# remove vote on post
@app.route('/unvote/<string:id>')
def unvote(id):

    # create cursor
    cur = mysql.connection.cursor()

    # check if user voted
    result = cur.execute('SELECT * FROM votes WHERE username = "{0}" AND post_id = "{1}"'.format(session['username'], id))

    if result:
        cur.execute('UPDATE posts SET votes = votes - 1 WHERE id = "{0}"'.format(id))
        cur.execute('DELETE FROM votes WHERE username = "{0}" AND post_id = "{1}"'.format(session['username'], id))
    else:
        error = 'Du har ikke stemt, og kan derfor ikke trække din stemme tilbage'
        return render_template('index.html', error=error)

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('phase1'))

# remove vote on comments
@app.route('/post/unvote/<string:id>/<string:post_id>')
def unvote_comment(id, post_id):

    # create cursor
    cur = mysql.connection.cursor()

    # check if user voted
    result = cur.execute('SELECT * FROM votes WHERE username = "{0}" AND post_id = "{1}" AND type = "comment"'.format(session['username'], id))


    if result:
        cur.execute('UPDATE comments SET votes = votes - 1 WHERE id = "{0}"'.format(id))
        cur.execute('DELETE FROM votes WHERE username = "{0}" AND post_id = "{1}" AND type = "comment"'.format(session['username'], id))
    else:
        error = 'Du har ikke stemt endnu'
        return render_template('index.html', error=error)

    mysql.connection.commit()
    cur.close()

    return redirect("/phase2/post/{0}".format(post_id))


# sign user out
@app.route('/logout')
def logout():
    session.clear()
    flash('Du er logget ud', 'success')
    return redirect(url_for('login'))

# new post
@app.route('/new_post', methods=['GET', 'POST'])
@is_logged_in
def new_post():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate() and session['authority'] == False:
        title = form.title.data
        body = form.body.data

        # create cursor
        cur = mysql.connection.cursor()

        # FIRE THE CANNONS, COMRADES!!!
        cur.execute('INSERT INTO posts(title, body, author, belongs_to_union) VALUES(%s, %s, %s, %s)', (title, body, session['name'], session['connected_union']))

        # commit to database and close connection
        mysql.connection.commit()
        cur.close()

        flash('Your post have been published', 'success')
        return redirect(url_for('phase1'))
    return render_template('new_post.html', form=form)

# blocked solutions
@app.route('/vetoed')
@is_logged_in
def vetoed():
    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM posts WHERE vetoed_by IS NOT NULL AND belongs_to_union = "{0}"'.format(session['connected_union']))
    posts = cur.fetchall()

    if result:
        return render_template('vetoed.html', posts=posts)
    else:
        msg = 'No posts.'
        return render_template('vetoed.html', msg=msg)



# veto a solution
@app.route('/veto/<string:id>')
@is_logged_in
def veto(id):

    # if user is an authority trying to veto, all sneaky-beaky like
    if session['authority'] == True:
        error = 'Du har ikke rettigheder til at blokere'
        return render_template('index.html', error=error)

    # create cursor
    cur = mysql.connection.cursor()

    # find and update post
    cur.execute('UPDATE posts SET vetoed_by = "{0}" WHERE id = "{1}"'.format(session['name'], id))

    # commit to database and close connection
    mysql.connection.commit()
    cur.close()

    msg = 'Youve successfully blocked the solution'
    return render_template('phase3.html', msg=msg)
@app.route('/veto/confirm/<string:id>')
@is_logged_in
def veto_confirm(id):
    return render_template('veto.html', id=id)

# finished solutions
@app.route('/completed')
@is_logged_in
def completed():
    # create cursor and find posts
    cur = mysql.connection.cursor()

    # check if issues from phase 3 should be moved here
    result = cur.execute('SELECT * FROM posts WHERE phase = "3" AND belongs_to_union = "{0}"'.format(session['connected_union']))
    posts = cur.fetchall()
    if result:
        for post in posts:
            # assign values... again (this should really be optimized)
            now = datetime.datetime.now()
            create_date = post['create_date']
            time_since = str(now - create_date)[:10]
            minutes = time_since[2:4]

            app.logger.info(time_since)
            try:
                if int(minutes) >= resting_time:
                    cur.execute('UPDATE posts SET phase = "4" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    app.logger.info('Problemet med id {0} i union {1} er nu løst!'.format(post['id'], session['connected_union']))
            except ValueError:
                days = time_since[:1]
                app.logger.info(days)
                if int(days) >= 2:
                    cur.execute('UPDATE posts SET phase = "4" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    app.logger.info('Problemet med id {0} i union {1} er nu løst!'.format(post['id'], session['connected_union']))


        mysql.connection.commit()


    result = cur.execute('SELECT * FROM posts WHERE phase = "4" AND belongs_to_union = "{0}" AND vetoed_by IS NULL'.format(session['connected_union']))
    posts = cur.fetchall()

    if result:
        for post in posts:
            # A S S I G N  M O R E  V A L U E S
            now = datetime.datetime.now()
            create_date = post['create_date']
            time_since = str(now - create_date)[:10]
            minutes = time_since[2:4]

            try:
                if int(minutes) >= resting_time:
                    cur.execute('UPDATE posts SET phase = "4" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    app.logger.info('Problemet med id {0} i union {1} er nu løst!'.format(post['id'], session['connected_union']))
            except ValueError:
                days = time_since[:1]
                app.logger.info(days)
                if int(days) >= 2:
                    cur.execute('UPDATE posts SET phase = "4" WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(post['id'], session['connected_union']))
                    app.logger.info('Problemet med id {0} i union {1} er nu løst!'.format(post['id'], session['connected_union']))

        mysql.connection.commit()
        cur.close()
        return render_template('completed.html', posts=posts)
    else:
        msg = 'Ingen opslag at vise'
        return render_template('completed.html', msg=msg)

@app.route('/about')
def about():
    return render_template('about.html')

# list unions for use somewhere else
def listUnions():
    # create cursor
    cur = mysql.connection.cursor()

    # find all unions in database
    unions = cur.execute('SELECT union_name FROM unions')

    # add unions to tuple
    i = 0
    result = []
    while unions > i:
        data = cur.fetchone()
        _union = data['union_name']
        result.append((_union,_union))
        i+=1
    return result

# find solution proposals for a certain post
def listComments(post_id, username):
    # create cursor
    cur = mysql.connection.cursor()
    _cur = mysql.connection.cursor()

    # find all comments in database belonging to this specific post
    comments = cur.execute('SELECT * FROM comments WHERE post_id = "{0}" ORDER BY votes DESC'.format(post_id))

    # make a tuple with the result
    i = 0
    result = []
    while comments > i:
        data = cur.fetchone()
        comment = {'author':data['author'], 'body':data['body'], 'votes':data['votes'], 'id':data['id']}
        result.append(comment)

        # se om brugeren har stemt
        voted_on = _cur.execute('SELECT * FROM votes WHERE post_id = "{0}" AND username = "{1}"'.format(data['id'], username))
        _cur.fetchone()
        if voted_on:
            comment['voted'] = True
        else:
            comment['voted'] = False

        i+=1

    i = 0

    return result

# list unions for pretty-printing
def printUnions():
    # create cursor
    cur = mysql.connection.cursor()

    # find all unions in database
    unions = cur.execute('SELECT union_name FROM unions')

    # make a neat little tuple with the result
    i = 0
    result = []
    while unions > i:
        data = cur.fetchone()
        _union = data['union_name']
        result.append(_union)
        i+=1
    return result

# csrf (WIP - not implemented yet, and probably doesnt work)
def wrap_requires_csrf(*methods):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if request.method in methods:
                if request.method == 'POST':
                    csrf = request.form.get('csrf')
                elif request.method == 'GET':
                    csrf = request.args.get('csrf')
                if not csrf or csrf != session.get('csrf'):
                    abort(400)
                session['csrf'] = generate_csrf_token()
            return fn(*args, **kwargs)
        return wrapped
    return wrapper


# FORMS
class RegisterUnionForm(Form):
    union_name = StringField('Name', [validators.Length(min=1, max=50)])
    password = PasswordField('Password (hand this out to all members of your union)', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords doesnt match')
    ])
    confirm = PasswordField('Enter your password again')

class RegisterForm(Form):
    name = StringField('Display name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='The passwords doesnt match')
    ])
    confirm = PasswordField('Confirm password')
    authority = BooleanField('Register as authority')
    users_union = SelectField('Union', choices=[('kristensamfundet', 'Kristensamfundet')])
    union_password = PasswordField('Password for union', [validators.DataRequired()])

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=150)])
    body = TextAreaField('Body', [validators.Length(min=20, max=1000, message='Your post body should contain between 20 and 1000 characters.')])

class CommentForm(Form):
    body = TextAreaField('', [validators.length(min=1, max=1000)])

if __name__ == '__main__':
    app.secret_key='Ka,SkqNs//'
    app.run(debug=True)
