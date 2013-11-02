yunwei
======================

一个服务器批量管理系统


基于以下开源软件：
django
paramiko
jquery
artdialog
codemirror
juqerydatatable
freewebfilemanager


需要环境:

    yum -y install gcc python-devel mysql-devel sqlite-devel MySQL-python freetype-devel openssh-clients python-sqlite python-setuptools
    python版本2.6或者2.7,注意编译安装完，要修改yum命令
    python包:
	    pexpect
	    pycrypto
	    httplib2
	    Imaging
	    Django 1.2
	    MySQL-python
安装:
    
    python setup.py
    
配置数据库(可修改settings.py文件配置mysql，默认使用sqlite):
   
    python manage.py syncdb
    
启动:

    python manage.py runserver 0.0.0.0:8000
    或者
    uwsgi --http 0.0.0.0:8000 --module wsgi  --chdir ./ --pythonpath .. --enable-threads -M -p4  --reload-mercy 4
    最好配合nginx使用uwsgi
    
浏览:http://localhost:8000

    默认帐号密码:admin/admin


    
