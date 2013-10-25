#coding:utf-8


import sys,os
import time

f=os.path.dirname
ProjectsDir=f(f(sys.path[0]))#项目路径
sys.path.append(ProjectsDir)


os.environ['DJANGO_SETTINGS_MODULE'] ='settings'
from django.core.management import setup_environ
import settings
setup_environ(settings)

from yw.Global import *
from yw.models import  hosts,hostgroup,scripts
from yw.core.ssh import Host
from yw.core.bf import xBF


_concurrency=ConcurrencyNums
#处理ssh的返回
def GetShellRet(Func,shellarrtuple):
	c,s,t=Func(*shellarrtuple)
	if c==0:
		return s
	else:
		return '\033[31m%s\033[0m\n'%s
def BFShell(func,hostsobjs,bfn,timeout,shellarrtuple,printret=True):
	a=xBF(None,[],bfn=bfn,printret=printret)
	for o in hostsobjs:
		hostobj=Host(o.ip,o.port,o.user,o.password,o.sshtype,timeout)
		Func=getattr(hostobj,func)
		a.append(GetShellRet,(Func,shellarrtuple))
	a.start(True)
	
def RunScript(hostsobjs,Script):
			if not os.path.isfile(Script.split(' ')[0]):
				ScriptAbsPath=scripts.GetScriptPath(Script,TmpScript=False)
			else:
				ScriptAbsPath=os.path.join(os.getcwd(),Script)
			return BFShell('RunScript',hostsobjs,_concurrency,10,(True,ScriptAbsPath))
	
def	RunCMD(hostsobjs,CMD):
		BFShell('RunCMD',hostsobjs,_concurrency,10,(True,CMD))

def SetPublicKey(hostsobjs):
		BFShell('SetPublicKey',hostsobjs,30,10,())

def ShowTarget(hostsobjs=[]):
	print 'HostGroups:\n',
	for i,g in enumerate(hostgroup.GetHostGroup()):
		print '%s.[%s]'%(i+1,g),
	if hostsobjs:
		print '\n'
		for i,o in enumerate(hostsobjs):
			print '<%s>'%(i+1),o.alias,o.ip,o.port,o.user,o.group,o.describe
		print '\n','-'*10,u'目标\033[31m (%s)\033[0m个.'%len(hostsobjs),'-'*10
		
def ShowScript():
		d={}
		for o in scripts.objects.all():
			d.setdefault(o.scriptgroup,[])
			d[o.scriptgroup].append(o.scriptname)
		for k,v in d.iteritems():
			print '[%s]'%k
			for i,s in enumerate(v):
				print '\t%s. %s'%(i+1,s)
			
def main():
	from optparse import OptionParser 
	parser = OptionParser()  			
	parser.add_option("-H", "--host", dest="host", default='',
						help="Connect to host",metavar='')				
	parser.add_option("-g", "--group", dest="group", default='',
						help="Connect to host",metavar='')  
	parser.add_option("-c", "--cmd", dest="cmd", default='',
						help="run cmd",metavar='')					
	parser.add_option("-s", "--script", dest="script", default='',
						help="run script | -s show will show scripts",metavar='') 				
	parser.add_option("-l", "--list", dest="show",action = "store_true",
						help="print target")
	parser.add_option("-b", "", dest="concurrency",default = 100,
						help="Concurrency nums")					
	parser.add_option("", "--setPub", dest="setpub",action = "store_true",
						help="setting PublicKey")
			
	(o, args) = parser.parse_args()
	if o.concurrency:
		global _concurrency
		_concurrency=150 if int(o.concurrency)<200 else o.concurrency
		
		
	TarGet=[]
	HorG=o.host or o.group
	TarGet=hosts.GetHostObjs([],HorG)

	if o.show:
		if o.script=='show':
			ShowScript()#列出脚本
		else:
			ShowTarget(TarGet)#列出目标
	elif o.setpub and TarGet:
		SetPublicKey(TarGet)
	elif o.script and TarGet:
		RunScript(TarGet, o.script)
	elif o.cmd and TarGet:
		RunCMD(TarGet,o.cmd)
	else:
		parser.print_help()

	
if __name__=="__main__":
	main()




