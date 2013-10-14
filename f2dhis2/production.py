from settings import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['f2dhis2.ona.io']


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