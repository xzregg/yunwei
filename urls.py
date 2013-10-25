#coding:utf-8

from django.conf.urls.defaults import *
import os,sys,glob,stat ,time
import traceback
from admin.views import requires_login,returnIndex,index

from settings import UploadDir
from libs import html

#为apache 保证路径
path=os.path.dirname(__file__)
os.chdir(path)


from admin.models import user,views
from admin.views import Sha1Md5
if not user.objects.all():#生成默认账户admin
    user.objects.create(createuser='admin',loginname='admin',username='admin',usergroup='',password=Sha1Md5('admin'),permission='0')
    

autourl=['',
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/images/favicon.ico'}),
    (r'^$', 'admin.views.returnIndex',{'redirectUrl':html.MakeURL(index)}),
    (r'^login[/]?$', 'admin.views.login'),
    (r'^logout[/]?$', 'admin.views.logout'),
    (r'^get_check_code_image/$', 'admin.check_code.get_check_code_image'), #验证码  
    (r'^(static|media)/(?P<path>.*)$','django.views.static.serve',{'document_root':'static'}),#js和css的静态文件
    (r'^%s/(?P<path>.*)$'%UploadDir,'libs.sendfile.download',{'document_root':'%s'%UploadDir}),#文件下载
]


def GetPyFileFunc(Dirlist):
    import re,inspect
    from libs import importlib
    PyFileList=[ os.path.join(dirpath,filename)  for dir in Dirlist if os.path.isdir(dir) for dirpath, dirs, files in os.walk(dir) for filename in files if  filename.endswith('.py')  ]
    funcdict={}                            
    for File in PyFileList:
        try:
            DjangoFuncList=[]
            f=open(File,'rb')
            for line in f:
                ret=re.search('^def(.*)\(request.*', line)
                if ret:
                    FuncName=ret.group(1).lstrip().rstrip()#获取文件内的Function
                    DjangoFuncList.append(FuncName)#找到django的函数
            if DjangoFuncList:#有
                    P_M=File.rstrip('py').replace(os.sep,'.').lstrip('.').rstrip('.')#生成目录.模块的字符串
                    Module=importlib.import_module(P_M)##载入模块
                    for FuncName in DjangoFuncList:
                        Func=getattr(Module,FuncName)
                        P_M_F=P_M+'.'+FuncName
                        funcdict[P_M_F]=Func	
        except:
            traceback.print_exc()
            continue
        finally:
            f.close()			
    return funcdict

def MakeURL(viewsdict):
    stime=time.time();autourl=[]
    views.objects.filter(loadcheck=1).update(loadcheck=0)#将所有的视图记录设置为false
    for k,v in viewsdict.iteritems():
            view=views.objects.filter(viewname=k)#数据库里找视图
            if view:#找到的话把视图对应的url加上
                view=view[0]
                view.loadcheck=1
                view.save()
                accessurl=view.accessurl
                autourl.append(('%s'%view.viewurl,requires_login(v,view.viewname)))
            else:#数据库没有记录,插入记录
                Title=v.__doc__.split('\n')[1].lstrip().rstrip() if v.__doc__ else k
                displaytype=1 if Title in DefaultShow else 0;#默认全部功能不显示
                x=k.split('.')
                viewurl=[ x[o] for o in (0,-2,-1)]
                defaultgroup=viewurl[0]
                accessurl='/%s/'%'/'.join(viewurl)
                viewurl=r'^%s.*$'%'/'.join(viewurl)
                o=views.objects.create(title=Title,accessurl=accessurl,viewurl=viewurl,viewname=k,permission=0,groupname=defaultgroup,loadcheck=1,displaytype=displaytype)
                o.permission=o.id
                o.save()
                autourl.append((viewurl,requires_login(v,k)))

    #views.objects.filter(loadcheck=0).delete()#删除不存在的视图
    etime=time.time()
    print '-'*20+'Make URL 完成,用时%.1f'%(etime-stime)+'-'*20
    autourl.append(('^.*','admin.views.ErrorRedirect'))
    return autourl
#安装app的views目录
from settings import INSTALLED_APPS,DefaultShow
viewsdict=GetPyFileFunc(INSTALLED_APPS)
urlpatterns=patterns(*tuple(autourl+MakeURL(viewsdict)))


