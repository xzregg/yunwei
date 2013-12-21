# coding:utf-8
class SSLMiddleware(object):

    """
    Middleware that applies some fixes for people using
    Nginx manage HTTPS and forward requests as HTTP to
    backend server.
    """

    def process_request(self, request):
        # use HTTPS forever
        request.is_secure = lambda: True == True
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            real_ip = real_ip.split(",")[0]
            request.META['REMOTE_ADDR'] = real_ip
