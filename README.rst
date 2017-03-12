ActionRising
============

.. note::

    The production version is hosted at `actionrising.com`_.

This project uses Django version 1.10.3 and Python version 2.7. See
documentation in the `docs` directory for a brief
`technical overview`_ for contributors.

Setting up the site locally
---------------------------

.. note::

    These instructions have been tested on Linux (Ubuntu 14.04) and
    OS X 10.12.1.

1. Clone the repository from GitHub.

2. In the top level of the repo, create and activate a `virtualenv`_ called `venv`::

    virtualenv venv
    source venv/bin/activate

3. Install `pip`_ if you don't have it.
   Before installing the requirements, you may need to install the following
   library (which cannot be installed through pip)::

    sudo apt-get install libpq-dev  # ubuntu

   Now you can go ahead and install the rest of the requirements.::

    pip install -r requirements.txt

4. Copy `mysite/local_settings.example` to `mysite/local_settings.py` and edit
   the .py version. There are currently three custom keys you'll need to
   set.  Follow the instructions in that file to figure out which changes to make.

5. Run Django migrations (if needed, should be run the first time or if data
   models change)::

    python manage.py migrate

6. Load the test fixtures to get some fake data::

    python manage.py loaddata fixtures.json

7. Start site::

    python manage.py runserver

8. Open site in browser (see command line output of previous step for correct
   link, usually something like `http://127.0.0.1:8000`__)

9. Remember to run the tests and make sure they're passing before you make any changes::

     python manage.py test

   Consider running coverage on tests as well::

     coverage run manage.py test
     coverage report

.. _actionrising.com: https://actionrising.com
.. _technical overview: https://github.com/shaunagm/actionrising/tree/master/docs/source/technical_overview.md
.. _virtualenv: https://virtualenv.pypa.io/en/stable/userguide/#usage
.. _pip: https://pip.pypa.io/en/stable/installing/
.. __: http://127.0.0.1:8000
