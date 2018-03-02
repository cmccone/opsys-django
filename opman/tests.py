from django.test import TestCase
from opman.models import MyUser as User
# Create your tests here.
from django.http import HttpResponse,HttpResponseRedirect
from functools import wraps

def getLoginUserInfo(request):
    user = User.objects.get(id=request.user.id)
    perm = [ perm[i] for perm in user.permission.values("url") for i in perm ] if user.permission.values() else "false"
    url = str(request.get_full_path())
    url =  url[0:len(url)-1] if url[-1] == "/" else url
    if url in ''.join(perm):
       res = "你有权限访问"
    else:
       res = "你无权访问该页面"
    #permlist = user.myuser.permission.values("myuser_id")
    #if permlist:
    #  perm = permlist
    #else:
    #   perm = "false"
    return HttpResponse(url + " " + res)



def permission_required(next_url=None):
    def decorator(func):
        @wraps(func)
        def wrapper(request,**kwargs):
            user = request.user
            if user.is_superuser and user.is_active:
                rv = func(request,**kwargs)
            elif user.is_active:
                permlist = [ perm[i] for perm in user.permission.values("url") for i in perm ] if user.permission.values() else False
                url = str(request.path)
                url = url[0:len(url)-1] if url[-1] == "/" else url
                if permlist and url in ''.join(permlist):
                    rv = func(request,**kwargs)
                else:
                    return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect(next_url)
            return rv
        return wrapper
    return decorator
