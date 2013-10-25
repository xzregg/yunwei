#coding:utf-8
from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

autourl=['filemanage',
#    (r'^test/$','views.test.test'),

]

urlpatterns=patterns(*tuple(autourl))


