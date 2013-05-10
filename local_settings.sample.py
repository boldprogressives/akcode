# AKCODE_GIT_REPO = 'user@git-server.com:repository'

# Make this unique, and don't share it with anybody.
# SECRET_KEY = 'secret!'

import os
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'default.db'),
        'USER': '',                     
        'PASSWORD': '',                 
        'HOST': '',                     
        'PORT': '',                     
    },
    'ak': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'actionkit_db_name',
        'USER': 'actionkit_db_user',
        'PASSWORD': 'actionkit_db_password',
        'HOST': 'client-db.actionkit.com',
        'PORT': '',
        },    
    }

ACTIONKIT_API_HOST = 'https://act.my-domain.com'
ACTIONKIT_API_USER = 'api_user'
ACTIONKIT_API_PASSWORD = 'api_password'

LOCAL_MIDDLEWARE_CLASSES = (
    "djangohelpers.middleware.AuthRequirementMiddleware",
)
ANONYMOUS_PATHS = (
    "/static/",
    "/admin/",
    "/accounts/",
    )

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
