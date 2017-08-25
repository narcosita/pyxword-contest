# -*- coding: utf-8 -*-
"""Create an application instance."""
import importlib
import os

from flask.helpers import get_debug_flag

from pyxword_contest.app import create_app


def import_string(name):
    module_name, attr_name = name.rsplit('.', 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, attr_name)


config_factory_name = os.environ.get('PYXWORD_SETTINGS')
if not config_factory_name:
    config_factory_name = (
        'DevConfig' if get_debug_flag() else 'ProdConfig'
    )

if '.' not in config_factory_name:
    config_factory_name = f'pyxword_contest.settings.{config_factory_name}'

config_factory = import_string(config_factory_name)


CONFIG = config_factory()

app = create_app(CONFIG)
