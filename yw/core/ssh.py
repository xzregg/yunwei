#coding:utf-8


import pexpect
import traceback,sys,re
import socket,os,time
import paramiko


_ScriptRootDir='/tmp/'

def GetParamikoPrivateKey(file):
    return paramiko.RSAKey.from_private_key_file(file)

Pk_path=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'rsa_key')
Pk_file=os.path.join(Pk_path,'id_rsa')
PrivateKey=GetParamikoPrivateKey(Pk_file)


def ssh_pexcept(host,port,user,password,sudo,timeout=60,title=True,cmd='id'):
    stime=time.time()
    s=[];cmd=cmd.replace('\r\n','\n')
    timeout=int(timeout)
    cmd=cmd.replace('\r\n','\n')#替换换行符号
    # 为 ssh 命令生成一个 spawn 类的子程序对象.
    child = pexpect.spawn('ssh  -t -o StrictHostKeyChecking=no -p %s %s@%s' % (port,user,host))
    #获取命令执行结果
    cmd='%s  echo Rnum:0' % cmd  if cmd.endswith(r'&') else '%s ; echo Rnum:$?' % cmd
    s.append('[%s@%s] -e- Run Cmd: ' % (user,host) if title else '')
    while True:
                i=child.expect(['.*assword:','.*[$#>]',pexpect.EOF,pexpect.TIMEOUT],timeout=timeout)
                if i==0:
                        child.sendline(password)
                        #print '使用密码登录'
                elif i==1:
                        if sudo:
                                child.sendline('sudo su -')
                                child.expect('.*#',timeout=timeout)
                        child.sendline(cmd.encode('utf-8'))
                        child.expect('Rnum:[\d]+',timeout=timeout*2)
                        t=child.before.decode('utf-8','ignore')+child.after.decode('utf-8','ignore')+'\n'
                        t=re.sub('\[[\d]+;[\d]+m|\[[\d]{0,}m','',t)#替换终端特殊字符
                        s.append(t)
                        child.sendline('exit')
                        child.sendline('exit')
                        child.expect(pexpect.EOF)
                        RetCode=0
                        break
                else:
                        #print 'Connect %s@%s timeout!' % (user,host)
                        s.append('\nConnect %s@%s err or timeout!\n' % (user,host))
                        RetCode=2
                        break
    if not title:
        s='\n'.join(s[1].split('\n')[1:-1])
    etime=time.time()
    t=u'%.1f s'%(etime-stime)
    return (RetCode,''.join(s),t)

def GetSshPubkeyCMD(user,overwrite=False):
    pubssh1=open(os.path.join(Pk_path,'id_rsa.pub'),'rb').read()
    pubssh2=open(os.path.join(Pk_path,'id_rsa_ssh2.pub'),'rb').read()
    _append = '>' if overwrite else '>>'
    ShellText='''if which ssh2 >/dev/null 2>&1;then
    {{
     umask 077 && mkdir -pv ~{user}/.ssh2; sed -i  '/yw_rsa_ssh2.pub/d'	~{user}/.ssh2/authorization;echo 'Key yw_rsa_ssh2.pub' {append} ~{user}/.ssh2/authorization;echo '{pubssh2}' {append} ~{user}/.ssh2/yw_rsa_ssh2.pub && chown -R {user} ~{user}/.ssh2/
    }} > /dev/null && mkdir -p /tmp/yw && echo -e 'Set SSH2 PublicKey OK !'
else
    {{
    umask 077 && mkdir -pv ~{user}/.ssh; echo '{pubssh1}' {append} ~{user}/.ssh/authorized_keys &&chown -R {user} ~{user}/.ssh/
    }} > /dev/null && mkdir -p /tmp/yw && echo -e 'Set SSH PublicKey OK !'
fi'''.format(user=user,pubssh2=pubssh2,pubssh1=pubssh1,append=_append)
    return ShellText

def CheckCMD(CMD):
    cmd=CMD.split()

    point=0
    for s in cmd:
        if s=='/' or s.find('rm') >=0 or s=='/*' or s=='*':
            point+=1
    
    return False if point>2 else True

                    
class Host(paramiko.SSHClient):
    def __init__(self,host,port,user,password,sudo,timeout=30,privatekey=PrivateKey):
        '''
        @timeout 为连接超时
        '''
        paramiko.SSHClient.__init__(self)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host=host
        self.port=int(port)
        self.user=user.rstrip().lstrip()
        self.password=password
        self.sudo=sudo
        self.timeout=int(timeout)
        self.key=privatekey
        self.scriptroot=_ScriptRootDir
        #paramiko.util.log_to_file('paramiko.log')
    
    def __str__(self):
        return '%s@%s'%(self.user,self.host)
        
    def _Connect(method):#执行方法前都先连接到主机
        def Action(self,*args,**kwargs):
            stime=time.time()
            try:
                self.connect(self.host,self.port,self.user,self.password,pkey=self.key,timeout=self.timeout)
                c,r=method(self,*args, **kwargs)#每个方法都返回一个元组
                RetCode=c
            except socket.timeout:
                traceback.print_exc()
                r='Connect [%s@%s] Timeout!\n'% (self.user,self.host)
                RetCode=2
            except:
                #traceback.print_exc()
                #print sys.exc_info()
                r='Connect [%s@%s] Error!\n%s'% (self.user,self.host,str(sys.exc_info()))
                RetCode=555
            finally:
                self.close()
                etime=time.time()
                t=u'%.1f s'%(etime-stime)
            return (RetCode,r,t)
        return Action
    
    def _pexcept(method):
        def Action(self,*args,**kwargs):
            c,s,t=method(self,*args,**kwargs)
            if c==555:#不支持paramiko连接，用pexcept
                return ssh_pexcept(self.host,self.port,self.user,self.password,self.sudo,self.timeout,*args,**kwargs)
            else:
                return (c,s,t)
        return Action
        
    @_pexcept
    @_Connect
    def RunCMD(self,title=True,cmd='id'):
        return self._runcmd(title,cmd)
    
    def _runcmd(self,title=True,cmd='id',redirect=''):#执行命令
            if not CheckCMD(cmd):
                return (3,"You can't run [%s]"%cmd)
            
            s=[];cmd=cmd.replace('\r\n','\n').rstrip('\n')
            if redirect:
                cmd='%s %s'%(cmd.rstrip(r'&'),redirect)
            elif cmd.endswith(r'&') and cmd.find('>/')<0 :
                cmd='%s %s &'%(cmd.rstrip(r'&'),'>/dev/null') 
            
            Retcmd='' if cmd.endswith(r'&') else ';echo Rnum:$?'
            cmd = '%s %s'%(cmd.rstrip('\n').rstrip(';'),Retcmd)
            s.append('[%s@%s] -p- Run : %s\n' % (self.user,self.host,cmd) if title else '')
            if self.sudo:
                cmd=u'''sudo su - -c "%s"''' % cmd.replace(r'"',r'\"').replace(r'$',r'\$')
            stdin, stdout, stderr = self.exec_command(cmd.encode('utf-8'),bufsize=-1,timeout=self.timeout*5)#处理时间超时

            out=stdout.read().decode('utf-8','ignore')
            err=stderr.read().decode('utf-8','ignore')
            s.append(err+out)
            try:
                sp=s[-1].rfind('Rnum')
                if err:
                    RetCode=s[-1][sp:].split(':')[1]
                    RetCode=int(RetCode.split()[0])	
                else:
                    RetCode=0
                s[-1]=s[-1][:sp] if not title else s[-1]
            except:
                RetCode=1
                print s
                traceback.print_exc()
            return (RetCode,''.join(s))
            
    @_Connect		
    def RunScript(self,title=True,script='',savepath='',daemon=False,scripttype=''):
            savepath=savepath or self.scriptroot
            Shell=scripttype+' ' if scripttype else './'
            ScriptPathFile=script.split(' ')[0]#脚本绝对路径
            if not os.path.isfile(ScriptPathFile):
                return (3,'Not file!')
            ScriptFile=os.path.basename(ScriptPathFile)#脚本名
            sp=script.find(ScriptFile)
            ScriptOption=script[sp:]#脚本名加参数
            SaveScriptPath=os.path.join(savepath,ScriptFile)
            
            sftp=self.open_sftp()
            try:
                sftp.mkdir(os.path.dirname(SaveScriptPath))
            except:
                pass
            sftp.put(ScriptPathFile,SaveScriptPath)#传脚本文件
            sftp.chmod(SaveScriptPath,0744)#改权限
            
            ScriptLog=os.path.join(savepath,'%s_daemon'%ScriptFile)#后台记录文件
            Daemon='';info=''
            if daemon:
                Daemon=' >%s 2>&1 &'%ScriptLog
                info='You can run "tail %s" see the script run info!'%ScriptLog
            cmd='cd %s;%s%s'%(savepath,Shell,ScriptOption)
            c,s=self._runcmd(title,cmd,redirect=Daemon)#执行脚本
            s+=info if daemon else ''
            return (c,s)
            
    def SetPublicKey(self,overwrite=False):
        CMD=GetSshPubkeyCMD(self.user,overwrite)
        c,s,t=self.RunCMD(False,CMD)
        return c,'[%s@%s]\n'% (self.user,self.host)+'\n'.join(s.split('\n')[-2:]),t

        
    @_Connect	
    def PutFile(self,localpath,remotepath,aftercmd,md5=''):#上传文件
        sftp=self.open_sftp()
        try:
            sftp.mkdir(os.path.dirname(remotepath))
        except:
            pass
        lsize=os.path.getsize(localpath)
        r=sftp.put(localpath,remotepath)
        rsize=r.st_size
        cmd = aftercmd or 'ls -l %s'%remotepath
        cmd='md5sum %s' if md5 else cmd
        c,s,t=self._runcmd(title=False,cmd=cmd,Rnum=False)
        if md5:
            c=1 if md5!=s.split()[0] else c
            s=md5+' '+s 
        return c,s,t
        
    def GetCPUinfo(self):
        cmd=r'''awk '/physical id/{++p} \
/cpu MHz/{sub(/.*:/,"",$0);cm=$0} \
/cache size/{sub(/.*:/,"",$0);cs=$0} \
/model name/{sub(/.*:/,"",$0);cpu=$0} \
/cpu cores/{++cc} \
/processor/{pro++}
END{print \
"CPU:"cpu \
"\nMHz:"cm \
"\nCache:"cs \
"\nProcessor:"pro
} '  /proc/cpuinfo '''
        return self.RunCMD(False,cmd)
        
        
    @_Connect
    def GetFile(self,remotepath,localpath,beforcmd):#下载文件
        if beforcmd:
            self._runcmd(title=False,cmd=beforcmd,Rnum=False)
        sftp=self.open_sftp()
        r=sftp.stat(remotepath)
        rsize=r.st_size
        sftp.get(remotepath,localpath)
        lsize=os.path.getsize(localpath)
        if lsize==rsize:
            return (0,'Get %s size:[%s] OK!'%(remotepath,lsize))
        else:
            return (1,'Get %s size:[%s] Error!'%(remotepath,rsize))
    
    def filecall(self,a,b):
        print a,b
        
    
    @_Connect
    def FileOBJ(self,action,path,data='',bcmd='',acmd=''):
        sftp=self.open_sftp()
        path=path.rstrip()
        if bcmd:
            self._runcmd(title=False,cmd=bcmd)
        if action=="read":
            f=sftp.file(path,'rb')
            return (0,f.read())
        elif action=="write":
            f=sftp.file(path,'wb').write(data)
        elif action=="append":
            f=sftp.file(path,'ab').write(data)
        Acmd=acmd or 'ls -l %s'%path
        return self._runcmd(title=False,cmd=Acmd)
            
            


    
    
    
