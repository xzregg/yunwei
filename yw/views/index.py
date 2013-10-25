#coding:utf-8

from ..Global import *


	
def YWSystem(request):
	'''
	运维系统
	'''
	TabUrl=[['/yw/hosts/HostsManage/',u'主机管理'],
			['/yw/hosts/HostGroupManage/','主机组管理'],
			['/yw/scripts/ScriptsManage/','脚本管理'],
			['/yw/onekey/OneKeyManage/','一键管理'],
			]
	return render_to_response('showtab.html',locals())
	
	
