# standard libraries
import functools
import base64
# third party libraries
pass
# first party libraries
from .. import exceptions

class Basic(object):
    
    def __init__(self, authenticator, realm=''):
        self.authenticator = authenticator
        self.realm = realm

    def _raise_exception(self):
        response = exceptions.HTTPUnauthorized()
        response.headers['WWW-Authenticate'] = 'Basic realm="{}"'.format(self.realm)
        raise response

    def __call__(self, handler):
        @functools.wraps(handler)
        def _wrapper(controller, *args, **kwargs):
            # extract relevant authentication data
            request = controller.request
            authorization = request.authorization
            if authorization is None:
                self._raise_exception()
            try:
                authorization_type, authorization_data = authorization
                if authorization_type.lower() != 'basic':
                    self._raise_exception()
                username, password = base64.b64decode(authorization_data).split(':')
            except:
                self._raise_exception()
            # attempt basic authentication
            if self.authenticator(username, password):
                return handler(controller, *args, **kwargs)
            else:
                self._raise_exception()
        return _wrapper