from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from werkzeug.exceptions import abort

from donkey_package.auth import login_required
from donkey_package.db import get_db


bp = Blueprint('rss_reader', __name__)

@bp.route('/')
def index():
    db = get_db()

