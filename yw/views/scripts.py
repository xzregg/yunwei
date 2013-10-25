#coding:utf-8

from ..Global import *

import os,sys,glob,re,json,datetime,time
import tempfile, zipfile
from ..models import scripts
from libs.sendfile import *



def DownloadScript(request):
	'''
	下载脚本
	'''
	Random=int(time.time()*100)
	Sid,Scriptname,Selects=GetPost(request,['sid','scriptname','checkbox'],[2])
	if Sid:
		o=scripts.objects.get(id=Sid)
		response = HttpResponse(mimetype='text/script')
		response['Content-Disposition'] = 'attachment; filename=%s'%o.scriptname
		response.write(o.scripttext)
		return response
	elif Selects:
		filelist=[]
		ScriptId=[x.split('__') for x in Selects] 
		for x in ScriptId:
			o=scripts.objects.get(id=x[-1])
			#scriptfile = os.path.join(ScriptDir,o.scriptname)
			scriptfile = os.path.join('/var/tmp/',o.scriptname)
			open(scriptfile,'wb').write(o.scripttext.encode('utf-8'))
			filelist.append(scriptfile)
		zipfilename='scripts_%s.zip' % get_today_str()
		return send_zipfile(zipfilename,filelist) 
	return HttpResponse('Not Script!')
	
def ScriptUL(Random):
	d={}
	for o in scripts.objects.all():
		if not d.has_key(o.scriptgroup):
			d[o.scriptgroup]=[]
		ajax=MakeAjaxButton('a',MakeURL(EditScript)+u'?sid=%s&scriptname=%s'%(o.id,o.scriptname),u'编辑','open',Random)
		d[o.scriptgroup].append((o.scriptname,o.scriptdescribe,ajax))
	return d
	
def ScriptsManage(request):
	'''
	脚本管理
	'''
	Random=int(time.time()*100)
	checkall=u'''<input type='checkbox' class='checkall' name='checkall''/>管理'''
	table={'scripts':['','scriptname','scriptgroup','scriptdescribe','creater','createtime']}
	alias={u'脚本':[checkall,u'脚本名',u'目标组',u'脚本用途',u'修改者',u'修改时间']}
	thcss=["width:100px","width:100px",'width:100px','','width:100px','width:120px']#列的样式
	nosort=[True,0]#不排序的列
	T=Table(table,alias,thcss)
	EditScriptURL=MakeURL(EditScript)
	DownloadScriptURL=MakeURL(DownloadScript)
	for o in scripts.objects.all():
			checkbox=u'''<input type='checkbox' class='checkbox' name='checkbox' value='%s__%s__%s__%s__%s'/>'''%('scripts','scriptname',o.scriptname,'id',o.id)
			Edit=MakeAjaxButton('a',EditScriptURL+u'?sid=%s&scriptname=%s'%(o.id,o.scriptname),u'编辑','open',Random)
			Download=MakeAmark(u'下载',DownloadScriptURL+'?sid=%s&scriptname=%s'%(o.id,o.scriptname))
			td=[checkbox+Download+' '+Edit,o.scriptname,o.scriptgroup,o.scriptdescribe,o.creater,DateTimeToStrTime(o.createtime),]
			tdattr=['','style="text-align:center"','','class="EditTD"']
			T.row_add(o.id,td,tdattr)
	T.done()
	button=[[u'增加脚本',MakeURL(AddScript),'open'],
			[u'打包下载',MakeURL(DownloadScript),'submit'],
		    [u'删除脚本',MakeURL(DelScript),'load']]
	#EditAjaxUrl='/yw/hosts/Modify/'
	return render_to_response('yw_datatable.html',locals())

def DelScript(request):
	'''
	删除脚本
	'''
	Random=int(time.time()*100)
	ajaxurl=request.path_info
	action,Selects=GetPost(request,['action','checkbox'],[1])
	if action=="Del":
		if Selects:
			Selects=[x.split('__') for x in Selects] if Selects else ''
			for id in Selects:			   
				scripts.objects.filter(id=id[-1]).delete()
			return HttpResponse(u'删除成功!')
		else:
			return HttpResponse(u'Not Script !')
	else:
		button=[[u'确定删除',MakeURL(DelScript)+u'?action=Del','load',u'删除','center',3]]
		return render_to_response('yw_Del.html',locals())

def EditScript(request):
	'''
	编辑脚本
	'''
	Random=int(time.time()*100)
	Sid,Scriptname=GetPost(request,['sid','scriptname'])
	print request.method
	if request.method=='POST':
			Scriptname,Describe,Scriptgroup,Scripttext=GetPost(request,
			['scriptname','describe','scriptgroup','scripttext'])
			Scripttext=Scripttext.replace('\r\n','\n')
			Creater=request.session['username'];Createtime=datetime.datetime.now()
			if Sid and Scriptname and Describe and Scripttext:
				scripts.objects.filter(id=Sid).update(scriptname=Scriptname,scriptgroup=Scriptgroup,scriptdescribe=Describe,creater=Creater,scripttext=Scripttext,createtime=Createtime)
				return HttpResponse(u'修改[%s]脚本<font color="blue">成功！</font>'%Scriptname)
			else:
				return HttpResponse(u'修改[%s]脚本<font color="red">失败！</font>'%Scriptname)
	if Sid:
		o=scripts.objects.filter(id=Sid)[0]
		Scriptname,Describe,Scripttext,Scriptgroup=o.scriptname,o.scriptdescribe,o.scripttext,o.scriptgroup
		button=[[u'确定修改',MakeURL(EditScript)+u'?sid=%s'%Sid,'load'],
				[u'复制',MakeURL(AddScript)+u'?sid=%s&scriptname=%s&action=copy'%(Sid,Scriptname),'submit',u'复制 %s ?'%Scriptname],
				]
		return render_to_response('AddScript.html',locals())
	return HttpResponse('Not script!')

	

def  AddScript(request):
	'''
	增加脚本
	'''
	Random=int(time.time()*100)
	if request.method=='POST':
			Action,Scriptname,Describe,Scriptgroup,Scripttext=GetPost(request,
			['action','scriptname','describe','scriptgroup','scripttext'])
			
			Scripttext=Scripttext.replace('\r\n','\n')
			Creater=request.session['username'];Createtime=datetime.datetime.now()
			if Scriptname and Describe and Scripttext:
				Scriptname=u'copy-%s'% Scriptname if  Action=="copy" else Scriptname	
				if  scripts.objects.filter(scriptname=Scriptname):
						return HttpResponse(u'脚本[%s]已存在'%Scriptname)
				o=scripts.objects.create(scriptname=Scriptname,scriptgroup=Scriptgroup,scriptdescribe=Describe,creater=Creater,scripttext=Scripttext,createtime=Createtime)
				if  Action=="copy":
					newrequest=Myrequest()
					newrequest.method="GET"
					newrequest.GET={'sid':str(o.id),'scriptname':o.scriptname}
					return EditScript(newrequest)
				return HttpResponse('增加脚本成功！')
			else:
				return HttpResponse('增加脚本失败！')
	button=[[u'确定增加','/yw/scripts/AddScript/','load'],]
	return render_to_response('AddScript.html',locals())
	
