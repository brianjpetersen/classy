# standard libraries
import os
import datetime
import json
import glob
# third party libraries
pass
# first party libraries
import classy

def authenticate(username, password):
    if username == password:
        return True
    else:
        return False

class Root(classy.Controller):

    #@classy.authentication.Basic(authenticate)
    def get(self):
        return 'Welcome to this test.' 
    get._before = lambda: 'test'

app = classy.application
app.add_route('/', Root)

if __name__ == '__main__':

    import inspect
    get = getattr(Root, 'get')
    print inspect.getargspec(get)
    print get._before()
    """
    def search_for_orig(decorated, orig_name):
        for obj in (c.cell_contents for c in decorated.__closure__):
            if hasattr(obj, "__name__") and obj.__name__ == orig_name:
                return obj
            if hasattr(obj, "__closure__") and obj.__closure__:
                found = search_for_orig(obj, orig_name)
                if found:
                    return found
        return None

    print inspect.getargspec(search_for_orig(get, 'get'))
    """
    #classy.serve(host='0.0.0.0',port=8080)