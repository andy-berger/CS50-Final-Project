import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


# Open DB connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows that behave like dicts allowing accessing the columns by name
        g.db.row_factory = sqlite3.Row
    
    return g.db


# Close DB connection
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Initialize the DB
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# Insert initial data into the DB
def init_db_data():
    db = get_db()
    # Create initial category in the database
    initial_category = get_db().execute(
        'SELECT name'
        ' FROM categories'
        ' WHERE name = ?',
        ("Uncategorized",)
    ).fetchone()
    if initial_category is None:
        initial_category = db.execute(
            'INSERT INTO categories (name)'
            ' VALUES (?)',
            ("Uncategorized",)
        )
        db.commit()
    # Create initial room in the database
    initial_room = get_db().execute(
        'SELECT name'
        ' FROM rooms'
        ' WHERE name = ?',
        ("No room assigned",)
    ).fetchone()
    if initial_room is None:
        initial_room = db.execute(
            'INSERT INTO rooms (name)'
            ' VALUES (?)',
            ("No room assigned",)
        )
        db.commit()
    # Create initial manufacturer in the database
    initial_manufacturer = get_db().execute(
        'SELECT name'
        ' FROM manufacturers'
        ' WHERE name = ?',
        ("No manufacturer assigned",)
    ).fetchone()
    if initial_manufacturer is None:
        initial_manufacturer = db.execute(
            'INSERT INTO manufacturers (name)'
            ' VALUES (?)',
            ("No manufacturer assigned",)
        )
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    init_db_data()
    click.echo('Initialized the database.')


# Initialize the app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
