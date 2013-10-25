#coding:utf-8
#定义全局
#

from django.http import HttpResponseRedirect
from django.http import HttpResponse,Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
import sys,os,time,re
from libs.html import *
from libs.timelib import *
from .core.ssh import Host


#定义全局变量
ConcurrencyNums=150
ScriptDir=os.path.join(os.path.dirname(__file__),'shellscript')
FileObjectsDir=os.path.join(os.path.dirname(__file__),'fileobjects')

WebSSHAddress='127.0.0.1:7001'
WebSSHFormat='''<a href="javascript:viod(0);" onclick="window.open ('%s',Math.round(Math.random()*1000000000),'height=400,width=500,scrollbars=no')" >%s</a>'''

def CreateDir(path=[]):
	for d in path:
		if not os.path.isdir(d) and not os.path.isfile(d):
			#print 'create %s'%d
			os.mkdir(d)
		#print '%s exists!'%d
CreateDir([ScriptDir,FileObjectsDir])
