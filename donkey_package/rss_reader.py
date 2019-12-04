from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from donkey_package.auth import login_required
from donkey_package.db import get_db
from donkey_package.feed import parse_feed, update_feed_db, well_formed, get_latest_feed_dict

bp = Blueprint('rss_reader', __name__)


def get_feedlist_for_dropdown(db=None):
    if not db:
        db = get_db()

    feeds = db.execute(
        'SELECT feed.id, title'
        ' FROM feed'
        ' JOIN user on user.id = feed.user_id'
        ' WHERE user.id = ?', (g.user['id'],)
    ).fetchall()

    return feeds


@bp.route('/latest')
@login_required
def latest():
    db = get_db()

    items = db.execute(
        'SELECT i.title, i.description, i.link, i.created'
        ' FROM item i '
        ' JOIN feed f on i.feed_id = f.id'
        ' JOIN user u on u.id = f.user_id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC', (g.user['id'],)
    ).fetchall()

    feeds = get_feedlist_for_dropdown(db)

    return render_template('rss_reader/latest.html', items=items, feeds=feeds)


@bp.route('/single/<int:feed_id>')
@login_required
def single(feed_id):
    refresh = request.args.get('refresh', None)
    if refresh:
        feed_dict = get_latest_feed_dict(feed_id)
        update_feed_db(feed_dict)

    db = get_db()

    # Get all feed entries
    items = db.execute(
        'SELECT i.title, i.description, i.link, i.created, f.id'
        ' FROM item i '
        ' JOIN feed f on i.feed_id = f.id'
        ' JOIN user u on u.id = f.user_id'
        ' WHERE u.id = ? AND f.id = ?'
        ' ORDER BY created DESC', (g.user['id'], feed_id)
    ).fetchall()

    # Get all feeds of user for dropdown menu
    feeds = get_feedlist_for_dropdown(db)

    single_feed = db.execute(
        'SELECT * FROM feed WHERE feed.id = ?', (feed_id,)
    ).fetchone()

    return render_template('rss_reader/single.html', items=items, feeds=feeds, single_feed=single_feed, refresh=refresh)


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
            if not well_formed(feed):
                error = 'Feed is not well-formed!'
                flash(error)
            else:
                title = feed.feed.get('title', 'No title')
                # TODO add html parsing to extract text and img link in description:
                description = feed.feed.get('description', 'No description')
                link = feed.feed.get('link', 'No link')

                # Check whether feed already exists in database
                db = get_db()
                found = db.execute(
                    'SELECT * FROM feed'
                    '   WHERE (title = ? AND description = ? AND link = ? AND user_id = ?)',
                    (title, description, link, g.user['id'])
                ).fetchone()

                if found:
                    error = 'Feed was already added!'
                    flash(error)
                else:
                    db.execute(
                        'INSERT INTO feed (title, description, link, href, user_id)'
                        'VALUES (?, ?, ?, ?, ?)',
                        (title, description, link, xml_href, g.user['id'])
                    )
                    db.commit()

                    update_feed_db(feed)

            return redirect(url_for('rss_reader.latest'))

    feeds = get_feedlist_for_dropdown()

    return render_template('rss_reader/add_feed.html', feeds=feeds)


@bp.route('/delete_feed', methods=('GET', 'POST'))
@login_required
def delete_feed():
    if request.method == 'POST':
        chosen_feed = request.form['FormControlSelect']

        db = get_db()
        db.execute('DELETE FROM feed WHERE (user_id = ? AND title = ?)', (g.user['id'], chosen_feed))
        db.commit()

        return redirect(url_for('rss_reader.latest'))

    feeds = get_feedlist_for_dropdown()

    return render_template('rss_reader/delete_feed.html', feeds=feeds)
