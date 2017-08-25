# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
import base64
import logging

from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_limiter import Limiter
from flask_login import current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_webpack import Webpack
from flask_wtf.csrf import CSRFProtect
from raven.contrib.flask import Sentry

from .admin import PyXwordAdmin
from .auth import CustomLoginManager
from .markdown import Markdown

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = CustomLoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
webpack = Webpack()
admin = PyXwordAdmin(db)

limiter = Limiter(
    key_func=lambda: getattr(current_user, 'email', None),
)


@limiter.request_filter
def anonymous_whitelist():
    return not current_user or current_user and current_user.is_anonymous


sentry = Sentry(
    logging=True,
    level=logging.ERROR,
)

markdown = Markdown()


@login_manager.request_loader
def load_user_from_request(request):

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)

        try:
            api_key = base64.b64decode(api_key).decode('utf-8')
            email, password = api_key.split(':', 1)
        except (TypeError, ValueError):
            pass
        else:
            from pyxword_contest.user.models import User
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                return user

    # finally, return None if both methods did not login the user
    return None
