# actnow

This project uses Django version 1.10.3.

## Setting up the site locally

Note: these instructions have been tested on Linux (Ubuntu 14.04) and
OS X 10.12.1.

1) Clone the repo from GitHub

2) Create and activate a [virtualenv](https://virtualenv.pypa.io/en/stable/userguide/#usage)

3) Install requirements

    pip install -r requirements.txt

4) Run Django migrations (if needed, should be run the first time or if data
  models change)

    python manage.py migrate

5) Load the test fixtures to get some fake data:

    python manage.py loaddata fixtures.json

6) Start site

    python manage.py runserver

7) Open site in browser (see command line output of previous step for correct
  link, usually something like http://127.0.0.1:8000)

8) Remember to run the tests and make sure they're passing before you make any changes:

     python manage.py test
