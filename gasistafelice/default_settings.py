# Django settings for gasistafelice project.

from django.utils.translation import ugettext_lazy as _

import os 

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
VERSION = __version__ = file(os.path.join(PROJECT_ROOT, 'VERSION')).read().strip()

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '26lk413y7^-z^t$#u(xh4uv@+##0jh)&_wxzqho655)eux33@k'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'gasistafelice.middleware.ResourceMiddleware',
)

ROOT_URLCONF = 'gasistafelice.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + "/rest/templates",
    PROJECT_ROOT + "/templates",
)

INSTALLED_APPS = (
    'permissions',
    'workflows',
    'history',
    'gasistafelice.auth',
    'gasistafelice.base',
    'gasistafelice.accounting',
    'gasistafelice.supplier',
    'gasistafelice.gas',
     #'gasistafelice.admin',
     #'gasistafelice.gas_admin',
     #'gasistafelice.rest',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'gasistafelice.des',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.comments',
    #'south',
    
)

URL_PREFIX = "gasistafelice/"

RESOURCE_PAGE_BLOCKS = {
    'site' : [{
        'name' : 'info',
        'descr' : 'Generale',
        'blocks' : ['details', 'gas_list', 'supplier_list']
    }],
    'gas' : [{
        'name' : 'open_orders',
        'descr': 'Ordini aperti',
        'blocks': ['open_orders'],
    },{
        'name' : 'ordered_products',
        'descr': 'Prodotti ordinati',
        'blocks': [],
    }],
    'supplier' : [{
        'name' : 'products',
        'descr': 'Prodotti',
        'blocks': [],
    },{
        'name' : 'info',
        'descr': 'Generale',
        'blocks': [],
    }],
}
   
LOGIN_URL = "/%saccounts/login/" % URL_PREFIX
CAN_CHANGE_CONFIGURATION_VIA_WEB = False
ENABLE_OLAP_REPORTS = False

######################################################################################
# Accounting-related settings
ACCOUNT_TYPES = [
    ('ROOT', _('Root account')),
    ('INCOME', _('Incomes')),
    ('EXPENSE', _('Expenses')),
    ('ASSET', _('Asset')),
    ('LIABILITY', _('Liability')),
    ('INVOICES', _('Invoices')),
]

TRANSACTION_TYPES = [
    ('SUPPLIER_ORDER_PAYMENT', _('Payment of an order to a supplier')),
    ('RECHARGE', _('Recharge of a GAS member account')),
    ('GASMEMBER_ORDER_PAYMENT', _('Payment of an order from a GAS member')),
    ('MEMBERSHIP_FEE_PAYMENT', _('Payment of a membership fee')),   
]
