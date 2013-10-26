#coding:utf-8
#定义数据库
from django.db import models,connection
from django.db.models import Q
from libs.timelib import *

class user(models.Model):
    username = models.CharField(max_length=100)
    loginname = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    contact = models.CharField(max_length=100,default='')
    usergroup = models.CharField(max_length=1000)
    createuser = models.CharField(max_length=100)
    logintime = models.DateTimeField(null=True)
    loginip = models.IPAddressField(null=True)
    permission = models.CharField(max_length=100)
    lock = models.BooleanField(default=False)
    
    @classmethod
    def UserGroupPermission(cls,uid):
        '''用户加组的权限并集'''
        o = cls.objects.filter(id=uid)
        if o:
            o = o[0]
        else:
            return 0
        if o.lock: return -1
        p = int(o.permission)
        if p == 0 :return p#管理员
        for g in o.usergroup.split(','):
            if g:
                Gobj = usergroup.objects.get(groupname=g)
                p |= int(Gobj.permission)
        return p

    @classmethod
    def ChangePermission(cls,Uid,viewslist):#改变用户权限
        o = cls.objects.get(id=Uid)
        o.permission = 0 if o.username == 'admin' else views.MakePermission(viewslist) 
        o.save()

    
class usergroup(models.Model):
    groupname = models.CharField(max_length=100)
    groupmembers = models.CharField(max_length=1000)
    permission = models.CharField(max_length=100)
    
    @classmethod
    def ChangePermission(cls,Gid,viewslist):#改变用户组权限
        cls.objects.filter(id=Gid).update(permission=views.MakePermission(viewslist))
        
    @classmethod
    def GetGroupMembers(cls,Gid):#获取组成员
        o = cls.objects.get(id=Gid)
        return o.groupmembers.split(',')
    
    @classmethod
    def DelUserGroup(cls,Gid):#删除用户组
        go = cls.objects.get(id=Gid)
        GroupName = go.groupname
        for o in user.objects.filter(usergroup__contains=GroupName):
            o.usergroup = o.usergroup.replace('%s,'%GroupName,'').replace(GroupName,'')
            o.save()
        go.delete()
        return GroupName

    @classmethod
    def ChangeGroupUser(cls,Gid,UserList):#修改组用户
        obj = cls.objects.get(id=Gid)
        obj.groupmembers = ','.join(UserList)
        obj.save()
        groupname = obj.groupname
        for userobj in user.objects.all():#
            userobj.usergroup = userobj.usergroup.replace('%s,'%groupname,'')
            if str(userobj.id) in UserList:
                userobj.usergroup += obj.groupname+','
            userobj.save()
        return obj.groupname
    
class views(models.Model):
    title = models.CharField(max_length=50,verbose_name="权限名")
    accessurl = models.CharField(max_length=50,verbose_name="访问URL")
    viewurl = models.CharField(max_length=50,verbose_name="DjangoURL")
    viewname = models.CharField(max_length=50,verbose_name="视图P_M_F")
    groupname = models.CharField(max_length=50,blank=True,verbose_name="菜单组名")
    permission = models.IntegerField(verbose_name="所需权限")
    displaytype = models.IntegerField(default=1,verbose_name="显示类型")#菜单显示
    logtype = models.IntegerField(default=0,verbose_name="是否记录")
    loadcheck = models.IntegerField(default=1,verbose_name="是否已检测")

    class Meta:
        ordering = ['groupname'] 
    
    @classmethod
    def AddPermission(cls,*t,**kv):#增加权限
        o = cls.objects.create(*t,**kv)
        o.permission = o.id
        o.save()
        
    @classmethod
    def ClearErrView(cls): #删除不存在的视图
        v = ''
        for o in cls.objects.filter(loadcheck=0):
            v += o.viewname + ','
            o.delete()
        return v
    
    @classmethod
    def DelPermission(cls,Pid):#删除权限
        cls.objects.filter(id=Pid).delete()
    @classmethod
    def ViewsLog(cls,Selects,logtype):#访问记录日志
        for id in Selects:
                cls.objects.filter(id=id).update(logtype=logtype)
    @classmethod
    def ViewsShow(cls,Selects,displaytype):#菜单显示
        for id in Selects:           
            cls.objects.filter(id=id).update(displaytype=displaytype)
            
    @classmethod
    def CheckViewPermission(cls,Selects,checkpermission):#检查视图权限
                for id in Selects:
                    o = cls.objects.get(id=id)
                    o.permission = o.id if checkpermission else 0
                    o.save()
    @staticmethod
    def _PaddingBin(string,Num):
       '''填充二进制'''
       if len(string) < Num:
           string = string.rjust(Num,'0')#补位
       str = ''
       for n,s in enumerate(string[::-1]):
               str += '1' if n == Num-1 else s
       return str[::-1]
    
    @classmethod
    def MakePermission(cls,viewidlist):
        '''生成权限'''
        BinPermission = '0'
        for vid in viewidlist:
            o = cls.objects.get(id=vid)
            BinPermission = cls._PaddingBin(BinPermission,o.permission)
        PermissionNumber = int(BinPermission,2)#返回一个10进制的数
        return str(PermissionNumber)
    
class logs(models.Model):
    who = models.CharField(max_length=100,verbose_name="操作者")
    logdatetime = models.DateTimeField(null=True,verbose_name="操作时间")
    title = models.CharField(max_length=50,verbose_name="权限名")
    info = models.CharField(max_length=500,verbose_name="操作键值")
    ip = models.IPAddressField(null=True,verbose_name="操作ip")
        
    @classmethod
    def SearchLog(cls,Page,ItemNum,Stime,Etime,text):
         std = StrTimeToDateTime
         startPos  =  (Page-1) * ItemNum
         endPos = startPos + ItemNum
         o = cls.objects.filter(logdatetime__range=(std(Stime or '1970-01-01 00:00:00'),std(Etime))).filter(Q(info__icontains=text)|Q(title__icontains=text)|Q(ip__icontains=text)|Q(who__icontains=text)).order_by('-id')
         Tol = o.count()
         return Tol,o[startPos:endPos]
        
    @staticmethod
    def Truncate():
        cursor  =  connection.cursor()
        cursor.execute('TRUNCATE TABLE admin_logs;')
        return True

#old------------------------------------------------------------   
    @staticmethod
    def GetCount(text):
        cursor  =  connection.cursor()
        sql = '''select count(id) from admin_logs where title like '%%%%%s%%%%' or info like '%%%%%s%%%%' '''%(text,text)
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        return count
        
    @staticmethod   
    def FilterOR(text,s,t,stime,etime):
        cursor  =  connection.cursor()
        sql = '''select * from admin_logs where (title like '%%%%%s%%%%' or info like '%%%%%s%%%%') and logdatetime >= '%s' and logdatetime <= '%s' order  by 'id' desc limit %s offset %s'''%(text,text,stime,etime,t,s,)
        cursor.execute(sql)
        return cursor.fetchall()
