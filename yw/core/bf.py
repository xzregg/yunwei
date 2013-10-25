#!/usr/bin/env python
# coding:utf-8
#  并发进程的类 by xzr

import multiprocessing
import time
import subprocess
import os,sys
import traceback
import threading
#import Queue

def get_now():
	tf='%Y-%m-%d %H:%M:%S'
	return time.strftime(tf,time.localtime())

_Cpus=multiprocessing.cpu_count()
class xBF:
		'''
			一个并发进程线程的类
			@f 函数
			@tuplist 函数的参数列表
			@bfn 限制的任务数
			@threadnums 每个进程开启的线程数
			@printret 打印结果
		'''
		def __init__(self,f=None,tuplist=[],bfn=0,printret=False):
				self.cpus=_Cpus
				bfn=int(bfn)
				self.bfn=bfn or 150
				self.Manager=multiprocessing.Manager()
				self.retdict= self.Manager.dict()
				self.Q=multiprocessing.Queue()
				self.printret=printret
				self.funcs=[]
				self.mul=threading.Thread 
				if f and tuplist:#初始化时有函数
						for n,o  in enumerate(tuplist):
								n+=1#下限为1
								process=self.mul(target=self.get_fun_ret,args=(n,self.f,o))
								self.funcs.append(process)
								
		def append(self,f,opttup):
				n=len(self.funcs)+1
				process=self.mul(target=self.get_fun_ret,args=(n,f,opttup))
				self.funcs.append(process)						

		def get_fun_ret(self,n,f,tup):
				self.retdict[n]=f(*tup)
				if self.printret==True:print '<%s>\n%s'%(n,self.retdict[n])

		def startprocess(self,threadjobs,n):#进程启动线程
				for t in threadjobs:
						t.start()
				for t in threadjobs:
						t.join()
				self.Q.put(n)
				
		def start(self,Print=True):
				stime=get_now()
				tp=len(self.funcs)
				ltp=min(tp,self.bfn)
				self.threadnums=ltp/self.cpus or 1#按限制任务数或任务数分线程,使cpus个进程的总线程数接近线程。
				self.threadnums+=1 if ltp%self.cpus else 0
				GroupbyPl=[ self.funcs[i:i+self.threadnums] for i in xrange(0,tp,self.threadnums)]
				pp=[]
				for i,threadjobs in enumerate(GroupbyPl):
						process=multiprocessing.Process(target=self.startprocess,args=(threadjobs,i))
						pp.append(process)
						process.start()
						if i>=self.cpus-1:
							n=self.Q.get()
							if n!=None:pp[n].join()
						
				for p in pp:
						p.join()
						
				if Print:
					print '[%s]' % stime,'-'*30,'任务数 %s 限制任务数:%s 进程:%s 线程数为:%s 开始' % (tp,self.bfn,self.cpus,self.threadnums)
					print '[%s]' % get_now() ,'-'*30,'任务数 %s 限制任务数:%s 进程:%s 线程数为:%s 结束' % (tp,self.bfn,self.cpus,self.threadnums)
				
		def dict(self):
				d=dict(self.retdict)
				self.Manager.shutdown()
				return d

		def Print(self):
				print '任务数 %s 限制任务数:%s 进程:%s 线程数为:%s' % (len(self.funcs),self.bfn,self.cpus,self.threadnums)


def f(a,b):
	time.sleep(10)
	return 'f'+str(a)+str(b)

def test(x):
	time.sleep(1)
	#print x
	return x
def test1(x):
	time.sleep(1)
	return x

if __name__ == "__main__":
	#a=xBF(bfn=9,thread=False,look=False)
	#a=xBF(bfn=1220,threadnums=100,look=False)
	a=xBF(bfn=12,look=True)
	for x in xrange(40):
		a.append(test,(x,))
	a.start()
	a.Print()
	dd=a.dict()
#	for k in dd:
#		print'<%s>' % k,'-'*20
#		print dd[k]
