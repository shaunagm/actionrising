ActionRising
============

.. note::

    The production version is hosted at `actionrising.com`_.

This project uses Django version 1.10.3 and Python version 2.7.
For contributor guidelines, see our `contributor overview`_.

Setting up the site locally
---------------------------

.. note::

    These instructions have been tested on Linux (Ubuntu 14.04) and
    OS X 10.12.1.

#. `Clone`_ the repository from GitHub.

#. Install `pip`_ if you don't have it. On Linux, you may need to install the
   following library (which cannot be installed through pip)::

    sudo apt-get install libpq-dev  # ubuntu

#. Use pip to install `virtualenv`_::

    pip install virtualenv

#. Download and install `postgres`_. On OS X, the
   `Postgres.App`_ is recommended. To add
   Postgres.App to your path, type the following at the command line
   (be sure to restart your terminal to ensure the path is updated)::

    sudo mkdir -p /etc/paths.d &&
    echo /Applications/Postgres.app/Contents/Versions/latest/bin |
      sudo tee /etc/paths.d/postgresapp

#. Create and activate a virtual env called `venv` that uses python 2.7::

    virtualenv venv --python=python2.7
    source venv/bin/activate

#. Once the virtualenv has been activated, install the requirements::

    pip install -r requirements.txt

#. Copy `mysite/local_settings.example` to `mysite/local_settings.py` and edit
   the .py version. There are currently three custom keys you'll need to
   set.  Follow the instructions in that file to figure out which changes to make.

#. Run Django migrations (if needed, should be run the first time or if data
   models change). If you get an import error, double check `local_settings.py`
   and make sure you are using python2.7 for your virtualenv.::

    python manage.py migrate

#. Load the test fixtures to get some fake data::

    python manage.py loaddata fixtures.json

#. Create a database table for `caching`_ ::

    python manage.py createcachetable

#. Start site::

    python manage.py runserver

#. Open site in browser (see command line output of previous step for correct
   link, usually something like `http://127.0.0.1:8000`__).

#. Remember to run the tests and make sure they're passing before you make any changes::

     python manage.py test

   Consider running coverage on tests as well::

     coverage run manage.py test
     coverage report

.. _actionrising.com: https://actionrising.com
.. _Clone: https://help.github.com/articles/cloning-a-repository/
.. _contributor overview: https://github.com/shaunagm/actionrising/blob/master/CONTRIBUTING.md
.. _virtualenv: https://virtualenv.pypa.io/en/stable/userguide/#usage
.. _postgres: https://www.postgresql.org/download/
.. _Postgres.App: http://postgresapp.com/
.. _pip: https://pip.pypa.io/en/stable/installing/
.. _caching: https://docs.djangoproject.com/en/1.11/topics/cache/#database-caching
.. __: http://127.0.0.1:8000
