# -*- coding: utf-8 -*-
import os
import django


DIRNAME = os.path.dirname(__file__)

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
test_db = os.environ.get('DB', 'sqlite')
if test_db == 'mysql':
    DATABASES['default'].update({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'modeltranslation',
        'USER': 'root',
    })
elif test_db == 'postgres':
    DATABASES['default'].update({
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'NAME': 'modeltranslation',
        'OPTIONS': {
            'autocommit': True,
        }
    })

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.redirects',
    'modeltranslation',
    'modeltranslation.tests',
)
if django.VERSION[0] >= 1 and django.VERSION[1] >= 3:
    INSTALLED_APPS += ('django.contrib.staticfiles',)

STATIC_URL = '/static/'

ROOT_URLCONF = 'modeltranslation.tests.urls'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DIRNAME, 'media/')

SITE_ID = 1

LANGUAGES = (('de', 'Deutsch'),
             ('en', 'English'))
DEFAULT_LANGUAGE = 'de'

SECRET_KEY = 'z5)t*g3003n23lze(&amp;u5)kt&amp;9gtcf)*-o++m2#n-w!qts7u1cj'

MODELTRANSLATION_USE_MULTILINGUAL_MANAGER = True
