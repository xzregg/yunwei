#conding:utf-8
# jQuery File Tree
# Python/Django connector script
# By Martin Skou
#


from django.http import HttpResponseRedirect
from django.http import HttpResponse,Http404
from django.template.loader import get_template
from django.shortcuts import render_to_response
import os
import urllib


def dirlist(request,chroot='/data/'):
   r=['<ul class="jqueryFileTree" style="display: none;">']
   try:
		   r=['<ul class="jqueryFileTree" style="display: none;">']
		   d=urllib.unquote(request.POST.get('dir',chroot))
		   d=os.path.join(d,chroot) if not d.startswith(chroot) else d
		   print d
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
	
	return render_to_response('FileTree.html',locals())
