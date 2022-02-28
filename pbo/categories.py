from dataclasses import is_dataclass
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from pbo.auth import login_required
from pbo.db import get_db
from io import BytesIO
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField

bp = Blueprint('categories', __name__, url_prefix='/categories')


def get_category(id):
    category = get_db().execute(
        'SELECT id, name'
        ' FROM categories'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if category is None:
        abort(404, "category id {0} doesn't exist.".format(id))

    return category


@bp.route('/')
def index():
    db = get_db()
    categories = db.execute(
        'SELECT id, name'
        ' FROM categories'
        ' WHERE id > 1'
        ' ORDER BY name COLLATE NOCASE'
    ).fetchall()
    return render_template('categories/index.html', categories=categories)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        error = None
       
        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)

        db = get_db()
        db.execute(
            'INSERT INTO categories (name)'
            ' VALUES (?)',
            (name,)
        )
        db.commit()
        return redirect(url_for('categories.index'))

    return render_template('categories/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    category = get_category(id)

    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'

        if not id > 1:
            error = 'Wrong id.'

        if error is not None:
            flash(error)
        
        db = get_db()
        db.execute(
            'UPDATE categories SET name = ?'
            ' WHERE id = ?',
            (name, id)
        )
        db.commit()
        return redirect(url_for('categories.index'))

    return render_template('categories/update.html', category=category)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    category = get_category(id)
    category_name = category['name']

    db = get_db()
    category_ids = db.execute(
        'SELECT * FROM items WHERE category_id = ?', (id,)
    ).fetchall()

    error = None

    if len(category_ids) > 0:
        error = f"Deletion not possible, category \"{category_name}\" is in use."

    if not id > 1:
        error = 'Wrong id.'

    if error is not None:
        flash(error)
        return redirect(url_for('categories.index'))

    db = get_db()
    db.execute('DELETE FROM categories WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('categories.index'))
