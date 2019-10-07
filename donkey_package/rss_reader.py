from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from werkzeug.exceptions import abort

from donkey_package.auth import login_required
from donkey_package.db import get_db
from donkey_package.feed import parse_feed, update_feed_db

bp = Blueprint('rss_reader', __name__)


@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT i.title, i.description, i.link'
        ' FROM item i'
    ).fetchall()
    return render_template('rss_reader/index.html', items=items)


@bp.route('/add_feed', methods=('GET', 'POST'))
@login_required
def add_feed():
    if request.method == 'POST':
        xml_href = request.form['xml_href']
        error = None

        if not xml_href:
            error = 'XML file is required!'

        if error is not None:
            flash(error)
        else:
            feed = parse_feed(xml_href)
            title = feed.feed.title if feed.feed.get('title', None) else 'No title'
            description = feed.feed.description if feed.feed.get('description', None) else 'No description'
            link = feed.feed.link if feed.feed.get('link', None) else 'No link'

            db = get_db()
            db.execute(
                'INSERT INTO feed (title, description, link, href, user_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, description, link, xml_href, g.user['id'])
            )
            db.commit()

            update_feed_db(feed)

            return redirect(url_for('rss_reader.index'))

    return render_template('rss_reader/add_feed.html')


# def get_feed(id, check_user=True):
#     feed = get_db().execute(
#         'SELECT '
#     ).fetchone()
