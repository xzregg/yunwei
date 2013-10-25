#coding:utf-8


from ..Global import *

def test1(request):
		'''
		测试
		'''
		text=request.POST.get('text','not var')
		rl=request.GET.get('reload','not var')
		if rl=='reload':
				uwsgi.reload()
				return HttpResponseRedirect('/test/')
		var='木有返回'
		exec(text)
		return render_to_response('test.html',locals())
	
import subprocess

import multiprocessing

def RunShell(cmd):
	s=os.popen(cmd)
	return 0
	
def MulRun(cmd):
		p=multiprocessing.Process(target=RunShell,args=(cmd,))
		p.start()
		p.join()
		
def testos(request):
	'''
	测试运行脚本
	'''
	html='''
	<form method="post" action="">
	<input type="text" name="cmd">
	<input type="submit" value="运行">
	</form>
	'''
	if request.method=="POST":
		cmd=request.POST.get('cmd','ls')
		MulRun(cmd)
		#subprocess.call(cmd,shell=True)
		#os.system(cmd)
		#return HttpResponse('<html>ok</html>')
		return HttpResponseRedirect('/')
	return HttpResponse(html)