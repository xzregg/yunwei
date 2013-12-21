# coding:utf-8
from ..Global import *
import os
import time
import json
import datetime


from libs.html import *
from ..models import onekeys, hostgroup
import urllib
import urllib2


def ShowOneKey(request):
    '''
    查看一键
    '''
    Random = int(time.time() * 100)
    OneKeyLabel = {}
    for o in onekeys.objects.all():
        OneKeyLabel.setdefault(o.onekeygroup, [])
        OneKeyButton = {
            'ajaxurl': MakeURL(RunOneKey) + u'?Oid=%s&onekeyname=%s' % (o.id, o.onekeyname),
            'title': o.onekeydescribe.replace('\n', '<br>'),
            'method': 'load',
            'html': o.onekeyname
        }
        OneKeyLabel[o.onekeygroup].append(OneKeyButton)
    return render_to_response('ShowOneKeys.html', locals())


def urldecode(url):
    '''
    URL返回一个字典
    '''
    d = {}
    for o in url.split('&'):
        if o.find('=') > 0:
            k, v = o.split('=')
            d.setdefault(k, [])
            d[k].append(urllib.unquote_plus(v.encode('utf-8')).decode('utf-8'))
    return d


def urltorequest(d):
    r = Myrequest()
    r.POST = d
    return r


def RunOneKey(request):
    '''
    运行一键
    '''
    Random = int(time.time() * 100)
    from control import Interface
    Oid, action = GetPost(request, ['Oid', 'action'])
    o = onekeys.objects.get(id=Oid)
    if action == u'RunOneKey':
        if o.checktype == 1:
            verify = request.session.get('verify', '1')
            checkcode = request.POST.get('check', '2')
            if not verify == checkcode:
                return HttpResponse(u'验证码不正确！')
        Ret = []
        for i, v in enumerate(o.onekeyurl.split('\n')):
            d = urldecode(v)
            myrequest = urltorequest(d)
            r = Interface(myrequest)
            Ret.append([i + 1, r.content])
        return render_to_response('OneKeyRet.html', locals())
    if o.checktype == 1:
        RunOneKeyCheck = True
    button = [[u'运行[%s]' % o.onekeyname, MakeURL(
        RunOneKey) + u'?action=RunOneKey&Oid=%s&onekeyname=%s' % (o.id, o.onekeyname), 'load', u'运行一键', 'center'], ]
    OneKeyDescribe = o.onekeydescribe.replace('\n', '<br>')
    return render_to_response('RunOneKey.html', locals())

# print a.content


def OneKeyManage(request):
    '''
    一键管理
    '''
    Random = int(time.time() * 100)
    checkall = u'''管理<input type='checkbox' class='checkall' name='checkall'/>'''
    table = {'onekeys': ['checkall', 'onekeyname',
                         'onekeygroup', 'onekeydescribe', 'creater', 'createtime']}
    alias = {u'主机组': [checkall, u'一键名', u'目标组', u'描述', u'创建者', u'创建时间']}
    thcss = ['', '', '', 'width:400px', '']
    T = Table(table, alias, thcss)
    for o in onekeys.objects.all():
        checkbox = u'''<input type='checkbox' class='checkbox' name='checkbox' value='%s__%s__%s__%s__%s'/>''' % (
            'onekeys', 'onekeyname', o.onekeyname, 'id', o.id)
        ajax = MakeAjaxButton(
            'a', '/yw/onekey/EditOneKey/?Oid=%s&onekeyname=%s' %
            (o.id, o.onekeyname), u'修改', 'open', Random)
        ajax1 = MakeAjaxButton(
            'a', '/yw/onekey/RunOneKey/?Oid=%s&onekeyname=%s' %
            (o.id, o.onekeyname), u'运行', 'load', Random)
        td = [checkbox + ajax + ajax1, o.onekeyname, o.onekeygroup,
              o.onekeydescribe, o.creater, o.createtime]
        tdattr = ['', '', '', '', '']
        T.row_add(o.id, td, tdattr)
    T.done()
    nosort = [True, 0]  # 不排序的列
    button = [[u'增加一键', '/yw/onekey/AddOneKey/', 'open'],
              [u'删除一键', '/yw/onekey/DelOneKey/', 'load'],
              [u'执行命令', '/yw/control/RunCmd/', 'load'],
              [u'执行脚本', '/yw/control/RunScript/', 'load']
              ]
    # EditAjaxUrl='/yw/hosts/Modify/'
    return render_to_response('yw_datatable.html', locals())


def EditOneKey(request):
    '''
    编辑一键
    '''
    Random = int(time.time() * 100)
    Oid = request.GET.get('Oid', '')
    if request.method == 'POST':
        onekeyname, onekeyurl, onekeygroup, checktype, onekeydescribe = GetPost(
            request,
            ['onekeyname', 'onekeyurl', 'onekeygroup', 'checktype', 'onekeydescribe'], [1])
        onekeydescribe = onekeydescribe.replace('\r\n', '\n')
        Creater = request.session['username']
        Createtime = datetime.datetime.now()
        if onekeyname and onekeyurl and Oid:
            onekeyurl = '\n'.join([x for x in onekeyurl if x])
            onekeys.objects.filter(
                id=Oid).update(onekeyname=onekeyname, checktype=checktype, onekeyurl=onekeyurl,
                               onekeygroup=onekeygroup, creater=Creater, onekeydescribe=onekeydescribe, createtime=Createtime)
            return HttpResponse('修改一键成功！')
        else:
            return HttpResponse('修改一键失败！')
    if Oid:
        o = onekeys.objects.get(id=Oid)
        OneKeyUrl = []
        for u in o.onekeyurl.split('\n'):
            OneKeyUrl.append(u)
        button = [[u'确定修改', request.get_full_path(), 'load'], ]
        Hostgroupselect = hostgroup.GetHostGroup()
    return render_to_response('AddOneKey.html', locals())


def MakeOneKeyInput():
    input = []
    input.append(
        MakeSelect('cmdtimeout', ['10', '30', '60'], ['10', '30', '60'], 0, u'连接超时'))
    input.append(
        MakeSelect('thread', ['5', '50', '200'], ['5', '50', '200'], 0, u'线程'))
    input.append(MakeSelect('sshtitle', [u'否', u'是'], ['0', '1'], 0, u'头信息'))
    input.append(MakeSelect('daemon', [u'否', u'是'], ['0', '1'], 0, u'后台'))
    input.append('<br>')


def AddOneKey(request):
    '''
    增加一键
    '''
    Random = int(time.time() * 100)
    if request.method == 'POST':
        onekeyname, onekeyurl, onekeygroup, checktype, onekeydescribe = GetPost(
            request,
            ['onekeyname', 'onekeyurl', 'onekeygroup', 'checktype', 'onekeydescribe'], [1])
        onekeydescribe = onekeydescribe.replace('\r\n', '\n')
        Creater = request.session['username']
        Createtime = datetime.datetime.now()
        if onekeyname and onekeyurl:
            onekeyurl = '\n'.join([x for x in onekeyurl if x])
            if onekeys.objects.filter(onekeyname=onekeyname):
                return HttpResponse(u'一键[%s]已存在' % onekeyname)
            onekeys.objects.create(
                onekeyname=onekeyname, checktype=checktype, onekeyurl=onekeyurl,
                onekeygroup=onekeygroup, creater=Creater, onekeydescribe=onekeydescribe, createtime=Createtime)
            return HttpResponse('增加一键成功！')
        else:
            return HttpResponse('增加一键失败！')
    Hostgroupselect = hostgroup.GetHostGroup()
    OneKeyUrl = ['']
    button = [[u'确定增加', request.path_info, 'load'], ]
    return render_to_response('AddOneKey.html', locals())


def DelOneKey(request):
    '''
    删除一键
    '''
    Random = int(time.time() * 100)
    ajaxurl = request.path_info
    action, Selects = GetPost(request, ['action', 'checkbox'], [1])
    if action == "Del":
        if Selects:
            Selects = [x.split('__') for x in Selects]
            for id in Selects:
                onekeys.objects.filter(id=id[-1]).delete()
            return HttpResponse(u'删除一键成功!')
        else:
            return HttpResponse(u'NotOneKeys !')
    else:
        button = [[u'删除', MakeURL(DelOneKey) + u'?action=Del', 'load', u'删除']]
        return render_to_response('yw_Del.html', locals())
