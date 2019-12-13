import logging
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Create database and migration engine instance
db = SQLAlchemy()
migrate = Migrate()


# SQLAlchemy models inherit from db.Model, therefore importing models after instantiating db
from donkey_package import models


def create_app():
    logging.basicConfig(format='%(asctime)s | %(module)s | %(levelname)s | %(message)s',
                        level=logging.DEBUG)

    # Create and configure the WSGI application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(os.environ['APP_SETTINGS'])

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Bind database and migration engine to app
    db.init_app(app)
    migrate.init_app(app, db)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import rss_reader
    app.register_blueprint(rss_reader.bp)

    from . import briefing_view
    app.register_blueprint(briefing_view.bp)
    app.add_url_rule('/', endpoint='index')

    return app

