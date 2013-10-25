#/usr/bin/env pytho
# coding:utf-8


import threading,time
import sys,os
import signal

def get_now():
	tf='%Y-%m-%d %H:%M:%S'
	return time.strftime(tf,time.localtime())

class Mytimer():
	'''
	定时运行的类,runone=True时为到计时运行.
	'''
	def __init__(self,n,f,tup,runone=False):
		self.one=runone
		self.n=n
		self.f=f
		self.tup=tup

	def TimerF(self):
		while True:
			time.sleep(self.n)
			self.f(*self.tup)
			if self.one==True:break

	def start(self):
		self.t=threading.Thread(target=self.TimerF)
		self.t.start()
	
	def Stop(self):
		self.one=True
		self.t.join()

def f(a):
	print '\r-',
	time.sleep(a)
	sys.stdout.flush()
	print '\r\\',
	time.sleep(a)
	sys.stdout.flush()
	print '\r|',
	time.sleep(a)
	sys.stdout.flush()
	print '\r/',
	time.sleep(a)
	sys.stdout.flush()

#a=threading.Thread(target=mytime,args=(1,f,(1,2)))
#a.start()
if __name__ =="__main__":
 try:
	p=Mytimer(1,f,(0.5,))
	p.start()
	while True:
		print 'aaaa',
		time.sleep(3)
 except:
	p.Stop()
