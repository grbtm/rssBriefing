'''
This module contains pytest fixtures based on the flask documentation test setup:
https://flask.palletsprojects.com/en/1.1.x/tutorial/tests/

The fixtures are used by all tests in the test modules.
'''
import os
import tempfile

import pytest

from rssbriefing import create_app
from rssbriefing import db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({'TESTING': True,
                      'SECRET_KEY': 'test',
                      'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
                      'BETA_CODE': 'test'})

    with app.app_context():
        # Create all tables in temp database
        db.create_all()

        # Populate db with test user and feed
        db.session.execute(_data_sql)
        db.session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Tests make requests to this client."""
    return app.test_client()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
