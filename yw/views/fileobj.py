# coding:utf-8

from ..Global import *
import os
import sys
import glob
import re
import json
import time

from ..models import fileobj, hosts
from .control import GetCmdRet


def GetFileObjPath(name, ishost=True):
    #from ..Global import FileObjectsDir
    obj = 'hosts' if ishost else 'groups'
    path = os.path.join(FileObjectsDir, obj, name)
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


def Iptables(request):
    '''
    防火墙设置
    '''
    gid, group, hid, ip = GetPost(request, ['gid', 'group', 'hid', 'ip'])
    isgroup, unitsid, mark = (
        False, hid, ip) if hid and ip else (True, gid, group)
    filename = u'Iptables'
    rpath = '/etc/iptables.sh'
    # 检查是否有记录cron,没就创建
    o, create = fileobj.objects.get_or_create(
        unitsid=unitsid, filename=filename)
    if create:  # 新创建
        if hid:
            edittype = False
            bcmd = ''
            acmd = 'iptables -nvL'
            port = hosts.GetHost('id', hid).port
        else:  # 主机组默认为追加
            port = 22
            edittype = True
            bcmd = u"sed -i '/^#<yw_%s>/,/^#<\/yw_%s>/d' %s" % (mark,
                                                                mark, rpath)
            acmd = u"iptables -nvL && sed -n '/^#<yw_%s>/,/^#<\/yw_%s>/p' %s" % (mark,
                                                                                 mark, rpath)
        o.isgroup, o.rpath, o.edittype, o.bcmd, o.acmd = isgroup, rpath, edittype, bcmd, acmd
        # 默认的防火墙脚本

        o.text = u'''
#!/bin/sh
/sbin/modprobe ip_tables
/sbin/modprobe iptable_filter
/sbin/modprobe iptable_nat
/sbin/modprobe ip_conntrack
/sbin/modprobe ip_conntrack_ftp
#flush
iptables -F;iptables -X;iptables -t nat -F
iptables -P OUTPUT ACCEPT
iptables -N firewall
iptables -A INPUT -j firewall
iptables -A FORWARD -j firewall
#允许访问外部
iptables -A firewall  -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A firewall -i lo -j ACCEPT
#ssh
#iptables -A firewall -p tcp --dport %s -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
		''' % port
        o.save()
    NewRequest = Myrequest(request)
    rP = NewRequest.POST
    rP['fid'] = str(o.id)
    rP['rpath'] = o.rpath
    return FileOBJ(NewRequest)


def Cron(request):
    '''
    计划任务
    '''
    gid, group, hid, ip = GetPost(request, ['gid', 'group', 'hid', 'ip'])
    isgroup, unitsid, mark = (
        False, hid, ip) if hid and ip else (True, gid, group)
    filename = u'Cron'
    rpath = '/tmp/yw_%s_cron' % mark
    # 检查是否有记录cron,没就创建
    o, create = fileobj.objects.get_or_create(
        unitsid=unitsid, filename=filename)
    if create:  # 新创建
        if hid:
            edittype = False
            Gbcmd = ''
            Gacmd = ''
        else:  # 主机组默认为追加
            edittype = True
            Gbcmd = u"&& sed -i '/^#<yw_%s>/,/^#<\/yw_%s>/d' %s" % (mark,
                                                                    mark, rpath)
            Gacmd = u''
            # Gacmd=u"&& sed -n '/^#<yw_%s>/,/^#<\/yw_%s>/p'
            # %s"%(mark,mark,rpath)
        bcmd = 'crontab -l > %s ' % rpath + Gbcmd
        acmd = 'crontab %s && crontab -l ' % rpath + Gacmd
        o.isgroup, o.rpath, o.edittype, o.bcmd, o.acmd = isgroup, rpath, edittype, bcmd, acmd
        o.save()
    NewRequest = Myrequest(request)
    rP = NewRequest.POST
    rP['fid'] = str(o.id)
    rP['rpath'] = o.rpath
    return FileOBJ(NewRequest)


def FileOBJ(request):
    '''
    文件对象
    '''
    stime = time.time()
    Random = int(time.time() * 100)
    hid, ip, gid, group, HostsId, fid, action, filename, rpath, edittype, FileObjText, AfterCMD, BeforeCMD = GetPost(
        request,
        ['hid', 'ip', 'gid', 'group', 'checkbox', 'fid', 'action', 'filename', 'rpath', 'edittype', 'FileObjText', 'AfterCMD', 'BeforeCMD'], [4])
    if fid:
        o = fileobj.objects.get(id=fid)
        HostsId = [x.split('__')[-1]
                   for x in HostsId if x] if not hid else [hid]
        mark = ip or group
        if action == "Del":
            o.delete()
            return HttpResponse(u'%s[%s]删除成功!' % (o.filename, o.rpath))
        elif action == "Modify" and request.method == "POST":  # 保存到数据库
            edittype = True if edittype == "append" else False
            o.filename = filename
            o.edittype = edittype
            o.rpath = rpath
            o.text = FileObjText.encode('utf-8')
            o.bcmd = BeforeCMD
            o.acmd = AfterCMD
            o.save()
            return HttpResponse(u'[%s]保存成功!' % filename)
        elif action == "Sync" and request.method == "POST":  # 写文件
            FileObjText = FileObjText.replace('\r\n', '\n')
            if edittype == "append":
                FileObjText = u'\n#<yw_%s>\n' % mark + \
                    FileObjText + u'\n#</yw_%s>' % mark
            return HttpResponse(GetCmdRet('FileOBJ', HostsId, group, 0, 30, (edittype, rpath, FileObjText.encode('utf-8'), BeforeCMD, AfterCMD)))
        else:  # 读取
            EditType = 1 if o.edittype else 0
            isEdit = True
            if hid:
                Ho = hosts.GetHost('id', hid)
                HostObj = Host(Ho.ip, Ho.port, Ho.user,
                               Ho.password, Ho.sshtype, 10)
                # 主机直接读远程的
                c, FileObjText, t = HostObj.FileOBJ(
                    'read', o.rpath, '', o.bcmd)
                etime = time.time()
                UseTime = u'读用时: %.1f 秒' % (etime - stime)
            else:
                FileObjText = o.text

            Urlopt = u'?hid=%s&ip=%s' % (
                hid, ip) if hid and ip else u'?gid=%s&group=%s' % (gid, group)
            button = [
                [u'保存本地', MakeURL(FileOBJ) + Urlopt + '&action=Modify&fid=%s&rpath=%s' %
                 (fid, rpath), 'load', u'保存到数据！', 'center', 3],
                [u'同步远程', MakeURL(FileOBJ) + Urlopt + '&action=Sync&fid=%s&rpath=%s' %
                 (fid, rpath), 'load', u'同步对端!', 'center']
            ]
            return render_to_response('AddFileOBJ.html', locals())


def AddFileOBJ(request):
    '''
    增加文件对象
    '''
    Random = int(time.time() * 100)
    hid, ip, gid, group, filename, rpath, edittype = GetPost(request,
                                                             ['hid', 'ip', 'gid', 'group', 'filename', 'rpath', 'edittype'])
    if ((hid and ip) or (gid and group)) and request.method == "POST" and filename and rpath and edittype:
        isgroup, unitsid, mark = (
            False, hid, ip) if hid and ip else (True, gid, group)
        if edittype == "append":
            edittype = True
            bcmd = "sed -i '/^#<yw_%s>/,/^#<\/yw_%s>/d' %s" % (mark,
                                                               mark, rpath)
            acmd = "sed -n '/^#<yw_%s>/,/^#<\/yw_%s>/p' %s" % (mark,
                                                               mark, rpath)
        else:
            edittype, bcmd, acmd = (False, '', '')
        if fileobj.objects.filter(unitsid=unitsid, filename=filename):
            return HttpResponse(u'[%s]已存在!' % filename)
        o = fileobj.objects.create(isgroup=isgroup, unitsid=unitsid,
                                   filename=filename, edittype=edittype, rpath=rpath, bcmd=bcmd, acmd=acmd)
        NewRequest = Myrequest()
        rP = NewRequest.POST
        rP['hid'], rP['ip'], rP['gid'], rP['group'] = hid, ip, gid, group
        rP['fid'] = str(o.id)
        rP['rpath'] = o.rpath
        return FileOBJ(NewRequest)

    Urlopt = u'?hid=%s&ip=%s' % (
        hid, ip) if hid and ip else u'?gid=%s&group=%s' % (gid, group)
    button = [[u'增加', MakeURL(AddFileOBJ) + Urlopt, 'load'],
              ]
    return render_to_response('AddFileOBJ.html', locals())


def ShowFileOBJ(request):
    '''
    主机文件对象
    '''
    Random = int(time.time() * 100)
    gid, group, hid, ip = GetPost(request, ['gid', 'group', 'hid', 'ip'])
    unitsid = gid or hid
    Urlopt = u'?hid=%s&ip=%s' % (
        hid, ip) if hid and ip else u'?gid=%s&group=%s' % (gid, group)
    FileObjs = []
    for o in fileobj.objects.filter(unitsid=unitsid):
        FileObjs.append(
            MakeAjaxButton(
                'a', MakeURL(FileOBJ) + Urlopt + '&fid=%s&rpath=%s' %
                (o.id, o.rpath), o.filename, 'load', Random, '', 'center'))
        FileObjs.append(
            MakeAjaxButton(
                'a', MakeURL(FileOBJ) + Urlopt + '&fid=%s&rpath=%s&action=Del' %
                (o.id, o.rpath), u'删除', 'load', Random, u'删除', 'center', 3))
    T = MakeTable(['', ''], FileObjs)
    button = [[u'增加文件对象', MakeURL(AddFileOBJ) + Urlopt, 'load'],
              ]
    return render_to_response('ShowFileOBJ.html', locals())
