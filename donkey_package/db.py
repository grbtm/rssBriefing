import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    # g is a special object that is unique for each request.
    # It is used to store data that might be accessed by multiple functions during the request
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # sqlite3.Row tells the connection to return rows that behave like dicts.
        # This allows accessing the columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def get_id_feedtitle_lookup_dict():
    """ Returns a lookup dictionary mapping feed id -> feed title. """

    db = get_db()
    id_feedtitle = db.execute('SELECT id, title FROM feed').fetchall()
    lookup_dict = {key: value for (key, value) in id_feedtitle}
    return lookup_dict


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
