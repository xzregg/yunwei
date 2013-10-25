# coding: utf-8
# jQuery File Tree
# Python/Django connector script
# By Martin Skou
#


from django.http import HttpResponseRedirect
from django.http import HttpResponse,Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
import os,json,hashlib,shutil
import urllib
from libs.timelib import *
from libs.html import *


from settings import FileManagerChroot
def dirlist(request,chroot='/data'):
   r=['<ul class="jqueryFileTree" style="display: none;">']
   try:
           r=['<ul class="jqueryFileTree" style="display: none;">']
           d=urllib.unquote(request.POST.get('dir',chroot))
           d=os.path.join(d,chroot) if not d.startswith(chroot) else d
           for f in os.listdir(d):
               ff=os.path.join(d,f)
               if os.path.isdir(ff):
                   r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
               else:
                   e=os.path.splitext(f)[1][1:] # get .ext and remove dot
                   r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))
           r.append('</ul>')
   except Exception,e:
       r.append('Could not load directory: %s' % str(e))
   r.append('</ul>')
   return HttpResponse(''.join(r))


   
def test(request):
    '''
    目录树测试
    '''
    ScriptUrl="/filemanage/filetree/dirlist/"
    return render_to_response('FileTree_old.html',locals())  
   
class FileOrDir():
    def __init__(self,path):
        self.path=path
        self.isdir=True if os.path.isdir(path) else False
    def Del(self):
        if self.isdir:
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)
        return os.path.isdir(file)

    def ls(self):
        return os.listdir(self.path) if self.isdir else None

    def attr(self):
        return os.stat(self.path) 

    def mkdir(self):
        return	os.mkdir(self.path);
    
    def  touch(self):
        open(self.path,'w').write('')

    def copy(self,dst):
        try:
            if self.isdir:
                shutil.copytree(self.path,dst)
            else:
                shutil.copy(self.path,to)
            return True
        except:
            return False


    def copyDir(self,src, dst):
        if not self.file_exists(dst):
            shutil.copytree(src,dst)
            return True
        return False
        
    def read(self):
        return open(self.path,'rb').read() if not self.isdir else ''

    def writefile(self, content):
        if not self.isdir:
            open(self.path,'wb').write(content)
        return True
    '''
    public function move_uploaded_file ($from, $to) {
        return @move_uploaded_file($from, $to);
    }
    
    public function parseImage($ext,$img,$file = null){
        $result = false;
        switch($ext){
            case 'png':
                $result = imagepng($img,($file != null ? $file : ''));
            break;
            case 'jpeg':
                $result = imagejpeg($img,($file ? $file : ''),90);
            break;
            case 'jpg':
                $result = imagejpeg($img,($file ? $file : ''),90);
            break;
            case 'gif':
                $result = imagegif($img,($file ? $file : ''));
            break;
        }
        return $result;
    }
    
     public function imagecreatefrompng($src) {
         return imagecreatefrompng($src);	
     }
     
     public function imagecreatefromjpeg($src){
         return imagecreatefromjpeg($src);
     }
     
     public function imagecreatefromgif($src){
          return imagecreatefromgif($src);
     }
}
    '''   
    
def UnquoteUTF8(text):
    return urllib.unquote(text.encode('utf-8')).decode('utf-8')

class GSFileSystem():
    def __init__(self,request,chroot=FileManagerChroot):
        self.request=request
        self.chroot=chroot
        d=UnquoteUTF8(request.REQUEST.get('dir','')).lstrip('/')
        self.AbsDirPath=os.path.join(self.chroot,d) if d!='/' else chroot
        
        filename=UnquoteUTF8(request.REQUEST.get('filename','')).lstrip('/')
        self.Absfilename=os.path.join(self.AbsDirPath,os.path.basename(filename))
        
        
        files=UnquoteUTF8(request.REQUEST.get('files',''))
        self.files=files.split(',,,')
        
        opt=request.REQUEST.get('opt',1)
        functions={}
        functions[1] = 'listDir';
        functions[2] = 'makeFile';
        functions[3] = 'makeDirectory';
        functions[4] = 'deleteItem';
        functions[5] = 'copyItem';
        functions[6] = 'renameItem';
        functions[7] = 'moveItems';
        functions[8] = 'downloadItem';
        functions[9] = 'readfile';
        functions[10] = 'writefile';
        functions[11] = 'uploadfile';
        functions[12] = 'jCropImage';
        functions[13] = 'imageResize';
        functions[14] = 'copyAsFile';
        functions[15] = 'serveImage';
        functions[16] = 'zipItem';
        functions[17] = 'unZipItem';
        
        self.f=getattr(self,functions[int(opt)])

    
    def __call__(self):
        return self.f(self.request)
    def uploadfile(self,request):
        file_obj = request.FILES.get('filename', None)

        if file_obj:
            file=open(os.path.join(self.AbsDirPath,file_obj.name),'wb')
            for data in file_obj.chunks():
                file.write(data)
            file.close()
            #open(os.path.join(self.AbsDirPath,file_obj.name),'wb').write(file_obj.read())
        return HttpResponse('{result: \'1\'}')
        
    def downloadItem(self,request):
        from libs.sendfile import send_file
        dir=UnquoteUTF8(request.REQUEST.get('dir','')).lstrip('/')
        filename=UnquoteUTF8(request.REQUEST.get('filename','')).lstrip('/')
        FilePath=os.path.join(dir,filename)
        chroot=os.path.basename(self.chroot)
        URL='/%s/%s'%(chroot,FilePath)
        #return HttpResponseRedirect(URL)
        return send_file(self.Absfilename)
        
    def unZipItem(self,request):
        from libs.zip import unzip_file
        Absfilename=self.Absfilename
        unzip_file(Absfilename,Absfilename[:-4])
        #unzip_file(Absfilename,os.path.dirname(Absfilename))
        return HttpResponse('{result: \'1\'}')
        
        #return HttpResponse('{result: \'0\' , gserror: \'can\\\'t uzzip %s \'}'%Absfilename)
            
    def zipItem(self,request):
        from libs.zip import zip_dir
        Absfilename=self.Absfilename
        newfilename=request.POST.get('newfilename','')
        AbsNewfilename=os.path.join(self.AbsDirPath,newfilename)
        if zip_dir(Absfilename,AbsNewfilename):
            if os.path.isdir(Absfilename):
                    shutil.rmtree(Absfilename)
            else:
                    os.remove(Absfilename)
            return HttpResponse('{result: \'1\'}')
        else:
            return HttpResponse('{result: \'0\' , gserror: \'can\\\'t zip %s \'}'%AbsNewfilename)
            
    def copyAsFile(self,request):
        Absfilename=self.Absfilename
        newfilename=request.POST.get('newfilename','')
        AbsNewfilename=os.path.join(self.AbsDirPath,newfilename)
        shutil.copy(Absfilename,AbsNewfilename)
        return HttpResponse('{result: \'1\'}')
        
    def writefile(self,request):
        filenContent=request.POST.get('filenContent','')
        if filenContent:	
            open(self.Absfilename,'wb').write(UnquoteUTF8(filenContent).encode('utf-8'))
            return HttpResponse('{result: \'1\'}')
    def readfile(self,request):
        return HttpResponse(open(self.Absfilename,'rb').read())
        
    def moveItems(self,request):
        try:
            files=self.files
            if files:
                for filename in files:
                        chrootfilename=os.path.join(self.chroot,filename)
                        Abstarget=os.path.join(self.AbsDirPath,os.path.basename(chrootfilename))
                        shutil.move(chrootfilename,Abstarget)
                return HttpResponse('{result: \'1\'}')
        except:
            return HttpResponse('{result: \'0\' , gserror: \'can\\\'t move %s \'}'%str(files))
        
    def copyItem(self,request):
        files=self.files
        if files:
            for filename in files:
                chrootfilename=os.path.join(self.chroot,filename)
                Abstarget=os.path.join(self.AbsDirPath,os.path.basename(chrootfilename))
                Abstarget+='_copy' if chrootfilename==Abstarget else ''

                if os.path.isdir(chrootfilename):
                    shutil.copytree(chrootfilename,Abstarget)
                else:
                    shutil.copy(chrootfilename,Abstarget)
            return HttpResponse('{result: \'1\'}')
        return HttpResponse('{result: \'0\' , gserror: \'can\\\'t copy %s \'}'%str(files))
    
    def renameItem(self,request):
        try:
            Absfilename=self.Absfilename
            newfilename=request.POST.get('newfilename','')
            if newfilename:
                AbsNewfilename=os.path.join(self.AbsDirPath,newfilename)
                os.rename(Absfilename,AbsNewfilename)
                return HttpResponse('{result: \'1\'}')
        except:
            return HttpResponse('{result: \'0\' , gserror: \'can\\\'t rename %s to %s\'}'%(Absfilename,AbsNewfilename))
    def deleteItem(self,request):
        files=self.files
        if files:
            for filename in files:
                Absfilename=os.path.join(self.AbsDirPath,filename)
                if os.path.isdir(Absfilename):
                    shutil.rmtree(Absfilename)
                else:
                    os.remove(Absfilename)
            return HttpResponse('{result: \'1\'}')
        else:
            return HttpResponse('{result: \'0\' , gserror: \'can not del item %s\'}'%str(files))	
            
    def makeDirectory(self,request):
        Absfilename=self.Absfilename
        try:
            os.mkdir(Absfilename)
            return HttpResponse('{result: \'1\'}')
        except:
            return HttpResponse('{result: \'0\' , gserror: \'can\\\'t mkdir dir %s\'}'%Absfilename)
            
            
    def makeFile(self,request):
        Absfilename=self.Absfilename
        if not os.path.exists(Absfilename):

            open(Absfilename,'wb').write('')
            return HttpResponse('{result: \'1\'}')
        return HttpResponse('{result: \'0\' , gserror: \'can not create item %s\'}'%Absfilename)
        
    def listDir(self,request):
        d=UnquoteUTF8(request.POST.get('dir')).lstrip('/')
        Dir=self.AbsDirPath
        html=[]
        if os.path.exists(Dir):
            html.append( u'var gsdirs = new Array();')
            html.append(u'var gsfiles = new Array();')
            File=os.listdir(Dir)
            for i in File:
                AbsPath=os.path.join(Dir,i)
                ChrootPath=os.path.join(d,i)
                
                PathMd5=hashlib.md5(AbsPath.encode('utf-8')).hexdigest()
                PathMtime=UnixTimeToStrTime(os.stat(AbsPath).st_mtime)
                if os.path.isdir(AbsPath):
                    #目录名，绝对路径，md5,修改时间
                    DirNums=os.listdir(AbsPath).__len__()
                    tup=(i,ChrootPath,DirNums,PathMd5,PathMtime)
                    html.append( u'gsdirs.push(new gsItem("2", "%s", "%s", "%s", "%s", "dir", "%s"));'%tup)
                elif os.path.isfile(AbsPath):
                    ext=i.rfind('.')
                    ext=i[ext+1:].lower() if ext>=0 else 'unknown'
                    tup=(i,ChrootPath,os.path.getsize(AbsPath),PathMd5,ext,PathMtime)
                    html.append( u'gsfiles.push(new gsItem("1", "%s", "%s", "%s", "%s", "%s", "%s"));'%tup)	
        return HttpResponse(''.join(html))		

    
    
def Connectors(request):
    '''
    文件操作
    '''
    return GSFileSystem(request)()

    
    
def FileManager(request):
    '''
    文件管理
    '''
    try:
        ips=os.popen("/sbin/ip add | grep -oP '(?<=inet )[^\s]+(?=/)'")

        IP=[ x for x in ips.read().split() if x!='127.0.0.1'][0]
        DownloadURL='http://%s:%s/%s'%(IP,request.META['SERVER_PORT'],FileManagerChroot)
    except:
        pass
    ScriptUrl=MakeURL(Connectors)

    #DownloadURL=request.META['HTTP_REFERER']+FileManagerChroot
    #DownloadURL=request.META['SERVER_NAME']+':'+request.META['SERVER_PORT']+'/'+FileManagerChroot+'/'
    return render_to_response('FileManager.html',locals())	
    
    
    
    
    

