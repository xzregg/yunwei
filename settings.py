# coding:utf-8
# Django settings for yunwei project.
import os
import sys
import MySQLdb
import traceback

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PWD = os.path.dirname(os.path.realpath(__file__)) + os.sep
sys.path.insert(1, os.path.join(PWD, 'libs'))


Title = u'YW-运维管理'
UploadDir = 'uploads'
AbsUploadDir = os.path.join(PWD, UploadDir)
FileManagerChroot = UploadDir

SessionTimeout = 120000  # seconds
LoginFailNums = 10
LonginAgainSec = 60  # seconds

DefaultShow = ['ADMIN系统', '查看日志', '运维系统', '文件管理', '查看一键']

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


d1 = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'
        # or 'oracle'.
        'ENGINE': 'mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'yunwei',
        'USER': 'root',					  # Not used with sqlite3.
                'PASSWORD': '123456',				  # Not used with sqlite3.
                # Set to empty string for localhost. Not used with sqlite3.
                'HOST': 'localhost',
        'PORT': '3306',
        # Set to empty string for default. Not used with sqlite3.
                'unix_socket': '/tmp/mysql.sock'
    },
}
d2 = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'
        # or 'oracle'.
        'ENGINE': 'sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': PWD + 'yunwei.db',
        'USER': '',					  # Not used with sqlite3.
                'PASSWORD': '',				  # Not used with sqlite3.
                # Set to empty string for localhost. Not used with sqlite3.
                'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
                'PORT': '',
    }
}

try:
    d = d1['default']
    conn = MySQLdb.connect(host=d['HOST'], port=int(
        d['PORT']), user=d['USER'], passwd=d['PASSWORD'], db=d['NAME'])
    DATABASES = d1

except:
    # traceback.print_exc()
    DATABASES = d2
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/adminmedia/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!lr!u)3vek=g%&$%*ay8nnra%w-0#vasm7l+&0zz8&g9a6wy!s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',#从egg文件中加载模板，egg文件类似jar包
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #	'django.middleware.csrf.CsrfViewMiddleware',
    #	'django.middleware.csrf.CsrfResponseMiddleware',
    #	'django.contrib.auth.middleware.AuthenticationMiddleware',
    #	'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.gzip.GZipMiddleware',
    'middleware.gzip.GZipMiddleware'
)

ROOT_URLCONF = 'urls'


# webssh代理设置
PROXY_DOMAIN = "127.0.0.1"
# PROXY_DOMAIN='www.baidu.com'
PROXY_PORT = 7001
PROXY_USER = 'user'
PROXY_PASSWORD = 'passwd'

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
    'admin',
    'filemanager',
    #   'south',
)


import platform
if platform.system() == "Linux":
    INSTALLED_APPS += ('yw',)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__),
                 'templates').replace('\\', '/'),
    # os.path.join(os.path.dirname(__file__),'media').replace('\\','/'),
)

Menu = {u'其他': [
    ['http://www.google.com', u'谷歌'],
    ['http://www.baidu.com/', u'百度'],
]

}


def djangoReload():
    f = open('reload.py', 'w')
    print>>f, ''
    f.close()
