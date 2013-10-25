#coding:utf-8

from ..Global import *
import os,time,random,json,os

import urllib,urllib2

from ..core.ssh import Host,Pk_path
from ..core.bf import xBF
from ..models import  hosts,scripts

from multiprocessing.managers import BaseManager
import Queue,os,sys
import threading,time,signal

def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'): 
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errorno, e.strerror)) 
        sys.exit(1) 
         
    os.chdir('/') 
    os.umask(0) 
    os.setsid() 
     
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errorno, e.strerror)) 
        sys.exit(1) 
         
    for f in sys.stdout, sys.stderr: 
        f.flush() 
     
    si = file(stdin, 'r') 
    so = file(stdout, 'a+') 
    se = file(stderr, 'a+', 0) 
    os.dup2(si.fileno(), sys.stdin.fileno()) 
    os.dup2(so.fileno(), sys.stdout.fileno()) 
    os.dup2(se.fileno(), sys.stderr.fileno()) 



class SharedProcess(BaseManager):
    def __init__(self,*t,**k):
        super(SharedProcess,self).__init__(*t,**k)
    def StartServer(self):
        def _CloseServer():
            return os.kill(os.getpid(),signal.SIGINT)
        self.q=Queue.Queue()
        self.register('CloseServer',callable=_CloseServer)
        self.register('get_queue',callable=lambda:self.q)
        daemonize()
        self.get_server().serve_forever()
#client method
    def CloseServer(self):
        self.register('CloseServer')
        self.connect()
        return self.CloseServer()
    def Q(self):
        self.register('get_queue')
        self.connect()
        return self.get_queue()


def server(request):
	'''
	测试服务器
	'''
    
	pid=os.fork()
        if pid:
            time.sleep(0.5)
            return HttpResponse(str(os.stat('/tmp/a')))
        else:
       	    SharedProcess('/tmp/a','a').StartServer()
	


#s=SharedProcess('/tmp/a','a')
if __name__=="__main__":
	pid=os.fork()
        if pid:
            os._exit(0)
        else:
       	    SharedProcess('/tmp/a','a').StartServer()

