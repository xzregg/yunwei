#coding:utf-8
import os,sys
#list去重
def unique_list(seq, excludes=[]):
    seen = set(excludes)
    return [x for x in seq if x not in seen and not seen.add(x)]

  
def GetPathSize(strPath):  
    if not os.path.exists(strPath):  
        return 0;  
    if os.path.isfile(strPath):  
        return os.path.getsize(strPath);  
    nTotalSize = 0;  
    for strRoot, lsDir, lsFiles in os.walk(strPath):  
        #get child directory size  
        for strDir in lsDir:  
            nTotalSize = nTotalSize + GetPathSize(os.path.join(strRoot, strDir));  
        #for child file size  
        for strFile in lsFiles:  
            nTotalSize = nTotalSize + os.path.getsize(os.path.join(strRoot, strFile));  
    return nTotalSize;  
	
def GetPyFile(Dir):#递归查找py文件
    return [ os.path.join(dirpath,filename)  for dirpath, dirs, files in os.walk(Dir) for filename in files if  filename.endswith('.py')  ]







	