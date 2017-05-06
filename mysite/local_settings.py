import os
# Copy this file to local_settings.py and edit it according to the instructions.
# This example file is tracked in the github repo but your actual settings are git-ignored
# and should not be added to the repo.

# SETTING 1: Django Secret Key
# 1. Generate a new secret key. Don't use the Django command for this; you can use a site like http://www.miniwebtool.com/django-secret-key-generator/.
# 2. Either
#    a. add it to venv/bin/activate with the line
#       export DJANGO_SECRET_KEY='$yoursecretkey', then deactivate and activate your venv
#    or
#    b. replace os.environ['DJANGO_SECRET_KEY'] in this file with your key.

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SETTING 2: PG_DB_PASSWORD
# (If you think you're unlikely to add or change models, you can use a different
# backend like sqlite instead of following these instructions.
# For help, see https://docs.djangoproject.com/en/1.10/ref/settings/#databases)
# 1. Download and connect to PostgreSQL.
# 2. Create a new superuser named actnowadmin.
# 3. Create a database called actnowdb.
# 4. Make up a password and either
#    a. add it to venv/bin/activate with the line
#       export PG_DB_PASSWORD='$your_pg_db_password', and reactivate your venv
#    or
#    b. replace os.environ['PG_DB_PASSWORD'] below with the password

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'actnowdb',
        'USER': 'actnowadmin',
        'PASSWORD': os.environ['PG_DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# SETTING 3: SPARKPOST_API_KEY
# Use these settings if you won't be interacting with email.
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_PASSWORD = ''
# If you do want to interact with emails, contact Shauna to get the API
# key and set it via venv/bin/activate or directly below.
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD =  os.environ['SPARKPOST_API_KEY']

# SETTING 4: DEBUG
# Sets debug to true for devel and stage, but leaves it off for production
if os.environ.get('IS_PRODUCTION_SITE') and os.environ.get('IS_PRODUCTION_SITE') == "True":
    DEBUG = False
else:
    DEBUG = True

# SETTING 5:
# The tests need the path to your global chromedriver rather than the virtualenv one.
# You may need to change this path if your chromedriver is in a different location.

CHROMEDRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
