# ActionRising

Note: The production version is hosted at actionrising.com.

This project uses Django version 1.10.3. See documentation in the `docs` directory for a brief
[technical overview](docs/technical_overview.md) for contributors.

## Setting up the site locally

Note: these instructions have been tested on Linux (Ubuntu 14.04) and
OS X 10.12.1.

1) Clone the repository from GitHub

2) Inside the repo, create and activate a [virtualenv](https://virtualenv.pypa.io/en/stable/userguide/#usage) called `venv`

3) Install the requirements

    pip install -r requirements.txt

4) Go to mysite/local_settings.py.  There are currently three custom keys you'll need to
set.  Follow the instructions in that file to figure out which changes to make.

5) Run Django migrations (if needed, should be run the first time or if data
  models change)

    python manage.py migrate

6) Load the test fixtures to get some fake data:

    python manage.py loaddata fixtures.json

7) Start site

    python manage.py runserver

8) Open site in browser (see command line output of previous step for correct
  link, usually something like http://127.0.0.1:8000)

9) Remember to run the tests and make sure they're passing before you make any changes:

     python manage.py test

   Consider running coverage on tests as well:

     coverage run manage.py test
     coverage report
