from flask_login import current_user, login_required
from flask import (Blueprint, render_template, flash, session,
                   redirect, abort, request, url_for)


from konsent import union_required
from konsent.forms import ArticleForm
from konsent.models import db, Union, Post


view = Blueprint('issue', __name__)


# new post
@view.route('/new-post', methods=['GET', 'POST'])
@login_required
@union_required
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

        if resting_time < 3000:
            flash('Resting time cannot be less than 50 minutes', 'error')
            return redirect(url_for('issue.new_post'))

        # LIGHT THE FUSES, COMRADES!!!
        post = Post(title, body, current_user.union_id, current_user.id, resting_time)
        db.session.add(post)
        db.session.commit()

        flash('Your post have been published', 'success')
        return redirect(url_for('phase1.get'))
    return render_template('new-post.html', form=form)
