import os
# You can override these to make the site easier to set up, but please don't push
# your changes to the github repo.

# SETTING 1: Django Secret Key
# Option 1: Generate a new secret key and add it to venv/bin/activate with the line
# export DJANGO_SECRET_KEY='$yoursecretkey' (don't forget to restart the venv)
# Option 2: Generate a new secret key and replace 'os.environ['DJANGO_SECRET_KEY']'
# with that key below.

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SETTING 2: PG_DB_PASSWORD
# Option 1: Create a new postgres DB with the name and user indicated below.  Set the
# password in venv/bin/activate with the line export PG_DB_PASSWORD='$your_pg_db_password'
# (don't forget to restart the venv).
# Option 2: Create a new postgres DB with the name and user indicated below.  Set the
# password by replacing 'os.environ['PG_DB_PASSWORD']' below.
# Option 3: If you think you're unlikely to add or change models, you can use a different
# backend like sqlite.  For help, see https://docs.djangoproject.com/en/1.10/ref/settings/#databases

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
# Option 1: If you want to interact with emails at all, contact Shauna to get the API
# key and set it via venv/bin/activate or directly below.
# Option 2: If you will not be interacting with email, replace with:
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# (You should be able to delete/comment out 'EMAIL_HOST_PASSWORD')
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD =  os.environ['SPARKPOST_API_KEY']

# SETTING 4: DEBUG
# Sets debug to true for devel and stage, but leaves it off for production
if os.environ.get('IS_PRODUCTION_SITE') and os.environ.get('IS_PRODUCTION_SITE') == "True":
    DEBUG = False
else:
    DEBUG = True
