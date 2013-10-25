#/usr/bin/env python
#coding=utf-8
#甄码农python代码
#使用zipfile做目录压缩，解压缩功能

import os,os.path
import zipfile

def zip_dir(dirname,zipfilename):
	filelist = [];isdir=True
	if os.path.isfile(dirname):
		filelist.append(dirname)
		isdir=False
	else :
		for root, dirs, files in os.walk(dirname):
			for name in files:
				filelist.append(os.path.join(root, name))
	print filelist
	zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
	for tar in filelist:
		arcname = tar[len(dirname):] if  isdir  else os.path.basename(dirname)
		zf.write(tar,arcname)
	zf.close()
	return os.path.getsize(zipfilename)


def unzip_file(zipfilename, unziptodir):
	if not os.path.exists(unziptodir): os.mkdir(unziptodir, 0755)
	zfobj = zipfile.ZipFile(zipfilename)
	for name in zfobj.namelist():
		#print name.decode('utf-8','replace').encode('utf-8','replace').decode('utf-8','replace')
		Name = name.decode('utf-8','replace').replace('\\','/')
		if name.endswith('/'):
			try:
				os.mkdir(os.path.join(unziptodir, name))
			except OSError:
				pass
		else:			
			ext_filename = os.path.join(unziptodir, Name)
			ext_dir= os.path.dirname(ext_filename)
			if not os.path.exists(ext_dir) : os.mkdir(ext_dir,0755)
			outfile = open(ext_filename, 'wb')
			outfile.write(zfobj.read(name))
			outfile.close()
	return os.path.exists(unziptodir)
	
	
if __name__ == '__main__':
	zip_dir(r'E:/python/learning',r'E:/python/learning/zip.zip')
	unzip_file(r'E:/python/learning/zip.zip',r'E:/python/learning2')