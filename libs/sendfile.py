#/usr/bin/env python
#coding:utf-8
import os, tempfile, zipfile
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from settings import PWD
import mimetypes

def download(request,path,document_root):
    File=os.path.join(PWD,document_root,path.replace('/',os.sep))
    return send_file(File)
    
def send_file(File,fileobj=None):
    """																		 
    Send a file through Django without loading the whole file into			  
    memory at once. The FileWrapper will turn the file object into an		   
    iterator for chunks of 8KB.												 
    """

    filename = File # Select your file here.	
    mimetype, encoding=mimetypes.guess_type(filename)
    mimetype = mimetype or 'application/octet-stream'
    try:
        wrapper = FileWrapper(open(filename))
    except IOError:
        return HttpResponse(u'Not This File!')
    response = HttpResponse(wrapper,  mimetype=mimetype,content_type=u'text/plain')
    response['Content-Encoding'] = encoding or u'utf-8'
    response['Content-Disposition'] = 'attachment; filename=%s'%os.path.basename(filename).encode('utf-8')
    response['Content-Length'] = os.path.getsize(filename)
    return response


def send_zipfile(zipfilename='temp.zip',filelist=[]):
    """																		 
    Create a ZIP file on disk and transmit it in chunks of 8KB,				 
    without loading the whole file into memory. A similar approach can		  
    be used for large dynamic PDF files.										
    """
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for file in filelist:						 
        archive.write(file,os.path.basename(file))
    archive.close()
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Encoding'] = 'utf-8'
    response['Content-Disposition'] = 'attachment; filename=%s'%zipfilename
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
 
