# -*- coding: utf-8 -*-
# Django settings for openshift project.
import imp, os
import sys

# a setting to determine whether we are running on OpenShift
ON_OPENSHIFT = False
if os.environ.has_key('OPENSHIFT_REPO_DIR'):
    ON_OPENSHIFT = True

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
if ON_OPENSHIFT:
    DEBUG = False
    ALLOWED_HOSTS = ['.stables.fi', 'stables-alitur.rhcloud.com']
    SESSION_COOKIE_DOMAIN='.stables.fi'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    ALLOWED_HOSTS = ['.localhost',]
    SESSION_COOKIE_DOMAIN=''
    DEBUG_TOOLBAR_CONFIG = { 'INTERCEPT_REDIRECTS': False }
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    SOUTH_MIGRATION_MODULES = {
        'easy_thumbnails': 'easy_thumbnails.south_migrations',
    }
    MERCHANT_ID="13466"
    MERCHANT_PASS="6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ"
    TEST_SMS="+358447671369"

ADMINS = (
    ('Juho Rutila', 'juho.rutila@sandis.fi'),
)
MANAGERS = ADMINS

AUTH_PROFILE_MODULE = 'stables.UserProfile'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'tenant.backends.MasterUserBackend')
SESSION_ENGINE='tenant.session.public'

if ON_OPENSHIFT:
    # os.environ['OPENSHIFT_MYSQL_DB_*'] variables can be used with databases created
    # with rhc cartridge add (see /README in this git repo)
    DATABASES = {
        'default': {
            'ENGINE': 'tenant_schemas.postgresql_backend', 
            'NAME': os.environ.get('PGDATABASE'),
            'USER': os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
            'PASSWORD': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
            'HOST': '',
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            #'ENGINE': 'tenant_schemas.postgresql_backend', 
            'ENGINE': 'tenant_schemas.postgresql_backend'
                if not 'test' in sys.argv else 'django.db.backends.sqlite3',
            'NAME': 'talli',
            'USER': 'talli',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fi'
LANGUAGES = [ ('fi', 'Finnish'), ]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
  os.path.join(PROJECT_DIR, 'locale'),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.environ.get('OPENSHIFT_DATA_DIR', '')
if not ON_OPENSHIFT:
    MEDIA_ROOT = os.path.join(PROJECT_DIR, '..', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, '..', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'djangobower.finders.BowerFinder',
)

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_DIR, '..', 'components')

BOWER_INSTALLED_APPS = (
        'momentjs#2.7.0',
        'underscore#1.6.0',
        'jquery-slugify#1.0.3',
        'bootstrap#3.2.0',
        'jquery-validate#1.13.0'
        )

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

# Make a dictionary of default keys
default_keys = { 'SECRET_KEY': 'vm4rl5*ymb@2&d_(gc$gb-^twq9w(u69hi--%$5xrh!xk(t%hw' }

# Replace default keys with dynamic values if we are in OpenShift
use_keys = default_keys
if ON_OPENSHIFT:
    imp.find_module('openshiftlibs')
    import openshiftlibs
    use_keys = openshiftlibs.openshift_secure(default_keys)

# Make this unique, and don't share it with anybody.
SECRET_KEY = use_keys['SECRET_KEY']

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'tenant_schemas.middleware.TenantMiddleware',
    'django.middleware.common.CommonMiddleware',
    'middleware.TimezoneMiddleware',
    # Enable when adding more languages
    #'django.middleware.locale.LocaleMiddleware',
    #'babeldjango.middleware.LocaleMiddleware',
    'solid_i18n.middleware.SolidLocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'tenant.middleware.AuthenticationMiddleware',
    'tenant.middleware.RestrictTenantStaffToAdminMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'middleware.LoginRequiredMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
)

LOGIN_EXEMPT_URLS = (r'^api/', r'^shop/' )

if not ON_OPENSHIFT:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INTERNAL_IPS = ('127.0.0.1',)

#ROOT_URLCONF = 'openshift.urls'
ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

CMS_TEMPLATES = (
        ('public/cms_template.html', 'Basic template'),
        ('public/features_template.html', 'Features page'),
        ('public/pricing_template.html', 'Pricing page'),
        ('public/frontpage_template.html', 'Frontpage'),
        ('public/contact_template.html', 'Contact page'),
        ('public/feature.html', 'Feature template'),
        ('public/pricing_option.html', 'Pricing template (under pricing page)'),
        ('public/testimonial.html', 'Testimonial template'),
        ('public/slider.html', 'Slider template'),
)

CMSPLUGIN_CONTACT_FORMS = (
        #('cmsplugin_contact.forms.ContactForm', 'default'),
        ('public.forms.ContactForm', 'Contact form'),
)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    'django.contrib.messages.context_processors.messages',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
)

LOGIN_REDIRECT_URL = '/'

PUBLIC_SCHEMA_URLCONF = 'public.urls'

SHARED_APPS = (
    'tenant',

    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',

    'south',

    'mptt',
    'rest_framework',
    'sekizai',
    'crispy_forms',

    'backbone_tastypie',
    'corsheaders',

    'cms',
    'cms.plugins.text',
    'cms.plugins.link',

    'cmsplugin_filer_image',
    'filer',
    'easy_thumbnails',

    'cmsplugin_contact',

    'menus',
    'reversion',

    'public',
    'djangobower',
    'django_twilio',
)

TENANT_APPS = (
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',

    # TODO: Deprecation warning: Django 1.6
    'fluent_comments',
    'django.contrib.comments',

    'grappelli.dashboard',
    'grappelli',

    'south',

    'stables',
    'schedule',
    'reversion',
    'reportengine',

    'shop',
    #'shop.addressmodel',
    'stables_shop',

    'django_settings',
)

INSTALLED_APPS = SHARED_APPS + TENANT_APPS + ('tenant_schemas', )

if not ON_OPENSHIFT:
    INSTALLED_APPS = INSTALLED_APPS + ('devserver', 'debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
      'JQUERY_URL':'',
    }

if 'test' in sys.argv:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'south']

TENANT_MODEL = 'tenant.Client'

SOUTH_DATABASE_ADAPTERS = {
    'default': 'south.db.postgresql_psycopg2',
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

SHOP_SHIPPING_BACKENDS = ['stables_shop.backends.DigitalShipping',]
SHOP_PAYMENT_BACKENDS = ['stables_shop.backends.PayTrailBackend', 'shop.payment.backends.prepayment.ForwardFundBackend']
SHOP_CART_MODIFIERS = ['stables_shop.modifiers.FixedVATRate',]
SHOP_PRODUCT_MODEL = ('stables_shop.product.Product', 'stables_shop')
SHOP_ADDRESS_MODEL = 'stables_shop.addressmodel.Address'
from decimal import Decimal
SHOP_VAT = Decimal('0.10')

PAYMENTLINK_METHOD = 'stables_shop.models.get_short_url_for'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s',
            }
        },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if DEBUG and not ON_OPENSHIFT:
    LOGGING['loggers']['django'] = {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        }
    LOGGING['handlers']['logfile'] = {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/tmp/django.log',
        }
