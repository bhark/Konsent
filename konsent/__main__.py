# coding=iso-8859-1
import argparse
from functools import wraps
import datetime
from flask import Flask, g, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms.csrf.core import CSRF
from wtforms.csrf.session import SessionCSRF
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, HiddenField, SubmitField, BooleanField, validators
from functools import wraps
import datetime
from datetime import timedelta
import hashlib

# CURRENT VERSION: 0.2a
# config
RESTING_TIME = 1 # resting time in phase 2 and 3 in minutes - 1440 = 2 days
REQUIRED_VOTES_DIVISOR = 2 # number of members in the union divided by this number is required in order to make the issue progress to stage 2
NO_RESULTS_ERROR = 'Nothing to show.'

app = Flask(__name__)
mysql = MySQL(app)


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

    update_phases()

    # create cursor
    cur = mysql.connection.cursor()

    # find post
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "%s" AND phase = "1"' % session['connected_union'])
    posts = cur.fetchall()
    # close connection to database
    cur.close()

    if result:
        for post in posts:
            post = assign_time_values(post)
        return render_template('phase1.html', posts=posts)
    else:
        return render_template('phase1.html', msg=NO_RESULTS_ERROR)


# phase 2, solution proposals
@app.route('/phase2')
@is_logged_in
def phase2():

    update_phases()

    # create cursor
    cur = mysql.connection.cursor()


    # find posts
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "{0}" AND phase = "2"'.format(session['connected_union']))
    posts = cur.fetchall()


    if result:
        for post in posts:
            post = assign_time_values(post)
        cur.close()

        return render_template('phase2.html', posts=posts)
    else:
        return render_template('phase2.html', msg=NO_RESULTS_ERROR)


# phase 3, solutions
@app.route('/phase3')
@is_logged_in
def phase3():

    update_phases()

    # create cursor
    cur = mysql.connection.cursor()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE belongs_to_union = "{0}" AND phase = 3 AND vetoed_by IS NULL'.format(session['connected_union']))
    posts = cur.fetchall()

    if result:
        for post in posts:
            post = assign_time_values(post)
        cur.close()
        return render_template('phase3.html', posts=posts)
    else:
        return render_template('phase3.html', msg=NO_RESULTS_ERROR)


# single post, phase 1
@app.route('/phase1/post/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def post1(id):
    form = UpvoteForm(request.form, meta={'csrf_context': session})

    # create cursor
    cur = mysql.connection.cursor()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE id = %s', [id])
    post = cur.fetchone()

    # check if user already voted
    result = cur.execute('SELECT * FROM votes WHERE username = "{0}" AND post_id = "{1}" AND type = "post"'.format(session['username'], id))
    post['voted'] = bool(result)

    # count total votes
    result = cur.execute('SELECT votes FROM posts WHERE id = "{0}"'.format(id))
    data = cur.fetchone()
    post['votes'] = data['votes']

    # if user submitted a vote request
    if request.method == 'POST' and form.validate():

        # if user has already voted, remove his vote
        if post['voted']:
            # decrement vote value
            cur.execute('UPDATE posts SET votes = votes - 1 WHERE id = "{0}"'.format(id))
            # delete relevant entry in votes
            cur.execute('DELETE FROM votes WHERE username = "{0}" AND post_id = "{1}"'.format(session['username'], id))

            # commit to database
            mysql.connection.commit()

            # redirect user
            return redirect(url_for('phase1'))

        # if user hasnt already voted, count his vote
        else:
            # increment vote value
            cur.execute('UPDATE posts SET votes = votes + 1 WHERE id = "{0}"'.format(id))
            # count that this user has now voted
            cur.execute('INSERT INTO votes(username, post_id) VALUES("{0}", "{1}")'.format(session['username'], id))

            # count union members
            result = cur.execute('SELECT COUNT(*) AS "count" FROM users WHERE connected_union = "{0}"'.format(session['connected_union']))
            union_members = cur.fetchone()

            # if enough union members have voted, move this post to phase 2
            if post['votes'] >= union_members['count']/REQUIRED_VOTES_DIVISOR:
                # reset create_date
                cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}"'.format(id))
                # increment phase value
                cur.execute('UPDATE posts SET phase = phase + 1 WHERE id = "{0}"'.format(id))

            # commit changes to database
            mysql.connection.commit()

            # redirect user
            return redirect(url_for('phase1'))



    cur.close()

    return render_template('post.html', post=post, phase=1, form=form)


# single post, phase 2
@app.route('/phase2/post/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def post2(id):
    form = CommentForm(request.form, meta={'csrf_context': session})

    # create cursor
    cur = mysql.connection.cursor()

    if request.method == 'POST' and form.validate():
        body = form.body.data
        author = session['name']
        cur.execute('INSERT INTO comments(body, author, post_id) VALUES("{0}", "{1}", "{2}")'.format(body, author, id))
        mysql.connection.commit()

    # find posts
    cur.execute('SELECT * FROM posts WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(id, session['connected_union']))

    post = cur.fetchone()

    cur.close()

    return render_template('post.html', post=post, form=form, comments=list_comments(id, session['username']), phase=2)


# single post, phase 3
@app.route('/phase3/post/<string:id>')
@is_logged_in
def post3(id):

    # create cursor
    cur = mysql.connection.cursor()

    # find issues
    result = cur.execute('SELECT * FROM posts WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(id, session['connected_union']))

    post = cur.fetchone()

    cur.close()

    return render_template('post.html', post=post, comments=list_comments(id, session['username']), phase=3)


# view a single solution that's been confirmed (phase 4)
@app.route('/completed/post/<string:id>', methods=['GET'])
@is_logged_in
def post_completed(id):

    # create cursor
    cur = mysql.connection.cursor()

    # find posts
    result = cur.execute('SELECT * FROM posts WHERE id = "{0}" AND belongs_to_union = "{1}"'.format(id, session['connected_union']))
    post = cur.fetchone()

    cur.close()

    return render_template('post.html', post=post, comments=list_comments(id, session['username']), phase=4)


# user registration
@app.route('/register', methods = ['GET', 'POST'])
@is_not_logged_in
def register():
    form = RegisterForm(request.form)
    form.users_union.choices = list_unions()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        users_union = form.users_union.data
        password = hashlib.sha256(str(form.password.data).encode('utf-8')).hexdigest()

        union_password_candidate = form.union_password.data

        # create cursor
        cur = mysql.connection.cursor()

        # find union
        result = cur.execute('SELECT * FROM unions WHERE union_name = "{0}"'.format(users_union))

        if result:
            # find saved hash
            data = cur.fetchone()
            union_password = data['password']

            if hashlib.sha256(union_password_candidate.encode('utf-8')).hexdigest() == union_password:
                # password matches hash
                cur.execute('INSERT INTO users(name, username, connected_union, password) VALUES(%s, %s, %s, %s)', (name, username, users_union, password))
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

    return render_template('register.html', form=form, unions=list_unions())


# register new unions
@app.route('/register-union', methods = ['GET', 'POST'])
@is_not_logged_in
def register_union():
    form = RegisterUnionForm(request.form)
    if request.method == 'POST':
        union_name = form.union_name.data
        password = hashlib.sha256(str(form.password.data).encode('utf-8')).hexdigest()

        # create cursor
        cur = mysql.connection.cursor()

        cur.execute('INSERT INTO unions(union_name, password) VALUES("{0}", "{1}")'.format(union_name, password))

        # commit to database
        mysql.connection.commit()

        # close connection
        cur.close()

        msg = 'Your union is now registered, and can be accessed by other users'
        return render_template('index.html', msg=msg)
    return render_template('register-union.html', form=form, unions=print_unions())


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

            # compare password to hash
            if hashlib.sha256(password_candidate.encode('utf-8')).hexdigest() == password:
                # that's a match, set session variables
                session['logged_in'] = True
                session['name'] = name
                session['username'] = username
                session['connected_union'] = connected_union
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
        data = cur.execute('UPDATE comments SET votes = votes + 1 WHERE id = "{0}"'.format(id))
        cur.execute('INSERT INTO votes(username, post_id, type) VALUES("{0}", "{1}", "comment")'.format(session['username'], id))

    mysql.connection.commit()
    cur.close()

    return redirect("/phase2/post/{0}".format(post_id))

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
    if request.method == 'POST' and form.validate():
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

    update_phases()

    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM posts WHERE vetoed_by IS NOT NULL AND belongs_to_union = "{0}"'.format(session['connected_union']))
    posts = cur.fetchall()

    if result:
        return render_template('vetoed.html', posts=posts)
    else:
        return render_template('vetoed.html', msg=NO_RESULTS_ERROR)


# veto a solution
@app.route('/veto/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def veto(id):

    form = VetoForm(request.form, meta={'csrf_context': session})

    if request.method == 'POST' and form.validate():
        # create cursor
        cur = mysql.connection.cursor()

        # find and update post
        cur.execute('UPDATE posts SET vetoed_by = "{0}" WHERE id = "{1}" AND phase = 3'.format(session['name'], id))

        # commit to database and close connection
        mysql.connection.commit()
        cur.close()

        msg = 'Youve successfully blocked the solution'
        return redirect(url_for("vetoed"))

    return render_template('veto.html', id=id, form=form)


# finished solutions
@app.route('/completed')
@is_logged_in
def completed():
    # create cursor and find posts
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM posts WHERE phase = "4" AND belongs_to_union = "{0}" AND vetoed_by IS NULL'.format(session['connected_union']))
    posts = cur.fetchall()

    if result:
        for post in posts:
            post = assign_time_values(post)

        return render_template('completed.html', posts=posts)
    else:
        return render_template('completed.html', msg=NO_RESULTS_ERROR)


@app.route('/about')
def about():
    return render_template('about.html')


# FUNCTIONS

# assign "posted x minutes/hours ago" values
def assign_time_values(post):
    now = datetime.datetime.now()
    create_date = post['create_date']
    time_since = str(now - create_date)[:-10]
    hours = int(time_since[:1])
    minutes = time_since[2:4]
    post['time_since_create_hours'] = hours
    post['time_since_create_minutes'] = minutes
    return post

# move posts on to next phase if ready
def update_phases():
    # create cursor
    cur = mysql.connection.cursor()

    # find all posts to be moved
    cur.execute('SELECT * FROM posts WHERE belongs_to_union = "{0}" AND create_date < (NOW() - INTERVAL {1} MINUTE)'.format(session['connected_union'], RESTING_TIME))
    posts = cur.fetchall()

    for post in posts:

        post_id = post['id']
        post_phase = post['phase']

        # phase 2
        if post_phase == 2:
            try:
                cur.execute('SELECT * FROM comments WHERE post_id = "{0}" ORDER BY votes DESC'.format( post_id ))
                solution = cur.fetchone()
                cur.execute('UPDATE posts SET create_date = NOW(), solution = "{0}", phase = 3 WHERE id = {1}'.format( solution['body'], post_id ))
                app.logger.info('Moved post with id {0} from phase 2 to phase 3, with solution "{1}"'.format( post_id, solution['body'] ))
            except TypeError:
                cur.execute('UPDATE posts SET create_date = NOW() WHERE id = "{0}"'.format( post_id ))
                app.logger.info('Post with id {0} didnt find a solution in time'.format( post_id ))

        # phase 3
        elif post_phase == 3:
            cur.execute('UPDATE posts SET create_date = NOW(), phase = 4 WHERE id = {0}'.format(post['id']))

    mysql.connection.commit()
    cur.close()


# list unions for use somewhere else
def list_unions():
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
def list_comments(post_id, username):
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
        voted_on = _cur.execute('SELECT * FROM votes WHERE post_id = "{0}" AND username = "{1}" AND type = "comment"'.format(data['id'], username))
        _cur.fetchone()
        if voted_on:
            comment['voted'] = True
        else:
            comment['voted'] = False

        i+=1

    i = 0

    return result


# list unions for pretty-printing
def print_unions():
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

class BaseForm(Form):
    class Meta:
        # enable csrf
        csrf = True
        # choose a CSRF implementation
        csrf_class = SessionCSRF
        # secret key
        csrf_secret = b'jkasjl123nm,nxm#6'
        # time limit
        csrf_time_limit = timedelta(minutes=20)

class RegisterUnionForm(Form):
    union_name = StringField('Name', [validators.Length(min=1, max=50)])
    password = PasswordField('Password (hand this out to all members of your union)', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords doesnt match')
    ])
    confirm = PasswordField('Enter your password again')


class RegisterForm(Form):
    name = StringField('Display name', [validators.Length(min=1, max=50), validators.Regexp("^[a-zA-Z0-9-_]+$", message='Display name may only contain alphanumerics, numbers, underscores and dashes')])
    username = StringField('Username', [validators.Length(min=4, max=50), validators.Regexp("^[a-zA-Z0-9-_]+$", message='Username may only contain alphanumerics, numbers, underscores and dashes')])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='The passwords doesnt match')
    ])
    confirm = PasswordField('Confirm password')
    users_union = SelectField('Union', choices=[('kristensamfundet', 'Kristensamfundet')])
    union_password = PasswordField('Password for union', [validators.DataRequired()])


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=150)])
    body = TextAreaField('Body', [validators.Length(min=20, max=1000, message='Your post body should contain between 20 and 1000 characters.')])


class CommentForm(BaseForm):
    body = TextAreaField('', [validators.length(min=1, max=1000)])

class UpvoteForm(BaseForm):
    vote = BooleanField('') # this field is hidden, is true by default and can work both as upvote and downvote

class VetoForm(BaseForm):
    veto = BooleanField('') # this field is hidden, and is true by default

def main():
    parser = argparse.ArgumentParser(description='Konsent')
    parser.add_argument('-d', '--database', default='konsent',
                        help='Database name')
    parser.add_argument('-u', '--user', default='root',
                        help='Database username')
    parser.add_argument('-p', '--password', default='',
                        help='Database password')
    args = parser.parse_args()

    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_USER'] = args.user
    app.config['MYSQL_PASSWORD'] = args.password
    app.config['MYSQL_DB'] = args.database
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.secret_key = 'Ka,SkqNs//'
    app.run(debug=True)


if __name__ == '__main__':
    main()
