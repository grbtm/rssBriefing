import os
import tempfile

import pytest
from donkey_package import create_app
from donkey_package import db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    os.environ['APP_SETTINGS'] = "config.TestingConfig"
    os.environ['DATABASE_URL'] = db_path
    app = create_app()

    with app.app_context():
        db.session.execute(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()

