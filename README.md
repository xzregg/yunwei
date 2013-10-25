yunwei
======================

基于django的服务器批量管理系统



需要:

    yum -y install gcc python-devel mysql-devel MySQL-python freetype-devel openssh-clients python-sqlite python-setuptools
    python版本2.6或者2.7,注意编译安装完，要修改yum命令
    python包:
	    pexpect
	    pycrypto
	    httplib2
	    Imaging
	    Django
	    MySQL-python
安装:
    
    python setup.py
    
配置数据库(可修改settings.py文件配置mysql，默认使用sqlite):

   
    python manage.py syncdb
    
启动:

    python manage.py 0.0.0.0:8000
    

浏览:http://localhost:8000

    默认帐号密码:admin/admin
