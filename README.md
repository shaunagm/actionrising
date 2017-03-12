# ActionRising

Note: The production version is hosted at actionrising.com.

This project uses Django version 1.10.3 and Python version 2.7. See documentation in the `docs` directory for a brief
[technical overview](docs/technical_overview.md) for contributors.

## Setting up the site locally

Note: these instructions have been tested on Linux (Ubuntu 14.04) and
OS X (10.12.1 and 10.12.2).

1. [Clone](https://help.github.com/articles/cloning-a-repository/) the repository from GitHub.

1. Install [pip](https://pip.pypa.io/en/stable/installing/) if you don't have it already. 


1. Use pip to install a [virtualenv](https://virtualenv.pypa.io/en/stable/userguide/#usage) called `venv`:

    ```
    pip install virtualenv
    ```

1. Download and install [postgres](https://www.postgresql.org/download/). On OS X, [Postgress.App](http://postgresapp.com/) is recommended. To add Postgress.App to your path, type the following at the command line (be sure to restart your terminal to ensure the path is updated):

    ```
    sudo mkdir -p /etc/paths.d &&
    echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp
    ```

1. Create and activate a virtual env called `venv` that uses python 2.7:

    ```
    virtualenv venv --python=python2.7
    source venv/bin/activate
    ```

1. On Linux, you may need to install the following library (which cannot be installed through pip), before you install the other requirements:

    ```
    sudo apt-get install libpq-dev  # ubuntu
    ```

1. Once the virtualenv has been activated, install the requirements for it:

    ```
    pip install -r requirements.txt
    ```

1. Copy mysite/local_settings.example to mysite/local_settings.py and edit the .py version. There are currently three custom keys you'll need to
set.  Follow the instructions in that file to figure out which changes to make.

1. Run Django migrations (if needed, should be run the first time or if data
  models change). If you get an import error, double check local_settings.py and make sure you are using python2.7 for your virtualenv.

    ```  
    python manage.py migrate
    ```

1. Load the test fixtures to get some fake data:

    ```
    python manage.py loaddata fixtures.json
    ```

1. Start site:

    ```
    python manage.py runserver
    ```

1. Open site in browser (see command line output of previous step for correct
  link, usually something like http://127.0.0.1:8000).

1. Remember to run the tests and make sure they're passing before you make any changes:

    ```
    python manage.py test
    ```

   Consider running coverage on tests as well:

     ```
     coverage run manage.py test
     coverage report
     ```
