#coding:utf-8

from ..Global import *



import httplib2
def webssh(request):
    '''
    连接Webssh服务器
    '''
    PROXY_FORMAT = u'http://%s%s' % (WebSSHAddress, u'%s')
    
    conn = httplib2.Http()

    url = request.path.replace(MakeURL(webssh),'/')

    if request.method == 'GET':
        url_ending = '%s?%s' % (url, request.GET.urlencode())
        url = PROXY_FORMAT % url_ending
        response, content = conn.request(url, request.method)
    elif request.method == 'POST':
        url = PROXY_FORMAT % url
        data = request.POST.urlencode()
        response, content = conn.request(url, request.method, data)
    return HttpResponse(content, status=int(response['status']), mimetype=response['content-type'])












