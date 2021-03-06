import os
import functools

from flask import Blueprint, current_app as app, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from rssbriefing import db
from rssbriefing.db_utils import get_user_by_username
from rssbriefing.models import Users
from rssbriefing.forms import ResetPasswordRequestForm, ResetPasswordForm
from rssbriefing.email import send_password_reset_email

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if g.user is None:
            return redirect(url_for('briefing.landing_page'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = Users.query.get(user_id)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    # If user is already logged in, redirect to index
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        beta_code = request.form['beta_code']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'

        elif not email:
            error = 'E-mail is required.'

        elif not beta_code:
            error = 'Invitation code is required.'

        elif beta_code != app.config["BETA_CODE"]:
            error = 'Wrong invitation code.'

        elif not password:
            error = 'Password is required.'

        elif get_user_by_username(username) is not None:

            error = 'Username {} is already taken.'.format(username)

        if error is None:

            new_user = Users(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    # If user is already logged in, redirect to index
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = get_user_by_username(username)

        if user is None:
            error = 'Incorrect username.'

        elif not check_password_hash(user.password_hash, password):
            error = 'Incorrect password.'

        if error is None:
            '''
            session is a dict that stores data across requests. When validation succeeds, 
            the user’s id is stored in a new session. 
            The data is stored in a cookie that is sent to the browser, 
            and the browser then sends it back with subsequent requests.
            Flask securely signs the data so that it can’t be tampered with.
            '''
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # If user is already logged in, redirect to index
    if g.user:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user:
            send_password_reset_email(user)

        flash('Check your email for the instructions to reset your password.')

        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # If user is already logged in, redirect to index
    if g.user:
        return redirect(url_for('index'))

    user = Users.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')

        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
