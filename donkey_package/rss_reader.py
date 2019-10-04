from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from werkzeug.exceptions import abort

from donkey_package.auth import login_required
from donkey_package.db import get_db

bp = Blueprint('rss_reader', __name__)


@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT i.id, i.title, i.description, created, f.title as feed_title'
        ' FROM item i JOIN feed f ON i.feed_id = f.id'
        ' JOIN user_feed uf on uf.feed_id = f.id'
        ' JOIN user u on u.id = uf.user_id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('rss_reader/index.html', items=items)


# @bp.route('add_feed', methods=('GET', 'POST'))
# @login_required
# def add_feed():
#     if request.method == 'POST':
