##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.middleware.locale import LocaleMiddleware
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# SECURITY Settings
# Those settings are mandatory and have to be defined in your .env file
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split()
ADMIN_URL = os.environ['ADMIN_URL']
ENVIRONMENT = os.environ['ENVIRONMENT']
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'


# Base configuration
ROOT_URLCONF = os.environ.get('ROOT_URLCONF', 'backoffice.urls')
WSGI_APPLICATION = os.environ.get('WSGI_APPLICATION', 'backoffice.wsgi.application')
MESSAGE_STORAGE = os.environ.get('MESSAGE_STORAGE', 'django.contrib.messages.storage.fallback.FallbackStorage')
EMAIL_SERVICE_DESK = os.environ.get('EMAIL_SERVICE_DESK', '')


# Application definition
# Common apps for all environments
# Specific apps (all osis modules except base and reference(mandatory) + env specific apps like sentry)
# have to be defined in environment settings (ex: dev.py)
INSTALLED_APPS = (
    'django.contrib.sites',
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'analytical',
    'localflavor',
    'ckeditor',
    'osis_common',
    'reference',
    'rules_management',
    'base',
    'education_group',
    'learning_unit',
    'program_management',
    'statici18n',
    'rest_framework',
    'rest_framework.authtoken',
    'bootstrap3',
    'ordered_model',
    'waffle',
    'ajax_select',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'hijack',
    'compat',
    'hijack_admin',
    'reversion',
    'django.contrib.gis',
    'ddd',
    'infrastructure',
    'osis_document',
    'osis_history',
    'osis_signature',
    'osis_export',
    'osis_notification',
    'osis_async',
    'django_htmx',
)


class CustomLocaleMiddleware(LocaleMiddleware):
    """
        Set default language normally except if there is a query_param equal to 'lang'
    """
    def process_request(self, request):
        language = request.GET.get('lang')
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()
        else:
            super().process_request(request)


MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'backoffice.settings.base.CustomLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'base.middlewares.extra_http_responses_midleware.ExtraHttpResponsesMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'base.middlewares.reversion_middleware.BaseRevisionMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
)


INTERNAL_IPS = ()
# check if we are testing right now
TESTING = 'test' in sys.argv or 'behave_runner' in sys.argv[0]
if TESTING:
    # add test packages that have specific models for tests
    INSTALLED_APPS += ('osis_common.tests', )
    # Speed up test because default hasher is slow by design
    # https://docs.djangoproject.com/en/1.11/topics/testing/overview/#password-hashing
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

# Remove this sh*t! We have inconsistency between module installed and tested
APPS_TO_TEST = (
    'osis_common',
    'reference',
    'rules_management',
    'base',
    'education_group',
    'learning_unit',
    'program_management',
    'ddd',
    'infrastructure',
    'preparation_inscription',
)
TEST_RUNNER = os.environ.get('TEST_RUNNER', 'osis_common.tests.runner.InstalledAppsTestRunner')
SKIP_QUEUES_TESTS = os.environ.get('SKIP_QUEUES_TESTS', 'False').lower() == 'true'
QUEUES_TESTING_TIMEOUT = float(os.environ.get('QUEUES_TESTING_TIMEOUT', 0.1))
TESTS_TYPES = os.environ.get('TESTS_TYPES', 'UNIT')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'base.views.common.common_context_processor',
                'base.context_processors.user_manual.user_manual_url',
                'base.context_processors.settings.virtual_desktop',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

FORMAT_MODULE_PATH = [
    'backoffice.formats',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get("DATABASE_NAME", 'osis_local'),
        'USER': os.environ.get("POSTGRES_USER", 'osis'),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD", 'osis'),
        'HOST': os.environ.get("POSTGRES_HOST", '127.0.0.1'),
        'PORT': os.environ.get("POSTGRES_PORT", '5432'),
        'ATOMIC_REQUESTS':  os.environ.get('DATABASE_ATOMIC_REQUEST', 'True').lower() == 'true'
    },
}

AUTHENTICATION_BACKENDS = os.environ.get('AUTHENTICATION_BACKENDS', 'django.contrib.auth.backends.ModelBackend').split()
PERMISSION_CACHE_ENABLED = os.environ.get('PERMISSION_CACHE_ENABLED', 'True').lower() == 'true'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
# If you want to change the default settings,
# you have to redefine the LANGUAGE_CODE and LANGUAGES vars in environment settings (ex: dev.py)
LANGUAGE_CODE = 'fr-be'
LANGUAGES = [
    ('fr-be', _('French')),
    ('en', _('English')),
]
LANGUAGE_CODE_FR = 'fr-be'
LANGUAGE_CODE_EN = 'en'
# You can change default values for internalizations settings in your .env file
USE_I18N = os.environ.get('USE_I18N', 'True').lower() == 'true'
USE_L10N = os.environ.get('USE_L10N', 'True').lower() == 'true'
USE_TZ = os.environ.get('USE_TZ', 'False').lower() == 'true'
TIME_ZONE = os.environ.get('TIME_ZONE', 'Europe/Brussels')

# Static files (CSS, JavaScript, Images) and Media
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATICI18N_ROOT = os.path.join(BASE_DIR, os.environ.get('STATICI18N', 'base/static'))

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, "uploads"))
MEDIA_URL = os.environ.get('MEDIA_URL',  '/media/')
CONTENT_TYPES = ['application/csv', 'application/doc', 'application/pdf', 'application/xls', 'application/xml',
                 'application/zip', 'image/jpeg', 'image/gif', 'image/png', 'text/html', 'text/plain']
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 5242880))
OSIS_DOCUMENT_BASE_URL = os.environ.get('OSIS_DOCUMENT_BASE_URL', '')

# Logging settings
# Logging framework is defined in env settings (ex: dev.py)
DEFAULT_LOGGER = os.environ.get('DEFAULT_LOGGER', 'default')
SEND_MAIL_LOGGER = os.environ.get('SEND_MAIL_LOGGER', 'send_mail')
QUEUE_EXCEPTION_LOGGER = os.environ.get('QUEUE_EXCEPTION_LOGGER', 'queue_exception')

# Email Settings
# By default Email are saved in the folder defined by EMAIL_FILE_PATH
# If you want ti use the smtp backend,
# you have to define EMAIL_BACKEND, EMAIL_HOST and EMAIL_PORT in your .env if the default values doesn't match.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'osis@localhost.be')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
LOGO_EMAIL_SIGNATURE_URL = os.environ.get('LOGO_EMAIL_SIGNATURE_URL', '')
EMAIL_PRODUCTION_SENDING = os.environ.get('EMAIL_PRODUCTION_SENDING', 'False').lower() == 'true'
COMMON_EMAIL_RECEIVER = os.environ.get('COMMON_EMAIL_RECEIVER', 'osis@localhost.org')
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.filebased.EmailBackend')
EMAIL_FILE_PATH = os.environ.get('EMAIL_FILE_PATH', os.path.join(BASE_DIR, "base/tests/sent_mails"))
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
SEND_BROKEN_LINK_EMAILS = os.environ.get('SEND_BROKEN_LINK_EMAILS', 'True').lower() == 'true'
INTERNAL_EMAIL_SUFFIX = os.environ.get('INTERNAL_EMAIL_SUFFIX', 'osis.org')
MAIL_SENDER_CLASSES = os.environ.get(
    'MAIL_SENDER_CLASSES',
    'osis_common.messaging.mail_sender_classes.MessageHistorySender'
).split()
ACADEMIC_CALENDAR_REMINDER_EMAILS = os.environ.get('ACADEMIC_CALENDAR_REMINDER_EMAILS', '').split()

# Authentication settings
LOGIN_URL = os.environ.get('LOGIN_URL', reverse_lazy('login'))
LOGIN_REDIRECT_URL = os.environ.get('LOGIN_REDIRECT_URL', reverse_lazy('home'))
LOGOUT_URL = os.environ.get('LOGOUT_URL', reverse_lazy('logout'))
OVERRIDED_LOGIN_URL = os.environ.get('OVERRIDED_LOGIN_URL', None)
OVERRIDED_LOGOUT_URL = os.environ.get('OVERRIDED_LOGOUT_URL', None)
PERSON_EXTERNAL_ID_PATTERN = os.environ.get('PERSON_EXTERNAL_ID_PATTERN', 'osis.person_{global_id}')

# Field upload settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ.get('DATA_UPLOAD_MAX_NUMBER_FIELDS', 5000))

# This has to be set in your .env with the actual url where you institution logo can be found.
# Ex : LOGO_INSTITUTION_URL = 'https://www.google.be/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
# A relative URL will work on local , but not out of the box on the servers.
LOGO_INSTITUTION_URL = os.environ.get('LOGO_INSTITUTION_URL',
                                      os.path.join(BASE_DIR, "base/static/img/logo_uclouvain.png"))
LOGO_OSIS_URL = os.environ.get('LOGO_OSIS_URL', '')

# The Queues are optional
# They are used to ensure the migration of Data between Osis and other application (ex : Osis <> Osis-Portal)
# See in settings.dev.example to configure the queues
QUEUES = {}


# Celery settings
CELERY_BROKER_URL = "amqp://{user}:{password}@{host}:{port}".format(
    user=os.environ.get('RABBITMQ_USER', 'guest'),
    password=os.environ.get('RABBITMQ_PASSWORD', 'guest'),
    host=os.environ.get('RABBITMQ_HOST', 'localhost'),
    port=os.environ.get('RABBITMQ_PORT', '5672')
)
CELERY_CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')

# Additionnal Locale Path
# Add local path in your environment settings (ex: dev.py)
LOCALE_PATHS = ()


# Apps Settings
CDN_URL = os.environ.get("CDN_URL", "")
CKEDITOR_JQUERY_URL = os.path.join(STATIC_URL, "js/jquery-2.1.4.min.js")
CKEDITOR_CONFIGS = {
    'minimal': {
        'extraPlugins': ','.join(['pastefromword']),
        'coreStyles_italic': {'element': 'i', 'overrides': 'em'},
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'clipboard', 'items': ['PasteFromWord', '-', 'Undo', 'Redo']},
            ['Format', 'Styles'],
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            {'name': 'insert', 'items': ['Table']},
        ],
        'autoParagraph': False,
    },
    'default': {
        "removePlugins": "stylesheetparser",
        'allowedContent': True,
        'extraPlugins': ','.join(['pastefromword']),
        'coreStyles_italic': {'element': 'i', 'overrides': 'em'},
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'clipboard', 'items': ['PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat']},
            {'name': 'links', 'items': ['Link']},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize', 'Source']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            '/',
            {'name': 'insert', 'items': ['Table']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            {'name': 'about', 'items': ['About']},
        ],
        'autoParagraph': False
    },
    'link_only': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Link', 'Unlink'],
        ],
    },
    'comment_link_only': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Link', 'Unlink'],
        ],
        'height': 75
    },
}

CKEDITOR_CONFIGS['education_group_pedagogy'] = dict(CKEDITOR_CONFIGS['minimal'])

if CDN_URL:
    for config_name in ['education_group_pedagogy']:
        CKEDITOR_CONFIGS[config_name]['extraPlugins'] += ',cdn'
        CKEDITOR_CONFIGS[config_name]['toolbar_Custom'].append({'name': 'cdn_integration', 'items': ['CDN']})
        CKEDITOR_CONFIGS[config_name].update({'customValues': {'cdn_url': CDN_URL}})
        CKEDITOR_CONFIGS[config_name]['allowedContent'] = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'default': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'queue_exception': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'functional': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'send_mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'backoffice.settings.rest_framework.authentication.ESBAuthentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'EXCEPTION_HANDLER': 'backoffice.settings.rest_framework.exception_handler.handle',
    'DEFAULT_PAGINATION_CLASS': 'backoffice.settings.rest_framework.pagination.LimitOffsetPaginationWithUpperBound',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS':	(
        'django_filters.rest_framework.DjangoFilterBackend',  # Allow advanced searching
        'rest_framework.filters.OrderingFilter',  # Allow ordering collections
        'rest_framework.filters.SearchFilter',   # Search based on admin
    ),
}
REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY = os.environ.get('REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY')

# ESB Configuration
ESB_API_URL = os.environ.get('ESB_API_URL')
ESB_AUTHORIZATION = os.environ.get('ESB_AUTHORIZATION')
# TODO: rename to ESB_STUDENT_ENDPOINT
ESB_STUDENT_API = os.environ.get('ESB_STUDENT_API')
ESB_REFRESH_PEDAGOGY_ENDPOINT = os.environ.get('ESB_REFRESH_PEDAGOGY_ENDPOINT')
ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT = os.environ.get('ESB_REFRESH_COMMON_PEDAGOGY_ENDPOINT')
ESB_REFRESH_COMMON_ADMISSION_ENDPOINT = os.environ.get('ESB_REFRESH_COMMON_ADMISSION_ENDPOINT')
ESB_REFRESH_LEARNING_UNIT_PEDAGOGY_ENDPOINT = os.environ.get('ESB_REFRESH_LEARNING_UNIT_PEDAGOGY_ENDPOINT')
ESB_GEOCODING_ENDPOINT = os.environ.get('ESB_GEOCODING_ENDPOINT')
ESB_ENTITIES_HISTORY_ENDPOINT = os.environ.get('ESB_ENTITIES_HISTORY_ENDPOINT')
ESB_ENTITY_ADDRESS_ENDPOINT = os.environ.get('ESB_ENTITY_ADDRESS_ENDPOINT')

RELEASE_TAG = os.environ.get('RELEASE_TAG')

# Selenium Testing
FUNCTIONAL_LOGGER = "functional"
SELENIUM_SETTINGS = {
    'WEB_BROWSER': os.environ.get('SELENIUM_WEB_BROWSER', 'FIREFOX'),
    'GECKO_DRIVER': os.environ.get('SELENIUM_GECKO_DRIVER', "geckodriver"),
    'VIRTUAL_DISPLAY': os.environ.get('SELENIUM_VIRTUAL_DISPLAY', 'False').lower() == 'true',
    'SCREEN_WIDTH': int(os.environ.get('SELENIUM_SCREEN_WIDTH', 1920)),
    'SCREEN_HIGH': int(os.environ.get('SELENIUM_SCREEN_HIGH', 1080)),
    'TAKE_SCREEN_ON_FAILURE': os.environ.get('SELENIUM_TAKE_SCREENSHOTS', 'True').lower() == 'true',
}

# BOOTSTRAP3 Configuration
BOOTSTRAP3 = {
    'set_placeholder': False,
    'success_css_class': '',
    'required_css_class': "required_field",
    "field_renderers": {
            "default": "base.utils.renderers.OsisBootstrap3FieldRenderer",
            "inline": "bootstrap3.renderers.InlineFieldRenderer",
        },
}

# Ajax select is not allowed to load external js libs
AJAX_SELECT_BOOTSTRAP = False


BACKEND_CACHE = os.environ.get("BACKEND_CACHE", "locmem").lower()
if BACKEND_CACHE == 'locmem':
    CACHE_CONFIG = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
elif BACKEND_CACHE == 'redis':
    CACHE_CONFIG = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_LOCATIONS", "redis://127.0.0.1:6379").split(),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 2,
            "SOCKET_TIMEOUT": 2,
            "PASSWORD": os.environ.get("REDIS_PASSWORD", "")
        },
        "KEY_PREFIX": os.environ.get("REDIS_PREFIX", 'osis')
    }
else:
    raise ImproperlyConfigured("Cache configuration error: invalid BACKEND_CACHE")


CACHES = {"default": CACHE_CONFIG}


WAFFLE_FLAG_DEFAULT = os.environ.get("WAFFLE_FLAG_DEFAULT", "False").lower() == 'true'


# HIJACK
HIJACK_LOGIN_REDIRECT_URL = '/'  # Where admins are redirected to after hijacking a user
# Where admins are redirected to after releasing a user
HIJACK_LOGOUT_REDIRECT_URL = "/{admin_url}auth/user".format(admin_url=ADMIN_URL)
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_USE_BOOTSTRAP = True

REQUESTS_TIMEOUT = 20

# PEDAGOGY INFORMATION
URL_TO_PORTAL_UCL = os.environ.get("URL_TO_PORTAL_UCL", "https://uclouvain.be/prog-{year}-{code}")

MINIMUM_SELECTABLE_YEAR = int(os.environ.get("MINIMUM_SELECTABLE_YEAR", 0))
MINIMUM_EDG_YEAR = int(os.environ.get("MINIMUM_EDG_YEAR", 0))
MINIMUM_LUE_YEAR = int(os.environ.get("MINIMUM_LUE_YEAR", 0))

YEAR_LIMIT_LUE_MODIFICATION = int(os.environ.get("YEAR_LIMIT_LUE_MODIFICATION", 0))
YEAR_LIMIT_EDG_MODIFICATION = int(os.environ.get("YEAR_LIMIT_EDG_MODIFICATION", 0))  # By default, no restriction

STAFF_FUNDING_URL = os.environ.get('STAFF_FUNDING_URL', '')
VIRTUAL_DESKTOP_URL = os.environ.get('VIRTUAL_DESKTOP_URL', '')
LEARNING_UNIT_PORTAL_URL = os.environ.get('LEARNING_UNIT_PORTAL_URL', 'https://uclouvain.be/cours-{year}-{code}')

# SITE_ID for Django "sites framework"
SITE_ID = os.environ.get('SITE_ID', 1)

# GIS-related
MAPBOX = {
    'ACCESS_TOKEN': os.environ.get("MAPBOX_ACCESS_TOKEN", ''),
    'CSS_PATHS': os.environ.get(
        "MAPBOX_CSS_PATHS",
        'https://api.mapbox.com/mapbox-gl-js/v1.11.1/mapbox-gl.css',
    ).split(' '),
    'JS_PATHS': os.environ.get(
        "MAPBOX_JS_PATHS",
        'https://api.mapbox.com/mapbox-gl-js/v1.11.1/mapbox-gl.js',
    ).split(' '),
}

LDAP_ACCOUNT_CREATION_URL = os.environ.get("LDAP_ACCOUNT_CREATION_URL", "")
LDAP_ACCOUNT_CONFIGURATION_URL = os.environ.get("LDAP_ACCOUNT_CONFIGURATION_URL", "")
INTERNSHIP_SCORE_ENCODING_URL = os.environ.get("INTERNSHIP_SCORE_ENCODING_URL", "")
CONTINUING_EDUCATION_STUDENT_PORTAL_URL = os.environ.get("CONTINUING_EDUCATION_STUDENT_PORTAL_URL", "")

SCHEDULE_APP_URL = os.environ.get("SCHEDULE_APP_URL", "")
APPLICATION_COURSES_PUBLICATION_DATE = os.environ.get("APPLICATION_COURSES_PUBLICATION_DATE", "")

REGISTRATION_ADMINISTRATION_URL = os.environ.get('REGISTRATION_SERVICE_URL', '')

OSIS_EXPORT_ASYNCHRONOUS_MANAGER_CLS = os.environ.get(
    "OSIS_EXPORT_ASYNCHRONOUS_MANAGER_CLS", "backoffice.settings.osis_export.async_manager.AsyncTaskManager"
)

OSIS_DOCUMENT_API_SHARED_SECRET = os.environ.get("OSIS_DOCUMENT_API_SHARED_SECRET", "")
