import logging
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Create database and migration engine instance
db = SQLAlchemy()
migrate = Migrate()

# SQLAlchemy models inherit from db.Model, therefore importing models after instantiating db
from rssbriefing_package import models


def create_app(test_config=None):

    logging.basicConfig(format='%(asctime)s | %(module)s | %(levelname)s | %(message)s',
                        level=logging.DEBUG)

    # Create and configure the WSGI application
    app = Flask(__name__)

    if test_config is None:
        # Load Config subclass according to environment variable
        app.config.from_object(os.environ.get('APP_SETTINGS'))
    else:
        # Load the test config if passed
        app.config.update(test_config)

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
