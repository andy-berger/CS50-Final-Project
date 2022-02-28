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

bp = Blueprint('rooms', __name__, url_prefix='/rooms')


def get_room(id):
    room = get_db().execute(
        'SELECT id, name'
        ' FROM rooms'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if room is None:
        abort(404, "room id {0} doesn't exist.".format(id))

    return room


@bp.route('/')
def index():
    db = get_db()
    rooms = db.execute(
        'SELECT id, name'
        ' FROM rooms'
        ' WHERE id > 1'
        ' ORDER BY name COLLATE NOCASE'
    ).fetchall()
    return render_template('rooms/index.html', rooms=rooms)


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
            'INSERT INTO rooms (name)'
            ' VALUES (?)',
            (name,)
        )
        db.commit()
        return redirect(url_for('rooms.index'))

    return render_template('rooms/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    room = get_room(id)

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
            'UPDATE rooms SET name = ?'
            ' WHERE id = ?',
            (name, id)
        )
        db.commit()
        return redirect(url_for('rooms.index'))

    return render_template('rooms/update.html', room=room)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    room = get_room(id)
    room_name = room['name']

    db = get_db()
    room_ids = db.execute(
        'SELECT * FROM items WHERE room_id = ?', (id,)
    ).fetchall()

    error = None

    if len(room_ids) > 0:
        error = f"Deletion not possible, room \"{room_name}\" is in use."

    if not id > 1:
        error = 'Wrong id.'

    if error is not None:
        flash(error)
        return redirect(url_for('rooms.index'))

    db = get_db()
    db.execute('DELETE FROM rooms WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('rooms.index'))
