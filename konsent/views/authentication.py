from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, request, render_template, flash, redirect, url_for

from konsent.models import db, User, Union
from konsent.utils import hash_password, check_password
from konsent.forms import RegisterForm, RegisterUnionForm, LoginForm, ConnectUnionForm


view = Blueprint('authentication', __name__)


# user registration
@view.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        # check if username exists
        user_exists = User.query.filter(User.username == username).first()
        if user_exists is not None:
            error = 'This username has already been taken'
            return render_template('register.html', error=error, form=form)
        else:
            # password matches hash
            user = User(username, hash_password(password), union=None)
            # send to database
            db.session.add(user)
            db.session.commit()
            # redirect user
            flash('You\'ve been registered and can now log in.', 'success')
            return redirect(url_for('authentication.login'))

    return render_template('register.html', form=form)


# register new unions
@view.route('/register-union', methods=['GET', 'POST'])
@login_required
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
@view.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        # save form data
        username = form.username.data
        password_candidate = form.password.data
        remember_me = form.remember_me.data

        # find user in database using submitted username
        user = User.query.filter(User.username == username).first()

        if user is not None:

            # compare password to hash
            if check_password(password_candidate, user.password):
                login_user(user, remember = remember_me)
                flash('Youve been logged in.', 'success')
                return redirect(url_for('home.index'))
            else:
                error = 'Wrong password'
                return render_template('login.html', error=error, form=form)
        else:
            error = 'This user doesnt exist'
            return render_template('login.html', error=error, form=form)

    return render_template('login.html', form=form)


# sign user out
@view.route('/logout')
def logout():
    logout_user()
    flash('Youve been logged out', 'success')
    return redirect(url_for('authentication.login'))


# connect to union
@view.route('/connect-union', methods=['GET', 'POST'])
def connect_union():
    form = ConnectUnionForm(request.form)
    form.union.choices = Union.list()

    if request.method == 'POST' and form.validate():
        union = form.union.data
        union_password_candidate = form.union_password.data

        # find union
        target_union = Union.query.filter(Union.union_name == union).first()
        # find user in db
        user = User.query.filter(User.username == current_user.username).first()

        if target_union is not None:
            if check_password(union_password_candidate, target_union.password):
                # password matches
                user.union_id = target_union.id
                db.session.commit()
                flash('You\'ve been connected to this union', 'success')
                return redirect(url_for('home.index'))
            else:
                flash('Wrong union password', 'error')
                return redirect(url_for('authentication.connect_union'))

    return render_template('connect-union.html', form=form)

