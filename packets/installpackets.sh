

yum -y install gcc python-devel mysql-devel sqlite-devel MySQL-python freetype-devel openssh-clients python-sqlite python-setuptools || exit 1
tar xf setuptools-1.1.6.tar.gz 
cd setuptools-1.1.6 
python setup.py  build
python setup.py  install
cd ..
tar xf pexpect-2.3.tar.gz
cd pexpect-2.3   
python setup.py  build
python setup.py  install
cd ..
tar xf pycrypto-2.6.tar.gz
cd pycrypto-2.6
python setup.py build
python setup.py  install
cd ..
tar xf httplib2-0.8.tar.gz
cd httplib2-0.8
python setup.py  build
python setup.py  install
cd ..


tar xf Imaging-1.1.7.tar.gz
cd Imaging-1.1.7
if uname -a | grep x86_64;then
sed -i "s#^FREETYPE_ROOT.*#FREETYPE_ROOT=\'/usr/lib64\'#" setup.py 
fi
python setup.py build
python setup.py  install
cd ..


tar xf Django-1.2.7.tar.gz
cd Django-1.2.7
python setup.py  build 
python setup.py  install
cd ..

tar xf MySQL-python-1.2.3.tar.gz 
cd MySQL-python-1.2.3
python setup.py  build 
python setup.py  install
cd ..
tar xf uwsgi-1.9.5.tar.gz 
cd uwsgi-1.9.5   
python setup.py  build 
python setup.py  install
