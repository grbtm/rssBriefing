import pytest
from flask import g, session


from donkey_package.db_utils import get_user_by_username


def test_register(client, app):

    assert client.get('/auth/register').status_code == 200

    response = client.post(
        '/auth/register', data={'username': 'a', 'email': 'a@a.com', 'password': 'a'}
    )

    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():

        assert get_user_by_username('a') is not None
