#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DataCenter.wsgi")
#=========================================================================
#=========================================================================
import os
import sys
import time
import datetime
from django.core.handlers.wsgi import WSGIHandler


if not os.path.dirname(__file__) in sys.path[:1]:
    sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

application = WSGIHandler()

from django.utils import autoreload
from uwsgidecorators import rbtimer
import uwsgi
import time

# 自动重载入


@rbtimer(3)
def change_code_gracefull_reload(sig):
    if autoreload.code_changed():
        print 'reload now [%s]' % time.strftime('%Y-%m-%d %T', time.localtime(time.time()))
        uwsgi.reload()
    else:
        pass
        # print 'not reload [%s]' % time.strftime('%Y-%m-%d
        # %T',time.localtime(time.time()))
