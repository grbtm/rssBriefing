import logging
import os
import click

from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from rssbriefing.db_utils import get_user_by_id, seed_feeds
from rssbriefing.models import Users, Feed

# Create database and migration engine instance
db = SQLAlchemy()
migrate = Migrate()

# SQLAlchemy models inherit from db.Model, therefore importing models after instantiating db
from rssbriefing import models


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """ Initialize database with seed values of a minimum set of RSS/Atom feeds needed for briefing generation. """

    new_user = Users(username=app.config["SEED_USER"],
                     email=app.config["SEED_EMAIL"],
                     password_hash=generate_password_hash(app.config["SEED_PASSWORD"]))
    db.session.add(new_user)
    db.session.commit()

    seed_user = get_user_by_id(user_id=1)

    for feed in seed_feeds:
        feed_entry = Feed(title=feed["title"], href=feed["href"])
        seed_user.feeds.append(feed_entry)

    db.session.commit()
    click.echo('Initialized the database with seed user and feeds.')


def create_app(test_config=None):
    logging.basicConfig(format='%(asctime)s | %(module)s | %(levelname)s | %(message)s',
                        level=logging.DEBUG)

    # Create and configure the WSGI application
    app = Flask(__name__)

    if test_config is None:
        # Load Config subclass according to environment variable
        app.config.from_object(os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig'))
    else:
        # Load the test config if passed
        app.config.update(test_config)

    # Bind database and migration engine to app
    db.init_app(app)
    migrate.init_app(app, db)

    app.cli.add_command(seed_db_command)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import rss_reader
    app.register_blueprint(rss_reader.bp)

    from . import briefing_view
    app.register_blueprint(briefing_view.bp)
    app.add_url_rule('/', endpoint='index')

    # Register a function to load css files with jinja2
    def get_resource_as_string(name, charset='utf-8'):
        with app.open_resource(name) as f:
            return f.read().decode(charset)

    app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string
    return app
