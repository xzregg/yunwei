#coding:utf-8
from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

autourl=['yw',
#    (r'^test/$','views.test.test'),
    #(r'^zhuce/$',register),
    #(r'^$', requires_login(index)),
    #(r'^login/$', login),
    #(r'^logout/$', logout), 
#    (r'^show/$', requires_login(show,6)),
#     (r'^ws/(?P<path>.*)$','django.views.static.serve',{'document_root':'ws'}),#js和css的静态文件
]

urlpatterns=patterns(*tuple(autourl))


