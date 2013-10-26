#coding:utf-8

import pexpect,os,sys
def MakeSshRsaKey(savepathfile):
		isSsh1=os.popen('ssh -V 2>&1 | grep Open').read()
		if not isSsh1:
			print 'This is run at Ssh1 environment!'
			sys.exit(1)
		child = pexpect.spawn ('ssh-keygen -t rsa -b 1024 -f %s'%savepathfile)
		while True:
			i=child.expect([':','(y/n)','saved',pexpect.EOF,pexpect.TIMEOUT],timeout=10)
			if i==0:
							child.sendline()
			elif i==1:
							child.sendline('y')
			elif i==2:
							child.expect(pexpect.EOF)
							break
			else:
							print 'Error'
							break
		os.system('ssh-keygen -e -f %s > %s_ssh2.pub'%(savepathfile,savepathfile))
		

if __name__ == "__main__":
		path=os.path.dirname(os.path.realpath(__file__))
		if path:os.chdir(path)
		MakeSshRsaKey('id_rsa')
