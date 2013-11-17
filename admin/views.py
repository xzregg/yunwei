#coding:utf-8
from django.http import HttpResponseRedirect
from django.http import HttpResponse,Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
from settings import djangoReload

import datetime,sys,time


from libs.timelib import *

#rsa算法和防止重复提交
from libs.forms import publickey_encodeing,privatekey_decodeing,GetMePublickey,anti_resubmit
from libs.html import *

import cStringIO
import binascii,struct

#用户表
from models import user,views,usergroup,logs

from settings import SessionTimeout,DEBUG
_sessiontimeout = SessionTimeout

def GetUrlPermission(url):
	UrlPermission = {'kvurl':{},'normalurl':{}}
	for o in views.objects.filter(accessurl=url):
		url = o.accessurl
		if o.viewurl.find('^') == 0:
			UrlPermission['normalurl'][url] = {'permission':o.permission,'logtype':o.logtype,'title':o.title}
		else:
			kvlist = o.viewurl.split(',')
			for x in kvlist:
				kv = x.split('=')
				if len(kv) != 2:continue
				k,v = kv
				UrlPermission['kvurl'].setdefault(k,{})
				UrlPermission['kvurl'][k].setdefault(v,{})
				UrlPermission['kvurl'][k][v].setdefault(url,{})
				UrlPermission['kvurl'][k][v][url]['permission'] = o.permission
				UrlPermission['kvurl'][k][v][url]['logtype'] = o.logtype
				UrlPermission['kvurl'][k][v][url]['title'] = o.title
	return UrlPermission

def CheckURL( request):
	#FullUrl = request.get_full_path()
	url = request.path_info
	V_P = '';title = '';isLog = False
	UrlPermission = GetUrlPermission(url)
	if UrlPermission['normalurl'].has_key(url):
		V_P = UrlPermission['normalurl'][url]['permission']
		title = UrlPermission['normalurl'][url]['title']
		if UrlPermission['normalurl'][url]['logtype'] == 1:
			isLog = True
	if request.REQUEST.keys():#含有参数的url
			d = dict(request.REQUEST)
			for k,v in d.iteritems():
				if  UrlPermission['kvurl'].has_key(k) and  UrlPermission['kvurl'][k].has_key(v) and UrlPermission['kvurl'][k][v].has_key(url):
					V_P = UrlPermission['kvurl'][k][v][url]['permission']
					title = UrlPermission['kvurl'][k][v][url]['title']
					if UrlPermission['kvurl'][k][v][url]['logtype'] == 1:
						isLog = True
	return (V_P,title,isLog)


def requires_login(view,accessurl='',*args, **kwargs):#登录与权限检查
	def new_view(request,*args, **kwargs):
			#print dict(request.POST)
			FullUrl = request.get_full_path()
			Now = datetime.datetime.now()
			V_P,Title,isLog = CheckURL(request)
			if isLog:LogURL(request,Title)
			V_P = V_P or 0
			if V_P == 0:return view(request,*args, **kwargs)
			if  request.session.get('uid','') and (Now-request.session.get('accesstime',Now)).seconds<_sessiontimeout:
				request.session['accesstime'] = Now
				U_P = user.UserGroupPermission(request.session.get('uid'))
				if U_P == -1:return HttpResponse(u'你已被锁定!<a href="/logout/">登出</a>')
				if CheckPermission(U_P,V_P):#没有权限：
					return view(request,*args, **kwargs)	
				else:
					return HttpResponse(u'你没有权限访问[%s]'%Title)
			else:#超时
				request.session.clear()
				return HttpResponse('<script> window.top.location="/login/?fromurl=%s"</script>'%FullUrl)
	return new_view
	
	
def CheckPermission(U_P,V_P):
	return CheckBin(U_P,V_P)
def CheckBin(U_P,V_P):#检查权限
		if int(U_P) == 0 or int(V_P) == 0 :return True#管理员
		U_Bin = bin(int(U_P))[2:]
		if len(U_Bin) < V_P:#
			return False
		elif U_Bin[-V_P] == "1":
			return True
		return False
	




def LogURL( request,title):
	loginfo = ''
	for k,v in dict(request.REQUEST).iteritems():	
		loginfo += '%s = %s\n' % (k,v[:20])#只记录20个字符
	Log(request,title,loginfo)



def Sha1Md5( str):
	import hashlib
	return hashlib.sha1(hashlib.md5(str).hexdigest()).hexdigest()


def login( request):
	'''
	登录
	'''
	Random = int(time.time() * 100)
	from settings import Title,LoginFailNums,LonginAgainSec
	Now = datetime.datetime.now()
	ip = request.META['REMOTE_ADDR']
	if request.POST.get('action','') == "GetMePublickey":#获取公钥匙
		return HttpResponse(GetMePublickey(request))
	if request.method ==  'POST' and request.session.get('verify',''):
		request.session.setdefault('loginfail',0)
		if request.session['loginfail'] > LoginFailNums:
			request.session.setdefault('logintime',Now)
			TimeDifference = (Now - request.session['logintime']).seconds
			if TimeDifference > LonginAgainSec:
				del request.session['logintime']
				request.session['loginfail'] = 0
			else:
				return HttpResponse('<script>alert("%s秒 后再试")</script>' % (LonginAgainSec - TimeDifference))	
		verify = request.session.get('verify','1')
		checkcode = request.POST.get('check','2')
		password = request.POST.get('password','')
		loginname = request.POST.get('loginname','')
		if  verify == checkcode and len(password) == 256:#Rsa1024为加密后长度为256
			privkey = request.session['privkey']
			password = privatekey_decodeing(password,privkey)
			loginname = privatekey_decodeing(loginname,privkey)
			try:
				user_objects = user.objects.get(loginname=loginname,password=Sha1Md5(password)) 
				if user_objects.lock == False :
					request.session['username'] = user_objects.username
					request.session['loginname'] = user_objects.loginname
					request.session['uid'] = user_objects.id
					request.session['permission'] = user_objects.permission
					request.session['accesstime'] = Now
					request.session['logintime'] = Now
					request.session['loginip'] = ip
					request.session['verify'] = ''
					user_objects.logintime = Now
					user_objects.loginip = ip
					user_objects.save()
					request.session['loginfail'] = 0
					Log( request,u'登录成功','')
					_fromurl = request.GET.get('fromurl','') or '/'
					return HttpResponse('<script> window.top.location="%s"</script>' % _fromurl)
					#return HttpResponseRedirect('/')
				else:
					msg = u'用户已锁定！' 
					Log( request,u'登录失败',u'用户锁定',loginname)
			except:
				request.session['loginfail'] += 1
				msg = u'登录失败,你还有[%s]次机会!'%(LoginFailNums-request.session['loginfail'])
				Log( request,u'登录失败',u'认证失败',loginname)
		else:
			request.session['loginfail'] += 1
			msg = u'验证错误,你还有[%s]次机会!'%(LoginFailNums-request.session['loginfail'])

	return render_to_response('login.html',locals())

		
def logout( request):
	'''登出'''
	try:
		request.session.clear()
		return HttpResponseRedirect('/login/')
	except KeyError:
		return HttpResponse('<script>var redirect=confirm("fuck");if(redirect){window.location.href="/login/"}</script>')



def AddUser(request):
	'''
	增加用户
	'''
	Random = int(time.time() * 100)
	loginname,username,password,contact,viewslist = GetPost(request,
	['loginname','username','password','contact','checkbox'])
	if request.method == "POST":
		if  viewslist and username and loginname and password:
			privkey = request.session['privkey']
			password = privatekey_decodeing(password,privkey)
			password = Sha1Md5(password)
			createuser = '%s[%s]'%(request.session['username'],request.session['loginname'])
			if not user.objects.filter(loginname=loginname):
				permission = views.MakePermission(viewslist)
				user.objects.create(username=username,createuser=createuser,loginname=loginname,password=password,permission=permission,contact=contact)
				return HttpResponse('注册成功!')
			else:
				return HttpResponse('用户已存在!')
		return HttpResponse(u'请至少选择一个权限！') if not viewslist else HttpResponse(u'注册失败!')
	Views = GetPermission(request.session['permission'],False)

	return render_to_response('AddUser.html',locals())

def EditUserMe(request):
	'''
	编辑自己
	'''
	return EditUser(request,Me=True)

def EditUser(request,Me=False):
	'''
	编辑用户
	'''
	Random = int(time.time() * 100)
	User,Uid = GetPost(request,['user','uid'])
	User = request.session['loginname']  if Me else User
	Uid = request.session['uid'] if Me else Uid
	if  Uid :
		obj=user.objects.get(id=Uid)
		UserName = obj.username
		LoginName = User
		Contact = obj.contact
		if request.method == "POST":
			loginname,username,password,contact = GetPost(request,['loginname','username','password','contact'])
			if password:
				privkey = request.session['privkey']
				password = privatekey_decodeing(password,privkey)
				password = Sha1Md5(password)
				obj.password = password
			obj.username,obj.contact = username,contact
			if not Me:
				obj.loginname  =  LoginName
			obj.save()
			return HttpResponse(u'编辑%s[%s]成功!' % (User,username))
	button = [[u'确定',u'?uid = %s&user = %s' % (Uid,User)]]
	return render_to_response('EditUser.html',locals())
	
def DelUser(request):
	'''
	删除/锁定用户
	'''
	Random = int(time.time() * 100)
	User,Uid,action = GetPost(request,['user','uid','action'])

	if Uid and User and action:
		if action == "delete":
			user.objects.filter(id=Uid).delete()
			return HttpResponse(u'删除[%s]成功!' % User)
		if action == "lock":	
			user.objects.filter(id=Uid).update(lock=True)
			return HttpResponse(u'锁定[%s]成功!' % User)
		if action == "unlock":	
			user.objects.filter(id=Uid).update(lock=False)
			return HttpResponse(u'解锁[%s]成功!' % User)	
	button=[[u'锁定%s' % User,MakeURL(DelUser) + u'?action=lock&uid=%s&user=%s' % (Uid,User),'load',u'锁定','center',3],
		[u'解锁%s' % User,MakeURL(DelUser) + u'?action=unlock&uid=%s&user=%s' % (Uid,User),'load',u'解锁','center',3],
		[u'删除%s' % User,MakeURL(DelUser) + u'?action=delete&uid=%s&user=%s' % (Uid,User),'load',u'删除','center',3]
		]
	return render_to_response('Del.html',locals())



def UserManage(request):
	'''
	用户管理
	'''
	Random = int(time.time() * 100)
	alias = {u'用户管理':[u'管理',u'登录名',u'用户名',u'用户组',u'创建者',u'登录时间',u'登录IP']}
	table = {'user_t':['manage','loginname','username','usergroup','createuser','logintime','loginip']}
	thcss = ['','','','width:150px']
	T = Table(table,alias,thcss)

	for o in  user.objects.all():
		DateTime = ''
		if o.logintime:DateTime = datetime.datetime.strftime(o.logintime,TimeFormat)
		ajax = MakeAjaxButton('a',MakeURL(ShowPermission) + u'?uid=%s&user=%s' % (o.id,o.loginname),u'查看权限','load',Random,'','center')
		ajax += MakeAjaxButton('a',MakeURL(EditUser) + u'?uid=%s&user=%s' % (o.id,o.loginname),u'编辑','open',Random,)
		Lock = u'解锁' if o.lock == True else u'锁定'
		ajax += MakeAjaxButton('a',MakeURL(DelUser) + u'?uid=%s&user=%s' % (o.id,o.loginname),Lock,'load',Random)
		tds = [ajax,o.loginname,o.username,o.usergroup,o.createuser,DateTime,o.loginip]
		tdattrs = []
		T.row_add(o.id,tds,tdattrs) 
	T.done()
	nosort = [True,6]
	button = [[u'增加用户',MakeURL(AddUser),'open']]
	return render_to_response('datatable.html',locals())

def GetPermission(IntPermission,showall=True):
	'''获取权限'''
	Views = {}
	for v in views.objects.all():
		if not v.groupname in Views.keys():
			Views[v.groupname] = []
		checked = True if CheckBin(IntPermission,v.permission) else False#拥有这个功能的权限
		if showall or checked :#这个用户拥有这个权限，显示
			Views[v.groupname].append(MakeCheckbox(v.id,v.title + '[%s]'%v.permission,checked))
	return Views
def ShowPermission(request):
	'''
			查看权限
	'''
	Random = int(time.time() * 100)
	User,Uid,Gid,Group = GetPost(request,
	['user','uid','gid','group'])

	if Uid and User:
		Who = User
		permission = user.objects.get(id=Uid).permission
	elif Gid and Group:
		Who = Group
		permission = usergroup.objects.get(id=Gid).permission

	Who = '%s[%s]'%(Who,permission)
	Views = GetPermission(permission)
	button = [
		[u'修改权限',MakeURL(ChangePermission)+u'?uid=%s&user=%s&gid=%s&group=%s' % (Uid,User,Gid,Group),'load','','',3]
	]
	return render_to_response('ShowPermission.html',locals())  

def ChangePermission(request):
	'''
	改变权限
	'''
	User,Uid,Gid,Group,viewslist = GetPost(request,
	['user','uid','gid','group','checkbox'],[4])
	if request.method == "POST" and (Gid or Uid):
			if User and Uid:
					user.ChangePermission(Uid,viewslist)
			if Group and Gid:
					usergroup.ChangePermission(Gid,viewslist)
			return HttpResponse(u'修改[%s]权限OK!'%(User + Group))
	return HttpResponse('没有用户!')

def AddUserGroup(request):
	'''
	增加用户组
	'''
	Random = int(time.time() * 100)
	usergroupname,viewslist = GetPost(request,['usergroupname','checkbox'],[1])
	if viewslist and usergroupname :
		if not usergroup.objects.filter(groupname=usergroupname):
			permission = views.MakePermission(viewslist)
			usergroup.objects.create(groupname=usergroupname,permission=permission)
			return HttpResponse(u'添加用户组[%s]成功!' % usergroupname)
		else:
			return HttpResponse(u'添加用户组[%s]已存在!' % usergroupname)
	Views = GetPermission(request.session['permission'],False)
	button = [[u'确定增加',MakeURL(AddUserGroup),'load','','center',3]]
	return render_to_response('AddUserGroup.html',locals())

def DelUserGroup(request):
	'''
	删除用户组
	'''
	Random = int(time.time() * 100)
	Gid,Group,action = GetPost(request,['gid','group','action'])
	if action == "delete":
		Group = usergroup.DelUserGroup(Gid)
		return HttpResponse(u'删除 [%s]成功!' % Group)
	button = [[u'删除[%s]' % Group,MakeURL(DelUserGroup) + u'?action=delete&gid=%s&group=%s' % (Gid,Group),'load',u'删除','center',3]]
	return render_to_response('Del.html',locals())
	
def UserGroupManage(request):
	'''
	用户组管理
	'''
	Random = int(time.time() * 100)
	alias = {u'用户组管理':[u'管理',u'用户组名',u'成员']}
	table = {'usergroup_t':['Manage','groupname','groupmembers']}
	thcss = ['width:150px','']
	T = Table(table,alias,thcss)
	for o in  usergroup.objects.all():
		UserNums = len([x for x in o.groupmembers.split(',') if x])
		ajax1 = MakeAjaxButton('a',MakeURL(ShowGroupUser) + u'?gid=%s&group=%s' % (o.id,o.groupname),u'查看组成员[%s]' % UserNums,'load',Random)
		ajax2 = MakeAjaxButton('a',MakeURL(ShowPermission) + u'?gid=%s&group=%s' % (o.id,o.groupname),u'查看组权限','load',Random,'','center')
		ajax3 = MakeAjaxButton('a',MakeURL(DelUserGroup) + u'?gid=%s&group=%s' % (o.id,o.groupname),u'删除用户组','load',Random)
		T.row_add(o.id,[ajax2 + ajax3,o.groupname,ajax1],[])
	T.done()
	#nosort = [True,6]
	button = [[u'增加用户组',MakeURL(AddUserGroup),'load']]
	return render_to_response('datatable.html',locals())
	

def ShowGroupUser(request):
	'''
	查看/修改组用户
	'''
	Random = int(time.time() * 100)
	Gid,Group,UserList,Action = GetPost(request,['gid','group','checkbox','action'],[2])
	if Gid and Group:
		if Action == 'change':
			Group = usergroup.ChangeGroupUser(Gid,UserList)
			return HttpResponse(u'修改[%s]成员成功！' % Group)
		UserCheckBox = []
		GroupMembers = usergroup.GetGroupMembers(Gid)
		for o in user.objects.all():#列出组里用户
			checked = True if str(o.id) in GroupMembers else False
			UserCheckBox.append(MakeCheckbox(o.id,'%s[%s]' % (o.loginname,o.username),checked))
		UserCheckBox = ''.join(UserCheckBox)
		button = [[u'修改[%s]成员' % Group,MakeURL(ShowGroupUser) + u'?gid=%s&group=%s&action=change' % (Gid,Group),'load',u'修改成员','',3]]
		return render_to_response('ShowGroupUser.html',locals())


def ClearErrView(request):
	'''
	删除错误视图
	'''
	Random = int(time.time() * 100)
	msg = ''
	if request.GET.get('action','') == "clearerrviews":#删除不存在的视图
		msg = views.ClearErrView()
	return HttpResponse(u'删除了[%s]' % msg)

def ViewsLog(request):
	'''
	视图记录日志
	'''
	Random = int(time.time() * 100)
	Vid,action,Selects = GetPost(request,['vid','action','checkbox'],[2])
	if action:
			Selects = [Vid] if Vid else [x.split('__')[-1] for x in Selects if x]
			logtype,Retmsg=(1,u'设置记录日志成功!') if action == "1" else (0,u'取消记录日志成功!')
			views.ViewsLog(Selects, logtype)
			return HttpResponse(Retmsg)
	else:
		button = [[u'记录日志',MakeURL(ViewsLog) + u'?action=1','load',u'记录日志','',3],
				[u'取消记录',MakeURL(ViewsLog) + u'?action=0','load',u'取消记录','',3],
		]
		return render_to_response('ViewsAction.html',locals())
	
def ViewsShow(request):
	'''
	菜单显示
	'''
	Random = int(time.time() * 100)
	Vid,action,Selects = GetPost(request,['vid','action','checkbox'],[2])
	if action:
			Selects = [Vid] if Vid else [x.split('__')[-1] for x in Selects if x]
			displaytype,Retmsg=(1,u'设置菜单项成功!') if action == "1" else (0,u'取消菜单项成功!')
			views.ViewsShow(Selects,displaytype)
			return HttpResponse(Retmsg)
	else:
		button = [[u'设置菜单项',MakeURL(ViewsShow) + u'?action=1','load',u'设置菜单项','',3],
				[u'取消菜单项',MakeURL(ViewsShow) + u'?action=0','load',u'取消菜单项','',3],
		]
		return render_to_response('ViewsAction.html',locals())
		
def CheckViewPermission(request):
	'''
	检查视图权限
	'''
	Random = int(time.time() * 100)
	Vid,action,Selects = GetPost(request,['vid','action','checkbox'],[2])
	if action:
			Selects = [Vid] if Vid else [x.split('__')[-1] for x in Selects if x]
			cp,Retmsg=(True,u'设置权限检测成功!') if action == "1" else (False,u'取消查权成功!')
			views.CheckViewPermission(Selects, cp)
			return HttpResponse(Retmsg)
	else:
		button = [[u'权限检测',MakeURL(CheckViewPermission) + u'?action=1','load',u'权限检测','',3],
				[u'取消查权',MakeURL(CheckViewPermission) + u'?action=0','load',u'取消查权','',3],
		]
		return render_to_response('ViewsAction.html',locals())
	
		
def ViewsManage(request):#视图管理
	'''
	视图管理
	'''
	Random = int(time.time() * 100)
	checkbox = u'''管理<input type = 'checkbox' class = 'checkall' name = 'checkall''/>'''
	alias = {u'视图管理':[checkbox,u'功能名',u'访问URL',u'DjangoURL',u'视图名',u'组名',u'查权',u'菜单',u'日志']}
	table = {'views':['checkall','title','accessurl','viewurl','viewname','groupname','permission','displaytype','logtype']}#对应数据库
	T = Table(table,alias)#第3列为主键
	for o in  views.objects.all():
		if o.viewname:
			ajax = u'<a href = "%s" target = "_blank">%s</a>' % (o.accessurl,u'访问')
		else:
			ajax=MakeAjaxButton('a',MakeURL(DelPermission) + u'?pid=%s&title=%s' % (o.id,o.title),u'删除','load',Random)
		checkbox = MakeCheckbox('%s__%s__%s__%s' % ('title',o.title,'id',o.id),'')
		phtml,p = (u'取消',0) if o.permission else (u'设置',1)
		Permission = MakeAjaxButton('a',MakeURL(CheckViewPermission) + u'?vid=%s&action=%s' % (o.id,p),phtml,'load',Random,u'修改?','',2) 
		mhtml,m = (u'取消',0) if o.displaytype == 1 else (u'设置',1)
		isMenu = MakeAjaxButton('a',MakeURL(ViewsShow) + u'?vid=%s&action=%s' % (o.id,m),mhtml,'load',Random,u'修改?','',2) 
		lhtml,l = (u'取消',0) if o.logtype else (u'设置',1)
		isLog = MakeAjaxButton('a',MakeURL(ViewsLog) + u'?vid=%s&action=%s' % (o.id,l),lhtml,'load',Random,u'修改?','',2) 
		tds = [checkbox+ajax,o.title,o.accessurl,o.viewurl,o.viewname,o.groupname,Permission,isMenu,isLog]
		tdattrs = ['','class="EditTD"','class="EditTD"','class="EditTD"','','class="EditTD"','class=""','class=""','class=""']
		T.row_add(o.id,tds,tdattrs)
	T.done()
	EditAjaxUrl = MakeURL(Modify)
	button = [[u'增加权限视图',MakeURL(AddPermission),'open'],
			[u'清除错误视图',MakeURL(ClearErrView) + u'?action=clearerrviews','load'],
			[u'检查权限',MakeURL(CheckViewPermission),'load'],
			[u'菜单显示',MakeURL(ViewsShow),'load'],
			[u'记录日志',MakeURL(ViewsLog),'load'],
			]
	nosort = [True,0]#不排序的列
	return render_to_response('datatable.html',locals())

def DelPermission(request):
	'''
	删除权限
	'''
	Random = int(time.time() * 100)
	Pid,Title,action = GetPost(request,['pid','title','action'])
	if action == "delete":
		if Pid and Title:
			views.DelPermission(Pid)
			return HttpResponse(u'删除 [%s]成功!' % Title)
		else:
			return HttpResponse(u'删除 [%s]失败!' % Title)
	button = [[u'删除[%s]'%Title,MakeURL(DelPermission) + u'?action=delete&pid=%s&title=%s' % (Pid,Title),'load',u'删除','',3]]
	return render_to_response('Del.html',locals())

def MakeViewsSerect():
	d = {}
	for o in views.objects.all():
		if o.viewurl.find('^') == 0:
			d.setdefault(o.groupname,[])
			d[o.groupname].append([o.accessurl,o.title])
	return d
def AddPermission(request):
	'''
	增加权限
	'''
	Random = int(time.time() * 100)
	if request.method == "POST":
		title,viewsselect,kv,groupname = GetPost(request,['title','viewsselect','kv','groupname'])
		if kv and title:
			views.AddPermission(title=title,accessurl=viewsselect,viewurl=kv,viewname="",groupname=groupname,permission=0,displaytype=3,loadcheck=3)
			return HttpResponse(u'添加[%s]权限成功!'%title)
		else:
			return HttpResponse(u'添加权限失败!')
	ViewsSerect = MakeViewsSerect()
	button = [[u'增加权限',request.get_full_path()]]
	return render_to_response('AddPermission.html',locals())
	
def Modify(request):#改表
	'''
	改视图表
	'''
	value = 'None'
	Random = int(time.time() * 100)
	tablename = request.GET.get('tablename','')
	if tablename  == "views":
		row = request.POST.get('row','')
		if row:
			tn,th,td = row.split('__')
			cloumn = request.POST.get('column','')
			value = request.POST.get('value','')
			views.objects.filter(**{th:td}).update(**{cloumn:value})
	return HttpResponse(value)



def Log( request,title,info,who=''):
	'''
	记录日志
	'''
	Now = datetime.datetime.now()
	who = who or request.session.get('loginname','anonymous')
	ip = request.META['REMOTE_ADDR']
	logs.objects.create(title=title,who=who,logdatetime=Now,info=info,ip=ip)

def ClearLogs(request):
	'''
	清除日志
	'''
	if request.GET.get('action','') == 'clear' and request.method == "POST":
		if logs.Truncate():
			Log(request,'清除全部日志','action=clear')
			return HttpResponse('清除日志成功！')
		else:
			return HttpResponse('清除日志失败！')
	button = [[u'确定清除全部日志',MakeURL(ClearLogs) + u'?action=clear','load',u'清除全部日志','center',3]]
	return render_to_response('Clear.html',locals())
	
def ShowLogs(request):
	'''
	查看日志
	'''
	Search,Page,Stime,Etime = GetPost(request,['search','page','stime','etime'])
	Stime = Stime if isDateTimeFormat(Stime) else ''
	Etime = Etime if isDateTimeFormat(Etime) else get_nowtime_str()
	Page = Page or 1#保证最小页数为1
	Page = int(Page)
	ItemNum = 50
	TolItem,Logs = logs.SearchLog(Page,ItemNum,Stime,Etime,Search)
	TolPage = TolItem / ItemNum
	TolPage += 1 if TolItem % ItemNum !=  0 else 0
	PreviousPage = Page-1 
	NextPage = Page + 1 if TolPage > Page else Page
	LastPage = TolPage
	#TolItem = logs.GetCount(Search)
	#Logs = logs.FilterOR(Search,startPos,ItemNum,Stime or '1970-01-01 00:00:00',Etime)
	alias = {u'日志记录':[u'id',u'操作者',u'操作时间',u'操作ip',u'标题',u'信息']}
	table = {'logs':['id','who','logdatetime','ip','title','info']}#对应数据库
	thcss = ['width:20px','width:60px','width:160px','width:100px','width:100px;text-align:center','text-align:left']
	T = Table(table,alias,thcss)#
	
	#for i,o in  enumerate(Logs):
	# T.row_add(o[0],[o[0],o[1],datetime.datetime.strftime(o[2],TimeFormat),o[5],o[3],o[4].replace('\n','<br>')],['','','','','','class="EditTD"'])
	for o in  Logs:  
		T.row_add(o.id,
					[o.id,o.who,DateTimeToStrTime(o.logdatetime),o.ip,o.title,o.info.replace('<',r'&lt;').replace('>',r'&gt;').replace('\n','<br>')],
					['','','','','','class="EditTD"']
				)
	T.done()
	button = [[u'清除日志',MakeURL(ClearLogs),'load']
			]
	#nosort = [True,0]
	return render_to_response('ShowLog.html',locals())
	

def returnIndex( request,view=None,redirectUrl=''):
		LogURL(request,request.META['HTTP_HOST'])
		if  redirectUrl:
			return HttpResponseRedirect(redirectUrl)
		else:
			return view(request)
	
def index(request):
	'''
	主页
	'''
	from settings import Title
	if request.GET.get('action','') == 'getinfo':
		return render_to_response('Info.html',locals())
	U_P = user.UserGroupPermission(request.session.get('uid',0))
	username = request.session.get('username','')
	loginname = request.session.get('loginname','')
	uid = request.session.get('uid','')
	logintime = DateTimeToStrTime(request.session.get('logintime',datetime.datetime.now()))
	loginip = request.session.get('loginip','')
	d = {}
	
	for o in views.objects.all():
		g = o.groupname
		if o.viewname and o.displaytype == 1 and  CheckBin(U_P,o.permission):
			d.setdefault(g,[])
			d[g].append([o.accessurl,o.title])
			
	from settings import Menu
	ul = d.keys() + Menu.keys()

	d.update(Menu)
	menu = [[k,d[k]] for k in ul ]

	
	return render_to_response('index.html',locals())

def ErrorRedirect( request):
	return HttpResponseRedirect('/')
def AdminSystem(request):
	'''
	ADMIN系统
	'''
	TabUrl = [[MakeURL(UserManage),u'用户管理'],
		[MakeURL(UserGroupManage),u'用户组管理'],
		[MakeURL(ViewsManage),u'视图和权限管理'],
		]#定义这个页面有多少个tab
	return render_to_response('showtab.html',locals())
