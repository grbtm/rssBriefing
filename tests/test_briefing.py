from rssbriefing.db_utils import get_feedlist_for_dropdown


def add_one_feed_to_users_feedlist(client):
    client.post('/add_feed', data={'xml_href': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'})


def test_index(client, auth):
    response = client.get('/auth/login')

    # Navbar elements on login page
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')

    # Navbar elements for new user without any feeds:
    assert b'Log Out' in response.data
    assert b'Latest' in response.data
    assert b'Add feed' in response.data
    assert b'Delete feed' in response.data
    assert b'All feeds' in response.data


def test_create(client, auth, app):
    auth.login()
    assert client.get('/add_feed').status_code == 200

    add_one_feed_to_users_feedlist(client)

    # Navbar elements for new user with one feed on single feed page:
    response = client.get('/single/1')
    assert b'Log Out' in response.data
    assert b'Latest' in response.data
    assert b'Add feed' in response.data
    assert b'Delete feed' in response.data
    assert b'Refresh' in response.data
    assert b'All feeds' in response.data

    # Confirm that one feed is available in users feedlist
    with app.app_context():
        count = len(get_feedlist_for_dropdown(user_id=1))
        assert count == 1


def test_delete(client, auth, app):
    auth.login()

    with app.app_context():

        # Add one feed to feedlist
        add_one_feed_to_users_feedlist(client)

        # Delete feed
        feed_list = get_feedlist_for_dropdown(user_id=1)
        response = client.post('/delete_feed', data={'FormControlSelect': feed_list[0].title})

        # After delete redirection to 'latest' page
        assert response.headers['Location'] == 'http://localhost/latest'

        # No feed left after deletion
        feed_list = get_feedlist_for_dropdown(user_id=1)
        assert len(feed_list) is 0
