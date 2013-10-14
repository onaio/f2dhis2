from settings import *


TIME_ZONE = 'Africa/Nairobi'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
CELERY_ALWAYS_EAGER = True

# DB name is set to f2dhis2 by default or f2dhis2_test if testing
if not TESTING_MODE:
    DATABASE_NAME = "f2dhis2_dev"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DATABASE_NAME,
        'USER': 'root',
        'PASSWORD': ''
    }
}

FH_OAUTH_CLIENT_ID = "aPQSVp@k_2-vD@OTHbw4aAf!znmwZsTQvf1cdhj0"
FH_OAUTH_CLIENT_SECRET = "=I8!obkuA4.Rec1up-LsGcySI=pN5@!ZpyXSC=YRTT.53@FHaT1K98lYQWy5SyZ;aq348PSbY2=46qjzzEjyv5ep=lXTB:1LL4LVBfJ1x.PTnQEm5yE5JsiYBKD!PINU"

FH_SERVER_URL = "https://dev.formhub.org"
FH_OAUTH_REDIRECT_URL = "http://localhost:8000/oauth"
FH_OAUTH_VERIFY_SSL = False
