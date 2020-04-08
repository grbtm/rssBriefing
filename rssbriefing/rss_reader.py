from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from rssbriefing import db
from rssbriefing.auth import login_required
from rssbriefing.db_utils import get_user_by_id, get_feedlist_for_dropdown
from rssbriefing.feed import parse_feed, update_feed_db, well_formed, get_latest_feed_dict
from rssbriefing.models import Feed, Users, Item

bp = Blueprint('rss_reader', __name__)


@bp.route('/latest')
@login_required
def latest():

    items = Item.query. \
        join(Feed). \
        join(Feed.users). \
        filter(Users.id == g.user.id). \
        order_by(Item.created.desc()). \
        limit(20)

    feeds = get_feedlist_for_dropdown(g.user.id)

    return render_template('rss_reader/latest.html', items=items, feeds=feeds)


@bp.route('/single/<int:feed_id>')
@login_required
def single(feed_id):

    refresh = request.args.get('refresh', None)

    if refresh:
        feed_dict = get_latest_feed_dict(feed_id)
        update_feed_db(feed_id, feed_dict)

    items = Item.query. \
        join(Feed). \
        filter(Feed.id == feed_id). \
        order_by(Item.created.desc()). \
        limit(50)

    # Get all feeds of user for dropdown menu
    feeds = get_feedlist_for_dropdown(g.user.id)

    # Get the given feed entry from db
    single_feed = Feed.query.filter_by(id=feed_id).first()

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

            parsed_feed = parse_feed(xml_href)

            if not well_formed(parsed_feed):

                error = 'Feed is not well-formed!'
                flash(error)

            else:

                title = parsed_feed.feed.get('title', 'No title')
                # TODO add html parsing to extract text and img link in description:
                description = parsed_feed.feed.get('description', 'No description')
                link = parsed_feed.feed.get('link', 'No link')

                # Check whether feed already exists in database
                found_feed = Feed.query.filter_by(title=title).first()

                # Check whether relation to given user exists
                current_user = get_user_by_id(g.user.id)

                if found_feed:

                    if current_user.id in [user.id for user in found_feed.users]:

                        error = 'Feed was already added!'
                        flash(error)

                    # If feed exists but no relation to user exists yet, create one
                    else:
                        current_user.feeds.append(found_feed)
                        db.session.commit()

                # If feed doesn't exist at all in database, add it and create relation to given user
                else:

                    feed_entry = Feed(title=title, description=description, link=link, href=xml_href)
                    current_user.feeds.append(feed_entry)
                    db.session.commit()

                    # After committing, the model will have the id property set
                    update_feed_db(feed_entry.id, parsed_feed)

            return redirect(url_for('rss_reader.latest'))

    feeds = get_feedlist_for_dropdown(g.user.id)

    return render_template('rss_reader/add_feed.html', feeds=feeds)


@bp.route('/delete_feed', methods=('GET', 'POST'))
@login_required
def delete_feed():

    if request.method == 'POST':

        chosen_feed_title = request.form['FormControlSelect']

        feed_to_be_deleted = Feed.query.filter_by(title=chosen_feed_title).first()
        current_user = get_user_by_id(g.user.id)
        current_user.feeds.remove(feed_to_be_deleted)

        db.session.commit()

        return redirect(url_for('rss_reader.latest'))

    feeds = get_feedlist_for_dropdown(g.user.id)

    return render_template('rss_reader/delete_feed.html', feeds=feeds)
