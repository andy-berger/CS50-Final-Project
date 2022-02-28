import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from pbo.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return render_template('auth/registrationsuccess.html', username=username)

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/changepassword', methods=('GET', 'POST'))
@login_required
def changepassword():
    if request.method == 'POST':
        current_password = request.form['current_password']
        password = request.form['password']
        confirmation = request.form['confirmation']
        db = get_db()
        error = None

        if not current_password:
            error = 'Current password is required.'
        elif not password:
            error = 'New password is required.'
        elif not confirmation:
            error = 'Password confirmation is required.'
        elif not password == confirmation:
            error = "Passwords don't match."

        current_password_query = db.execute("SELECT password FROM user WHERE id = ?", str(g.user['id'])).fetchone()
        if not check_password_hash(current_password_query[0], current_password):
            error = "Current password is incorrect."
        
        current_user_query = db.execute("SELECT username FROM user WHERE id = ?", str(g.user['id'])).fetchone()
        username = current_user_query[0]

        if error is None:
            db.execute(
                'UPDATE user SET password = ? WHERE id = ?',
                (generate_password_hash(password), g.user['id'])
            )
            db.commit()
            return render_template('auth/passwordchangesuccess.html', username=username)

        flash(error)

    return render_template('auth/changepassword.html')