import os

from production_settings import (SECRET_KEY, DEBUG, CHROMEDRIVER_PATH, DATABASES,
    EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD, EMAILS_FAIL_SILENTLY)

# Override production setting, set debug back to true, otherwise should have same settings
DEBUG = True

EMAILS_FAIL_SILENTLY = True
