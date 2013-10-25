#coding:utf-8
from django.db import models
from libs.html import *
from Global import ScriptDir
import os

class hosts(models.Model):
	alias=models.CharField(max_length=100)
	ip=models.IPAddressField()
	port=models.IntegerField()
	user=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	group=models.CharField(max_length=100)
	describe=models.TextField(default='')
	sshtype=models.IntegerField(default=0)
	
	@classmethod
	def GetHost(cls,key,value):
		return cls.objects.get(**{key:value})

		
	@classmethod
	def GetHostObjs(cls,HostsId,group):
		'''返回主机对象'''
		hostobjs=[]
		if group:
			if group=="ALL":
				hostobjs=cls.objects.all()
			else:
				hostobjs=cls.objects.filter(group__contains=',%s,'%group)
			if not hostobjs:
					hostobjs=cls.objects.filter(ip=group)
		elif HostsId:
			for i in HostsId:
				o=cls.GetHost('id',i)
				hostobjs.append(o)
		return hostobjs

class hostgroup(models.Model):
	groupname=models.CharField(max_length=100)
	groupmembers=models.TextField(default='',verbose_name="主机组成员")
	grouodescribe=models.TextField(default='',verbose_name="主机组描述")
	
	@classmethod
	def GetHostGroup(cls):
		return [ o.groupname for o in cls.objects.all()]
	@classmethod
	def GetGroupHosts(groupname):
		return cls.objects.get(groupname=groupname).groupmembers
	
class fileobj(models.Model):
	isgroup=models.BooleanField(default=False,verbose_name="是否属于主机组")
	filename=models.CharField(max_length=200,verbose_name="文件名")
	unitsid=models.IntegerField(verbose_name="所属的主机id或这组id")
	edittype=models.BooleanField(default=False,verbose_name="修改方式,True为追加,False为覆盖")
	rpath=models.CharField(max_length=1000,verbose_name="远程主机的路径")
	bcmd=models.CharField(max_length=1000,default='',verbose_name="读改前运行的命令")
	acmd=models.CharField(max_length=1000,default='',verbose_name="修改后运行的命令")
	text=models.TextField(default='',verbose_name="文件内容")
	
	@staticmethod
	def MakeInput(Random,FileName,RPath,edittype,BeforeCMD,AfterCMD):
		edittype=0 if edittype else 1
		td=[]
		td+=[u'文件名:',MakeInput('text','filename',FileName,'width:100px')]
		td+=[u'文件路径:',MakeInput('text','rpath',RPath,'width:250px')+MakeAjaxButton('a','#',u'选择','load',Random),]
		td+=[u'编辑方式:',MakeRaio('edittype',['覆盖','追加'],['write','append'],edittype),]
		#td+=[u'读改前运行的命令:',MakeInput('text','BeforeCMD',BeforeCMD,'width:300px')]
		#td+=[u'修改后运行的命令:',MakeInput('text','AfterCMD',AfterCMD,'width:300px')]
		T=MakeTable(['',''],td)
		return T

class scripts(models.Model):
	scriptname=models.CharField(max_length=100,verbose_name="脚本名")
	scriptgroup=models.CharField(max_length=100,verbose_name="组")
	scriptdescribe=models.TextField(verbose_name="脚本用途")
	creater=models.CharField(max_length=20,verbose_name="创建者")
	createtime=models.DateTimeField(null=True,verbose_name="创建时间")
	scripttext=models.TextField(verbose_name="脚本内容")
	
	
	@classmethod
	def GetScriptPath(cls,Script,TmpScript=False):
		'''获取脚本路径'''
		ScriptFile=Script.split(' ')[0]
		BaseScriptFile=os.path.basename(ScriptFile)
		if ScriptFile.find(os.sep)<0:#不是绝对路径
			o=cls.objects.filter(scriptname=BaseScriptFile)
			if o:
				o=o[0]
				ScriptFile=os.path.join(ScriptDir,BaseScriptFile)
				open(ScriptFile,'wb').write(o.scripttext.encode('utf-8'))
				Script=os.path.join(ScriptDir,Script)
		if TmpScript and not os.path.isfile(ScriptFile):
				open('/tmp/TmpScript','wb').write(Script.encode('utf-8').replace('\r\n','\n'))
				Script='/tmp/TmpScript'
		return Script
	
	
class onekeys(models.Model):
	onekeyname=models.CharField(max_length=100,verbose_name="一键名称")
	onekeydescribe=models.CharField(max_length=200,verbose_name="一键用途")
	onekeytype=models.CharField(max_length=30,verbose_name="一键类型，命令 脚本")
	onekeygroup=models.CharField(max_length=30,verbose_name="一键组")
	onekeyurl=models.CharField(max_length=1000,verbose_name="一键类型url")
	creater=models.CharField(max_length=30,verbose_name="创建者")
	createtime=models.DateTimeField(null=True,verbose_name="创建时间")
	checktype=models.IntegerField(default=0,verbose_name="验证检测类型")


		

