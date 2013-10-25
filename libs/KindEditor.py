#coding:utf-8
from django.http import HttpResponse,Http404
import json,os,string,re,time,datetime


from settings import MEDIA_ROOT,MEDIA_URL

class KindEditor(object):
    def __init__(self,root_path,root_url=MEDIA_URL):
        self.root_path = os.path.join(MEDIA_ROOT,root_path)
        self.root_url = root_url  
        #today = datetime.datetime.today()
        #save_dir = '/attached/' + dir_name + '/%d/%d/%d/' % (today.year, today.month, today.day)
#上传文件
    def Upload(self,request,sub_path=''):
        ext_allowed = {}
        ext_allowed["image"] = ['gif', 'jpg', 'jpeg', 'png']
        ext_allowed["flash"] = ["swf", "flv"]
        ext_allowed["media"] = ["swf", "flv", "mp3", "wav", "wma", "wmv", "mid", "avi", "mpg", "asf", "rm", "rmvb"]
        ext_allowed["file"] = ["doc", "docx", "xls", "xlsx", "ppt", "htm", "html", "txt", "zip", "rar", "gz" , "bz2"]
        max_size = 1000000
        dir_name = request.GET["dir"]
        save_path = os.path.join(self.root_path,dir_name,sub_path)
        
        if request.method == 'POST':
            file_content = request.FILES['imgFile']
            file_name=file_content.name
            if not file_name:
                return HttpResponse(json.dumps(
                    { 'error': 1, 'message': u'请选择要上传的文件' }
                ))
            ext = file_content.name.split('.').pop()
            if ext not in ext_allowed[dir_name]:
                return HttpResponse(json.dumps(
                    { 'error': 1, 'message': u'请上传后缀为%s的文件' %  ext_allowed[dir_name]}
                ))
            if file_content.size > max_size:
                return HttpResponse(json.dumps(
                    { 'error': 1, 'message': u'上传的文件大小不能超过10MB'}
                ))
            if not os.path.isdir(save_path):
                os.makedirs(save_path)
            new_file = '%s.%s' % (int(time.time()), ext)
            chroot_path_file=os.path.join(dir_name,sub_path,new_file)
            save_url = self.root_url + chroot_path_file.replace(os.sep,'/')
            save_file=os.path.join(save_path,new_file)
            destination = open(save_file, 'wb+')
            for chunk in file_content.chunks():
                destination.write(chunk)
            destination.close()
            return HttpResponse(json.dumps(
                    { 'error': 0, 'url': save_url}
            ))

        
    #从服务器上选择文件  
    def FileManager(self,request):
        root_path = self.root_path
        root_url = self.root_url
        file_types = ["gif", "jpg", "jpeg", "png", "bmp"]
        dir_types = ['image', 'flash', 'media', 'file']
          
        dir_name = request.GET["dir"]
        if dir_name not in dir_types:
              return  HttpResponse("Invalid Directory name.")
              
        root_path = os.path.join(root_path,dir_name)
        root_url = root_url + dir_name + "/"
        if not os.path.isdir(root_path) or not os.path.exists(root_path):
                    os.makedirs(root_path)

        path = request.GET["path"]
        current_dir_path = path
        current_path = os.path.join(root_path,path)
        current_url = root_url + path 
        moveup_dir_path=''  

        order = request.GET["order"]
        if order:
            order = string.lower(order)
        else:
            order = "name"
        if ".." in current_path:
            return HttpResponse("Access is not allowed.")

        if not os.path.isdir(current_path) or not os.path.exists(current_path):
            return HttpResponse("'Directory does not exist.") 
            
        file_list = []

        for file_name in os.listdir(current_path):
                  dicts = {}
                  file_path = os.path.join(current_path, file_name)
                  if os.path.isdir(file_path):
                    dicts["is_dir"] = True
                    dicts["has_file"] = len(os.listdir(file_path)) > 0
                    dicts["filesize"] = 0
                    dicts["is_photo"] = False
                    dicts["filetype"] = ""
                  else:
                    dicts["is_dir"] = False
                    dicts["has_file"] = False
                    dicts["filesize"] = os.path.getsize(file_path)

                    extensions = string.split(file_name, ".")
                    length = len(extensions) - 1
                    if string.lower(extensions[length]) in file_types:
                      dicts["is_photo"] = True
                    else:
                      dicts["is_photo"] = False
                    dicts["filetype"] = string.lower(extensions[length])
                  dicts["filename"] = file_name
                  dicts["datetime"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                  file_list.append(dicts)

        results = {}
        results["moveup_dir_path"] = moveup_dir_path
        results["current_dir_path"] = current_dir_path
        results["current_url"] = current_url
        results["total_count"] = len(file_list)
        results["file_list"] = file_list
        return HttpResponse(json.dumps(results))
                
    
    
    
    
    
    
    
