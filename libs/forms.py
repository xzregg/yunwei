#coding:utf-8
from django import forms

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.
import random
from django.conf import settings
from django.utils.decorators import available_attrs
from django.utils.hashcompat import md5_constructor
  
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
_MAX_CSRF_KEY = 18446744073709551616L     # 2 << 63
  
def _get_new_submit_key():
    return md5_constructor("%s%s" % (randrange(0, _MAX_CSRF_KEY), settings.SECRET_KEY)).hexdigest()
  
def anti_resubmit(page_key='',Redirect='/'):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.method == 'GET':
                request.session['%s_submit' % page_key] = _get_new_submit_key()
                print 'session:' + request.session.get('%s_submit' % page_key)
            elif request.method == 'POST':
                old_key = request.session.get('%s_submit' % page_key, '')
                if old_key == '':
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect(Redirect)
                request.session['%s_submit' % page_key] = ''
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



from libs.rsa import rsa
import binascii
def publickey_encodeing(mess,publickey):
	crypttext=rsa.encrypt(mess,publickey)
	return crypttext

def privatekey_decodeing(crypttext,privatekey):
	crypttext=binascii.unhexlify(crypttext)
	mess=rsa.decrypt(crypttext,privatekey)
	return mess

def GetRsa1024Keys():
	return rsa.newkeys(1024)

(_pubkey, _privkey)=rsa.newkeys(1024)
def GetMePublickey( request,NewKey=False):
	if NewKey:
		(pubkey, privkey)=rsa.newkeys(1024)
	else:
		pubkey=_pubkey
		privkey=_privkey
		#pubkey=rsa.PublicKey(133140523494670483630029776185109387594116070238963418671724648382921799708186111185095261336065345676347308364051683986058428857018900255537065386532293673626422214690295028445739291357298772704714696036333914406244341544934027933135508660210828498488717195447579867711927457752345392889413450272735207280859, 65537)
		#privkey=rsa.PrivateKey(133140523494670483630029776185109387594116070238963418671724648382921799708186111185095261336065345676347308364051683986058428857018900255537065386532293673626422214690295028445739291357298772704714696036333914406244341544934027933135508660210828498488717195447579867711927457752345392889413450272735207280859, 65537, 36374583413523277070901676039403445151176407794507530270186762123628100519936407232084633935368570644597686135440215477827428302865914049703086118553298572772036079186683229470918811763929682696697936049234472664682142260212095203827222245265454579621602151991952420576948588060912742592188099462754418921233, 44358178702179288532735573199178913532030150389126255600186656398020360144650719080190683071519048437213758898206650759301809932014436686414866242627668835390036233, 3001487603640709804757326567611215720543412247744427980345344795082680045949430355720102008866758474529188704205351512738913188612355894435907523)
	pub_n=hex(pubkey.n)[2:-1]#16进公钥
	request.session['privkey']=privkey
	return pub_n
	'''
	对应js
	<script src="/static/js/jquery-1.8.1.min.js"></script>
    <script src="/static/js/Scripts/jQuery.md5.js" type="text/javascript" ></script>
    <script src="/static/js/Scripts/BigInt.js" type="text/javascript"></script>
    <script src="/static/js/Scripts/RSA.js" type="text/javascript"></script>
    <script src="/static/js/Scripts/Barrett.js" type="text/javascript"></script>
    var rsa_n=data;
	var password=$('#password').val();
	var loginname=$('#loginname').val();
	var key = new RSAKeyPair("10001", '', rsa_n); 
	loginname = encryptedString(key, loginname);
	'''

	

		
class login(forms.Form):
    user = forms.CharField()
    password = forms.CharField()
    check = forms.CharField()
