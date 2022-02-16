from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from pbo.auth import login_required
from pbo.db import get_db

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT i.id, i.name, description, model, created, user_id, username, category_id, c.name AS category_name, r.name AS room_name, m.name AS manufacturer_name'
        ' FROM items i JOIN user u ON i.user_id = u.id JOIN categories c ON category_id = c.id JOIN rooms r ON room_id = r.id JOIN manufacturers m ON manufacturer_id = m.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index/index.html', items=items)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        room = request.form['room']
        manufacturer = request.form['manufacturer']
        model = request.form['model']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO items (name, description, category_id, room_id, manufacturer_id, model, user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, description, category, room, manufacturer, model, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index.index'))

    db = get_db()
    categories = db.execute(
        'SELECT id, name'
        ' FROM categories',
    ).fetchall()

    rooms = db.execute(
        'SELECT id, name'
        ' FROM rooms',
    ).fetchall()

    manufacturers = db.execute(
        'SELECT id, name'
        ' FROM manufacturers',
    ).fetchall()

    return render_template('index/create.html', categories=categories, rooms=rooms, manufacturers=manufacturers)


def get_item(id, check_user=True):
    item = get_db().execute(
        'SELECT i.id, name, description, model, created, user_id, username'
        ' FROM items i JOIN user u ON i.user_id = u.id'
        ' WHERE i.id = ?',
        (id,)
    ).fetchone()

    if item is None:
        abort(404, "Item id {0} doesn't exist.".format(id))

    if check_user and item['user_id'] != g.user['id']:
        abort(403)

    return item


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    item = get_item(id)

    db = get_db()
    categories = db.execute(
        'SELECT id, name'
        ' FROM categories',
    ).fetchall()

    current_category = db.execute(
        'SELECT category_id'
        ' FROM items'
        ' WHERE id = ?',
        (item['id'],)
    ).fetchone()

    rooms = db.execute(
        'SELECT id, name'
        ' FROM rooms',
    ).fetchall()

    current_room = db.execute(
        'SELECT room_id'
        ' FROM items'
        ' WHERE id = ?',
        (item['id'],)
    ).fetchone()

    manufacturers = db.execute(
        'SELECT id, name'
        ' FROM manufacturers',
    ).fetchall()

    current_manufacturer = db.execute(
        'SELECT manufacturer_id'
        ' FROM items'
        ' WHERE id = ?',
        (item['id'],)
    ).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        room = request.form['room']
        manufacturer = request.form['manufacturer']
        model = request.form['model']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE items SET name = ?, description = ?, category_id = ?, room_id = ?, manufacturer_id = ?, model = ?'
                ' WHERE id = ?',
                (name, description, category, room, manufacturer, model, id)
            )
            db.commit()
            return redirect(url_for('index.index'))

    return render_template('index/update.html', item=item, categories=categories, current_category=current_category, rooms=rooms, current_room=current_room, manufacturers=manufacturers, current_manufacturer=current_manufacturer)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_item(id)
    db = get_db()
    db.execute('DELETE FROM items WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index.index'))

@bp.route('/settings')
@login_required
def settinsg():
    return render_template('index/settings.html')
