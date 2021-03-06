import pytest
from flask import g, session


from rssbriefing.db_utils import get_user_by_username


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'email': 'a@a.com', 'beta_code': 'test', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']
    with app.app_context():
        assert get_user_by_username('a') is not None


@pytest.mark.parametrize(('username', 'email', 'beta_code', 'password', 'message'), (
        ('', '', '', '', b'Username is required.'),
        ('a', '', 'test', 'a', b'E-mail is required.'),
        ('a', 'a@a.com', '', 'a', b'Invitation code is required.' ),
        ('a', 'a@a.com', 'test', '', b'Password is required.'),
        ('test', 'a@a.com', 'test', 'a', b'Username test is already taken.'),
))
def test_register_validate_input(client, username, email, beta_code, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'email': email, 'beta_code': beta_code, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user.username == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
