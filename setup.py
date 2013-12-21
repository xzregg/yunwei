# coding:utf-8
import sys
import os

if __name__ == '__main__':
    path = os.path.dirname(os.path.realpath(__file__))
    if sys.version_info >= (2, 6):
        os.chdir('./packets')
        os.system('sh ./installpackets.sh')
        os.chdir(os.path.join(path, 'yw/rsa_key'))
        os.system('python MakeNewSshKey.py')
    else:
        print 'Python version is too low,>=2.6!'
        sys.exit(1)
