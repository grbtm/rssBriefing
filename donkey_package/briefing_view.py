from flask import Blueprint, g, render_template

from donkey_package.auth import login_required
from donkey_package.db import get_db
from donkey_package.briefing_model import briefing

bp = Blueprint('briefing', __name__)


@bp.route('/')
@login_required
def index():

    db = get_db()

    latest_date_row_obj = db.execute(
        'SELECT max(briefing_created)'
        ' FROM briefing b'
        ' WHERE b.user_id = ?', (g.user['id'],)
    ).fetchone()

    latest_date = latest_date_row_obj['max(briefing_created)']

    items = db.execute(
        'SELECT b.title, b.description, b.link, b.reference, b.score, b.feed_title'
        ' FROM briefing b'
        ' WHERE (b.user_id = ? AND b.briefing_created = ?)', (g.user['id'], latest_date)
    ).fetchall()

    feeds = db.execute(
        'SELECT feed.id, title'
        ' FROM feed'
    ).fetchall()

    return render_template('briefing/index.html', items=items, feeds=feeds)
