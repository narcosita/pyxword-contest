===============================
pyxword-contest
===============================

Python crossword contest app.


Development quickstart
----------

Gotta use Python 3.6 or newer.
Run the following commands to bootstrap your environment ::

    pip install -r requirements/dev.txt
    npm install
    npm start  # run the webpack dev server and flask server using concurrently

In general, before running shell commands, set the ``FLASK_APP`` and
``FLASK_DEBUG`` environment variables ::

    export FLASK_APP=autoapp.py
    export FLASK_DEBUG=1

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration ::

    flask db init
    flask db migrate
    flask db upgrade

Custom Config
-------------

Create ``local.py`` ::

    from pyxword_contest.settings import DevConfig


    class LocalConfig(DevConfig):
        SQLALCHEMY_DATABASE_URI = 'postgresql://pyxword:secret@localhost/pyxword'

and to use it .. code-block::

    export PYXWORD_SETTINGS=local.LocalConfig

Deployment
----------

You first want to setup custom config mentioned, with small differences ::

    from pyxword_contest.settings import ProdConfig


    class LocalProdConfig(ProdConfig):
        SQLALCHEMY_DATABASE_URI = 'postgresql://pyxword:secret@localhost/pyxword'
        SECRET_KEY = REPLACE_ME_WITH_SOME_SUPER_SECRET_STRING_LITERAL

        SENTRY_CONFIG = dict(ProdConfig.SENTRY_CONFIG)
        SENTRY_CONFIG['dsn'] = None # replace this if you want sentry


Then to deploy ::

    export PYXWORD_SETTINGS=local.LocalProdConfig
    npm run build   # build assets with webpack
    flask run       # start the flask server


Contest setup
-------------

First create a admin account by using command ::

    flask createsuperuser

You can access admin panel under http://localhost:5000/funadmin/ .
This is mostly a debug tool, but still you can do stuff with it and maybe you won't break the system.

To load supplied crosswords into database use ::

    flask crossword load fixtures/crosswords/

Handy commands:
-----

.. code-block:: bash

    flask shell # opens the interactive shell
    flask test # runs all tests

    # perform database upgrade (migrate all tables)
    flask db upgrade
