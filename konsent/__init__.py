# coding=iso-8859-1
import datetime
from functools import wraps

from flask import Flask, render_template, Blueprint
from flask_login import LoginManager, current_user

from .models import db, User, Post, Comment


def make_app(secret_key='Ka,SkqNs//', db_uri=None):
    from .views.phase1 import view as phase1_blueprint
    from .views.phase2 import view as phase2_blueprint
    from .views.phase3 import view as phase3_blueprint
    from .views.other import view as other_blueprint
    from .views.authentication import view as register_blueprint

    app = Flask(__name__)
    app.secret_key = secret_key 

    app.register_blueprint(home)
    app.register_blueprint(phase1_blueprint)
    app.register_blueprint(phase2_blueprint)
    app.register_blueprint(phase3_blueprint)
    app.register_blueprint(other_blueprint)
    app.register_blueprint(register_blueprint)

    login_manager.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    if db_uri is not None:
        db.init_app(app)

    return app


# CURRENT VERSION: 0.3b
# config
REQUIRED_VOTES_DIVISOR = 2  # divide by this to progress to stage 2
NO_RESULTS_ERROR = 'Nothing to show.'


# user login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'


# load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# connected union required decorator
def union_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.union_id is None:
            error = 'It\'s dangeours to go alone! Connect to a union before wandering off.'
            return render_template('index.html', error=error)
        return f(*args, **kwargs)
    return decorated_function


home = Blueprint('home', __name__)


# index
@home.route('/')
def index():
    return render_template('index.html')


# move posts on to next phase if ready
def update_phases(app):
    with app.app_context():

        # find all posts to be moved
        posts = Post.query.all()

        for post in posts:
            # phase 2
            if post.phase == 2 and post.end_date < datetime.datetime.now():
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
            elif post.phase == 3 and post.end_date < datetime.datetime.now():
                post.create_date = datetime.datetime.now()
                post.phase = 4
                db.session.add(post)
        db.session.commit()
