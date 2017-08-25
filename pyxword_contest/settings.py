# -*- coding: utf-8 -*-
"""Application configuration."""
import os

import raven


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('PYXWORD_CONTEST_SECRET')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'
    RATELIMIT_APPLICATION = '100/minute'

    SENTRY_CONFIG = {
        'dsn': None,
        'release': raven.fetch_git_sha(os.path.dirname(APP_DIR)),
    }
    SENTRY_USER_ATTRS = [
        'display_name',
        'email',
    ]

    # APPLICATION SPECIFIC
    GLOSSARY_PATH = os.path.abspath(os.path.join(
        PROJECT_ROOT, 'fixtures/glossaries/cpython36_almost_all.yaml'
    ))


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/pyxword'
    DEBUG_TB_ENABLED = False
    SENTRY_CONFIG = dict(Config.SENTRY_CONFIG)
    SENTRY_CONFIG['environment'] = 'production'


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SECRET_KEY = 'no-so-secret-dev-secret'


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
    SECRET_KEY = 'no-so-secret-dev-secret'
    RATELIMIT_ENABLED = False
