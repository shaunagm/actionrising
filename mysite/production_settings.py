import os

# SETTING 1: Django Secret Key
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# SETTING 2: PG_DB_PASSWORD
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
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD =  os.environ['SPARKPOST_API_KEY']

# SETTING 4: DEBUG
DEBUG = False

# SETTING 5:
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
