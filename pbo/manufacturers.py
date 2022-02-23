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

bp = Blueprint('manufacturers', __name__, url_prefix='/manufacturers')


def get_manufacturer(id):
    manufacturer = get_db().execute(
        'SELECT id, name'
        ' FROM manufacturers'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if manufacturer is None:
        abort(404, "Manufacturer id {0} doesn't exist.".format(id))

    return manufacturer


@bp.route('/')
def index():
    db = get_db()
    manufacturers = db.execute(
        'SELECT id, name'
        ' FROM manufacturers'
        ' WHERE id > 1'
        ' ORDER BY name'
    ).fetchall()
    return render_template('manufacturers/index.html', manufacturers=manufacturers)


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
            'INSERT INTO manufacturers (name)'
            ' VALUES (?)',
            (name,)
        )
        db.commit()
        return redirect(url_for('manufacturers.index'))

    return render_template('manufacturers/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    manufacturer = get_manufacturer(id)

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
            'UPDATE manufacturers SET name = ?'
            ' WHERE id = ?',
            (name, id)
        )
        db.commit()
        return redirect(url_for('manufacturers.index'))

    return render_template('manufacturers/update.html', manufacturer=manufacturer)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    manufacturer = get_manufacturer(id)
    manufacturer_name = manufacturer['name']

    db = get_db()
    manufacturer_ids = db.execute(
        'SELECT * FROM items WHERE manufacturer_id = ?', (id,)
    ).fetchall()

    error = None

    if len(manufacturer_ids) > 0:
        error = f"Deletion not possible, manufacturer \"{manufacturer_name}\" is in use."

    if not id > 1:
        error = 'Wrong id.'

    if error is not None:
        flash(error)
        return redirect(url_for('manufacturers.index'))

    db = get_db()
    db.execute('DELETE FROM manufacturers WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('manufacturers.index'))
