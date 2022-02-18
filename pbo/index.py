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

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('index', __name__)


def get_item(id, check_user=True):
    item = get_db().execute(
        'SELECT i.id, name, description, model, manual_filename, created, user_id, username'
        ' FROM items i JOIN user u ON i.user_id = u.id'
        ' WHERE i.id = ?',
        (id,)
    ).fetchone()

    if item is None:
        abort(404, "Item id {0} doesn't exist.".format(id))

    if check_user and item['user_id'] != g.user['id']:
        abort(403)

    return item


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class UploadForm(FlaskForm):
    file = FileField()
    submit = SubmitField("Submit")
    download = SubmitField("Download")


@bp.route('/')
def index():
    form = UploadForm()
    db = get_db()
    items = db.execute(
        'SELECT i.id, i.name, description, model, manual_filename, created, user_id, username, category_id, c.name AS category_name, r.name AS room_name, m.name AS manufacturer_name'
        ' FROM items i JOIN user u ON i.user_id = u.id JOIN categories c ON category_id = c.id JOIN rooms r ON room_id = r.id JOIN manufacturers m ON manufacturer_id = m.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index/index.html', items=items, form=form)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = UploadForm()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        room = request.form['room']
        manufacturer = request.form['manufacturer']
        model = request.form['model']
        error = None

        if form.validate_on_submit():
            if form.file.data == None:
                filename = None
            else:
                if allowed_file(form.file.data.filename):
                    filename =  secure_filename(form.file.data.filename)
                else:
                    filename = None
                    error = 'File type not allowed.'
                data = form.file.data.read()
        
        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)

        if filename == None:
            db = get_db()
            db.execute(
                'INSERT INTO items (name, description, category_id, room_id, manufacturer_id, model, user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, description, category, room, manufacturer, model, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index.index'))
        else:
            db = get_db()
            db.execute(
                'INSERT INTO items (name, description, category_id, room_id, manufacturer_id, model, manual_filename, manual, user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, description, category, room, manufacturer, model, filename, data, g.user['id'])
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

    return render_template('index/create.html', categories=categories, rooms=rooms, manufacturers=manufacturers, form=form)


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

    form = UploadForm()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        room = request.form['room']
        manufacturer = request.form['manufacturer']
        model = request.form['model']
        error = None

        if form.file.data == None:
            filename = None
        else:
            if allowed_file(form.file.data.filename):
                filename =  secure_filename(form.file.data.filename)
            else:
                filename = None
                error = 'File type not allowed.'
            data = form.file.data.read()            

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        
        if filename == None:
            db = get_db()
            db.execute(
                'UPDATE items SET name = ?, description = ?, category_id = ?, room_id = ?, manufacturer_id = ?, model = ?'
                ' WHERE id = ?',
                (name, description, category, room, manufacturer, model, id)
            )
            db.commit()
            return redirect(url_for('index.index'))
        else:
            db = get_db()
            db.execute(
                'UPDATE items SET name = ?, description = ?, category_id = ?, room_id = ?, manufacturer_id = ?, model = ?, manual_filename = ?, manual = ?'
                ' WHERE id = ?',
                (name, description, category, room, manufacturer, model, filename, data, id)
            )
            db.commit()
            return redirect(url_for('index.index')) 

    return render_template('index/update.html', item=item, categories=categories, current_category=current_category, rooms=rooms, current_room=current_room, manufacturers=manufacturers, current_manufacturer=current_manufacturer, form=form)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM items WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index.index'))


@bp.route('/<int:id>/downloadmanual', methods=('GET', 'POST'))
@login_required
def downloadmanual(id):
    item = get_item(id)
    form = UploadForm()
    if request.method == "POST":
        db = get_db()
        manual = db.execute(
            'SELECT manual_filename, manual'
            ' FROM items'
            ' WHERE id = ?',
            (item['id'],)
        ).fetchone()
        filename = manual['manual_filename']
        data = manual['manual']
        return send_file(BytesIO(data), attachment_filename=filename, as_attachment=True)

    return render_template("index.html", form=form)


@bp.route('/<int:id>/uploadmanual', methods=('GET', 'POST'))
@login_required
def uploadmanual(id):
    item = get_item(id)
    form = UploadForm()
    if request.method == 'POST':
        error = None

        if form.file.data == None:
            filename = None
        else:
            if allowed_file(form.file.data.filename):
                filename =  secure_filename(form.file.data.filename)
            else:
                filename = None
                error = 'File type not allowed.'
            data = form.file.data.read()

        if error is not None:
            flash(error)

        if filename:
            db = get_db()
            db.execute(
                'UPDATE items SET manual_filename = ?, manual = ?'
                ' WHERE id = ?',
                (filename, data, id)
            )
            db.commit()
            return redirect(url_for('index.index'))       

    return render_template("index/uploadmanual.html", id=id, item=item, form=form)


@bp.route('/<int:id>/deletemanual', methods=('POST',))
@login_required
def deletemanual(id):
    db = get_db()
    db.execute(
        'UPDATE items'
        ' SET manual_filename = NULL, MANUAL = NULL'
        ' WHERE id = ?',
        (id,))
    db.commit()
    return redirect(url_for('index.index', id=id))


@bp.route('/settings')
@login_required
def settings():
    return render_template('index/settings.html')