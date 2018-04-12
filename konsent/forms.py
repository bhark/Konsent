from datetime import timedelta

from wtforms.csrf.core import CSRF
from wtforms.csrf.session import SessionCSRF
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms import SelectField, HiddenField, SubmitField, BooleanField
from wtforms import IntegerField
from wtforms.validators import Optional


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
    password = PasswordField('Union password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords doesnt match')
    ])
    confirm = PasswordField('Enter your password again')


class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50),
        validators.Regexp(
            "^[a-zA-Z0-9-_]+$", message='Username may only contain alphanumerics, numbers, underscores and dashes')])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='The passwords doesnt match'),
        validators.Regexp(
            "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,666}$", message="Your password does not live up to the requirements")
    ])
    confirm = PasswordField('Confirm password')
    users_union = SelectField(
        'Union', choices=[('kristensamfundet', 'Kristensamfundet')])
    union_password = PasswordField(
        'Password for union', [validators.DataRequired()])


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=150)])
    body = TextAreaField(
        'Body', [validators.Length(min=20, max=1000, message='Your post body should contain between 20 and 1000 characters.')])
    resting_time = IntegerField('Resting time')

class CommentForm(BaseForm):
    body = TextAreaField('', [validators.length(min=1, max=1000)])


class UpvoteForm(BaseForm):
    vote = BooleanField(
        '')  # this field is true, hidden and is both upvote and downvote


class VetoForm(BaseForm):
    veto = BooleanField('')  # this field is hidden and is true


class DiscussionForm(BaseForm):
    url = StringField(
        'URL', [validators.DataRequired(), validators.Length(min=5, max=50)])
