#coding:utf-8

from ..Global import *


import os,sys,glob,re,json,time
#rsa算法
from libs.forms import publickey_encodeing,privatekey_decodeing,GetMePublickey
from ..models import  fileobj,hosts,hostgroup,scripts
from .control import RunCmd,RunScript,Publickey,Interface
from ..core.ssh import Host

sys.path.append(os.path.dirname(__file__))
    #获取函数名---------
    #import inspect
    #MyFuncName=inspect.stack()[0][3]
    #MyFuncName=sys._getframe().f_code.co_name
    #------------------


    
def TextToHostConfig(Text,sudo,commit=False):
    Hosts={};groups=[];Hostgroup={};i=0
    for line in Text.split('\n'):
        i+=1
        ma=re.search('^#\[([^/].*)\]', line)
        if ma:#匹配组开头符号				
                groups.append(ma.group(1))
                continue
        elif not re.search('^#', line) and re.search('\w', line):#不是开头#也不是组开头符号
                    host=line.split()
                    UserIp='%s@%s'%(host[1],host[3])
                    k=str(i)+' '+UserIp
                    Hosts.setdefault(k,{})
                    d=Hosts[k] 
                    d['alias'],d['user'],d['passwd'],d['ip'],d['port']=host[:5]
                    d['describe']=' '.join(host[5:])
                    d['sshtype']=1 if d['user']!='root' and sudo else 0
                    d['group']=','+','.join(groups)+','				
                    o=None
                    if commit :#and not hosts.objects.filter(ip=d['ip'],user=d['user']):
                        o=hosts.objects.create(alias=d['alias'],
                                            ip=d['ip'],
                                            port=int(d['port']),
                                            user=d['user'],
                                            password=d['passwd'],
                                            group=d['group'],
                                            describe=d['describe'],
                                            sshtype=d['sshtype'])
                        if d['alias']=="n":
                            o.alias='Host_%s'%o.id
                            o.save()
                    for g in groups:
                            if g not in Hostgroup.keys():
                                    Hostgroup[g]=[]
                            if o:Hostgroup[g].append(o.id)
                        
                    continue

        else:
                ma=re.search('^#\[[/](.*)\]', line)#匹配组结束
                if ma:
                    groups.pop(groups.index(ma.group(1)))#删除结束
    if commit:				
        for k,v in Hostgroup.iteritems():#写入主机组
            if k:
                o,create=hostgroup.objects.get_or_create(groupname=k)
                o.groupmembers+=','.join([str(x) for x in v]).rstrip(',')+','
                o.save()
    return (Hosts,Hostgroup)
def MulAddHost(request):
    '''
    批量增加主机
    '''
    Random=int(time.time()*100)
    action,Text,sudo=GetPost(request,['action','Text','sudo'])
    if request.method=="POST": 
        if Text and action:
            if action=="commit":
                h,g=TextToHostConfig(Text,sudo,True)
                return HttpResponse(u'已添加:主机组[%s]个<br><hr>%s<br><hr>主机[%s]个<br><hr>%s'%(len(g.keys()),u'<br>'.join(g.keys()),len(h.keys()),u'<br>'.join(sorted(h.keys()))))
            if action=="check":
                h,g=TextToHostConfig(Text,sudo,False)
                return HttpResponse(u'已检查:主机组[%s]个<br><hr>%s<br><hr>主机[%s]个<br><hr>%s'%(len(g.keys()),u'<br>'.join(g.keys()),len(h.keys()),u'<br>'.join(sorted(h.keys()))))
            
        else:
                return HttpResponse(u'没有数据!')
    button=[[u'提交信息','?action=commit','load',u'提交信息'],
            [u'检测配置','?action=check','load',u'检测配置']]
    return render_to_response('MulAddHost.html',locals())



#FullUrl=request.get_full_path()
def RedirectToWebSsh(request):
    '''
    重定向WebSSH
    '''
    from .webssh import webssh
    Hid=request.GET.get('hid','')
    if Hid:
        o=hosts.GetHost('id',Hid)
        return HttpResponseRedirect(MakeURL(webssh)+u'?host=%s@%s&port=%s&t=linux'%(o.user,o.ip,o.port))
    else:
        return HttpResponse('Not Host!')

def SettingHostGroup():
    '''整理主机和组'''
    stime=time.time()
    HostGroups={'ALL':[]}
    for o in hosts.objects.all():
        HostGroups['ALL'].append(o.id)
        for g in o.group.split(","):
            if g:
                HostGroups.setdefault(g,[])
                HostGroups[g].append(o.id)

    for k,v in HostGroups.iteritems():
            o=hostgroup.objects.filter(groupname__exact=k)
            if o:
                o=o[0]
            else:
                o=hostgroup.objects.create(groupname=k)
            o.groupmembers=','.join([ str(x) for x in v]).rstrip(',')+','
            o.save()
    etime=time.time()
    #print '-'*6+'刷新主机缓存---------------完成用时%.1f'%(etime-stime)

    
def HostAttr(request):
    '''
    主机属性
    '''
    from .fileobj import ShowFileOBJ,Cron,Iptables
    from .scripts import ScriptUL
    Random=int(time.time()*100)
    gid,group,hid,ip=GetPost(request,['gid','group','hid','ip'])
    Urlopt=u'?hid=%s&ip=%s'%(hid,ip) if hid and ip else u'?gid=%s&group=%s'%(gid,group)
    if  hid and ip:
        Webssh=WebSSHFormat%(MakeURL(RedirectToWebSsh)+u'?hid=%s'%hid,ip)
        EditHostURL=MakeURL(AddHost)+Urlopt

    if request.method=="GET":
        isGET=True
    scriptul=ScriptUL(Random)
    CronURL=MakeURL(Cron)+Urlopt
    IptablesURL=MakeURL(Iptables)+Urlopt

    InterfaceURL=MakeURL(Interface)+(Urlopt if hid else '?SelectHostGroup=%s'%group)
    FileObjURL=MakeURL(ShowFileOBJ)+Urlopt
    return render_to_response('Attr.html',locals())

def HostGroupAttr(request):
    '''
    主机组属性
    '''
    return HostAttr(request)
    
def HostsManage(request):
    '''
    主机管理
    '''
    Random=int(time.time()*100)
    ret=[]
    Hosts=hosts.objects.all()
    checkbox=u'''管理<input type='checkbox' class='checkall' name='checkall''/>'''
    alias={u'主机':[checkbox,u'别名',u'用户',u'IP地址',u'端口',u'主机组',u'描述']}
    table={'hosts':['checkall','alias','user','ip','port','group','describe']}
    thcss=['width:50px','width:100px','width:100px','width:100px','width:40px','width:200px','']
    T=Table(table,alias,thcss)#第3项为th的style
    HostAttrURL=MakeURL(HostAttr)
    RedirectToWebSshURL=MakeURL(RedirectToWebSsh)
    for v in Hosts:
            checkbox=MakeCheckbox('%s__%s__%s__%s__%s'%('hosts','ip',v.ip,'id',v.id),'')
            HostAttrAjax=MakeAjaxButton('a',HostAttrURL+'?hid=%s&ip=%s'%(v.id,v.ip),v.alias,'load',Random)
            Webssh=WebSSHFormat%(RedirectToWebSshURL+u'?hid=%s'%v.id,v.ip)
            td=[checkbox,HostAttrAjax,v.user,Webssh,v.port,v.group,v.describe]
            tdattr=['','','','','','','class="text_left"']
            T.row_add(v.id,td,tdattr)	
    T.done()
    hidecolume=['<a href="javascript:void(0);" class="hidecolumn" cloumn="2">用户</a>']
    hidecolume+=['<a href="javascript:void(0);" class="hidecolumn" cloumn="4">端口</a>']
    nosort=[True,0]#不排序的列
    button=[[u'增加主机',MakeURL(AddHost),'open'],
        [u'批量增加主机',MakeURL(MulAddHost),'open'],
        [u'删除主机',MakeURL(DelHost),'load'],
        [u'添加到主机组',MakeURL(AddGroupHost),'load'],
        [u'执行命令',MakeURL(RunCmd),'load'],
        [u'执行脚本',MakeURL(RunScript),'load'],
        [u'公钥管理',MakeURL(Publickey),'load'],
        ]

    #EditAjaxUrl='/yw/hosts/Modify/'
    Hostgroupselect=hostgroup.GetHostGroup()
    return render_to_response('yw_datatable.html',locals())

def Modify(request):
    '''
    改主机表
    '''
    tablename=request.GET.get('tablename','')
    value='None'
    if tablename:
        row=request.POST.get('row','')
        tn,th,td=row.split('__')
        cloumn=request.POST.get('column','')
        value=request.POST.get('value','')
        if row and cloumn and td and value:
            s=eval('''%s.objects.filter(%s=%s).update(%s=value)'''%(tablename,th,td,cloumn))
    return HttpResponse(value)



def AddHost(request):
    '''
    增加与编辑主机
    '''
    Random=int(time.time()*100)
    Hostgroupselect=hostgroup.GetHostGroup()
    if request.POST.get('action','')=="GetMePublickey":#获取公钥
        return HttpResponse(GetMePublickey(request))
            
    ajaxurl=request.path_info
    action,hid,ip,port,alias,user,password,group,describe,sshtype=GetPost(request,
    ['action','hid','HostIP','HostPort','HostAlias','HostUser_e','HostPassword_e','SelectHostGroup','HostDescribe','checkbox'])
    if request.method=="POST":
        sshtype=1 if sshtype else 0
        if user or password :
            privkey=request.session['privkey']
            user=privatekey_decodeing(user,privkey) if user else user
            password=privatekey_decodeing(password,privkey) if password else password
        if action=="AddHost":
                if  ip and port and user and password  and not hosts.objects.filter(ip=ip,user=user) :
                    alias=alias or ''
                    host=Host(ip,port,user,password,sshtype)
                    c,s,t=host.SetPublicKey()

                    if c==0:
                        o=hosts.objects.create(alias=alias,ip=ip,user=user,
                                            password=password,
                                            port=int(port),
                                            group=group.rstrip(',')+',' ,
                                            describe=describe,
                                            sshtype=sshtype)
                        if not alias:
                            o.alias='Host_%s'%o.id
                            o.save()
                        SettingHostGroup()
                        Newrequest=Myrequest()
                        Newrequest.POST['hid'],Newrequest.POST['ip']=(str(o.id),ip)
                        return HostAttr(Newrequest)
                        #return HttpResponse(u'增加%s@%s成功!<br>%s'%(user,ip,s))
                    else:
                        return HttpResponse(u"不能设置公钥！<br>%s"%str(s))
                return HttpResponse(u'<h2 style="color:red">增加%s@%s出错!</h2>'%(user,ip))
        elif  hid and action=="EditHost" :
                try:
                    o=hosts.objects.get(id=hid)
                    if alias:o.alias=alias
                    if password:o.password=password
                    if user:o.user=user
                    if ip:o.ip=ip
                    if port:o.port=int(port)
                    o.group=group.rstrip(',')+',' if group else ''
                    if describe:o.describe=describe
                    o.sshtype=sshtype
                    o.save()
                    SettingHostGroup()
                    return HttpResponse(u'修改%s@%s成功!'%(user,ip))
                    
                except:
                    return HttpResponse(u'修改%s@%s失败!'%(user,ip))			
        return HttpResponse('Not')
    if hid:
        o=hosts.objects.get(id=hid)
        alias,ip,port,user,group,describe=o.alias,o.ip,o.port,o.user,o.group,o.describe
        sudocheckbox=MakeCheckbox('sudo',u'sudo为root',True if o.sshtype==1 else False)
        button=[[u'修改主机',MakeURL(AddHost)+'?action=EditHost&hid=%s'%hid]]
    else:
        sudocheckbox=MakeCheckbox('sudo',u'sudo为root', False)
        button=[[u'增加主机',MakeURL(AddHost)+'?action=AddHost','load','']]
    return render_to_response('AddHost.html',locals())
    
def DelHost(request):
    '''
    删除主机
    '''
    Random=int(time.time()*100)
    action,Selects=GetPost(request,['action','checkbox'],[1])
    if action=="Del":
        if Selects:
            Selects=[x.split('__') for x in Selects] 
            for id in Selects:			   
                hosts.objects.filter(id=id[-1]).delete()
                fileobj.objects.filter(unitsid=id[-1]).delete()
            SettingHostGroup()
            return HttpResponse(u'删除成功!')
        else:
            return HttpResponse(u'NotHosts !')
    else:
        button=[[u'删除',MakeURL(DelHost)+u'?action=Del','load',u'所属的文件对象也会删除！','center',3]]
        return render_to_response('yw_Del.html',locals())
    
def AddHostGroup(request):
    '''
    增加主机组
    '''
    Random=int(time.time()*100)
    if request.method=="POST":
        hostgroupname,hostslist,describe=GetPost(request,['hostgroupname','checkbox','HostDescribe'])
        if hostgroupname :
            if not hostgroup.objects.filter(groupname=hostgroupname):
                    hostgroup.objects.create(groupname=hostgroupname,groupmembers='',grouodescribe=describe)
                    SettingHostGroup()
                    return HttpResponse(u'添加主机组[%s]成功!'%hostgroupname)
            else:
                return HttpResponse(u'添加主机组[%s]已存在!'%hostgroupname)
        else:	
            return HttpResponse(u'添加主机组[%s]失败!'%hostgroupname)
    button=[[u'增加主机组',MakeURL(AddHostGroup)]]
    return render_to_response('AddHostGroup.html',locals())
    
def DelHostGroup(request):
    '''
    删除主机组
    '''
    Random=int(time.time()*100)
    ajaxurl=request.path_info
    action,Selects=GetPost(request,['action','checkbox'],[1])
    if  action=="Del":
        if Selects:
                
                Selects=[x.split('__') for x in Selects] 
                for id in Selects:
                    if id[-3]==u'ALL':continue
                    for o in hosts.objects.filter(group__contains='%s,'%id[-3]):
                        o.group=re.sub(r'(^|,)%s,'%id[-3],',',o.group)
                        o.save()		   
                    hostgroup.objects.filter(id=id[-1]).delete()
                    fileobj.objects.filter(unitsid=id[-1]).delete()
                SettingHostGroup()
                return HttpResponse(u'删除成功!')
        else:
                return HttpResponse(u'NotHostGroup !')
    button=[[u'确定删除',MakeURL(DelHostGroup)+u'?action=Del','load',u'所属的文件对象也会删除！','center',3]]
    return render_to_response('yw_Del.html',locals())

def MakeHostCheckbox(group):
    checkboxlist=[]
    if group=="ALL":
        for o in hosts.objects.all():
            checkboxlist.append(MakeCheckbox(o.id,o.ip,False))
    else:
        for o in hosts.objects.filter(group__contains='%s,'%group):
            checkboxlist.append(MakeCheckbox(o.id,o.ip,False))
    return checkboxlist

def ShowGroupHosts(request):
    '''
    显示组里主机
    '''
    group=request.GET.get('group','')
    if group:	
        return HttpResponse(MakeTable(['',''],MakeHostCheckbox(group)))
    return HttpResponse('None')
    
def AddGroupHost(request):
    '''
    增加主机到组
    '''
    ajaxurl=request.path_info
    Hostgroupselect=hostgroup.GetHostGroup()
    Selects,GroupName=GetPost(request,['checkbox','SelectHostGroup'],[0])
    if GroupName:
        Selects=[x.split('__') for x in Selects] 
        try:
            g=hostgroup.objects.get(groupname=GroupName)
        except:
            return HttpResponse(u"没有这个组！")
        for id in Selects:
            if id[-1] not in g.groupmembers:
                g.groupmembers+=id[-1]+','
                g.save()
            h=hosts.objects.get(id=id[-1])
            if GroupName+',' not in h.group:
                h.group+=GroupName+','
                h.save()

        return HttpResponse(u'增加到主机组[%s]，成功!'%GroupName)

    button=[[u'增加到',MakeURL(AddGroupHost),'',''],
    ]
    return render_to_response('AddGroupHost.html',locals())


        
        
def HostGroupManage(request):
    '''
    主机组管理
    '''
    #Hostgroupselect=hostgroup.GetHostGroup()
    Random=int(time.time()*100)
    checkall=u'''管理<input type='checkbox' class='checkall' name='checkall''/>'''
    table={'hostgroup':['checkall','groupname','groupmembers','grouodescribe']}
    alias={u'主机组':[checkall,u'主机组名',u'成员',u'描述']}
    thcss=['width:80px','width:100px','width:100px','']
    T=Table(table,alias,thcss)
    
    for o in hostgroup.objects.all():
            checkbox=u'''<input type='checkbox' class='checkbox' name='checkbox' value='%s__%s__%s__%s__%s'/>'''%('hostgroup','groupname',o.groupname,'id',o.id)
            ajax1=MakeAjaxButton('a',MakeURL(HostGroupAttr)+'?gid=%s&group=%s'%(o.id,o.groupname),o.groupname,'load',Random)
            groupmembers=len([ x for x in o.groupmembers.split(',') if x])
            ajax2=MakeAjaxButton('a',MakeURL(ShowGroupHosts)+'?gid=%s&group=%s'%(o.id,o.groupname),u'查看成员[%s]'%groupmembers,'open',Random)
            td=[checkbox,ajax1,ajax2,o.grouodescribe]
            tdattr=['','','','class="EditTD text_left"']
            T.row_add(o.id,td,tdattr)	
    T.done()
    nosort=[True,0]#不排序的列
    button=[[u'增加主机组',MakeURL(AddHostGroup),'open'],
            [u'删除主机组',MakeURL(DelHostGroup),'load']]
    EditAjaxUrl=MakeURL(Modify)
    return render_to_response('yw_datatable.html',locals())
    

    
    
    
