from flask import Blueprint, g, render_template

from donkey_package.auth import login_required
from donkey_package.db import get_db
from donkey_package.models import briefing

bp = Blueprint('briefing', __name__)


@bp.route('/')
@login_required
def index():

    briefing.generate_briefing(user_id=g.user['id'])
    import time
    time.sleep(5)

    db = get_db()
    items = db.execute(
        'SELECT b.title, b.description, b.link, b.reference, b.score, b.feed_title'
        ' FROM briefing b'
#        ' WHERE b.user_id = ?', (g.user['id'],)
    ).fetchall()
    feeds = db.execute(
        'SELECT feed.id, title'
        ' FROM feed'
        ' JOIN user on user.id = feed.user_id'
        ' WHERE user.id = ?', (g.user['id'],)
    ).fetchall()
    return render_template('briefing/index.html', items=items, feeds=feeds)
