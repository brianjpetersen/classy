# standard libraries
pass
# third party libraries
pass
# first party libraries
import http_exceptions as exceptions

class Controller(object):
    
    __http_methods__ = ('get', 'head', 'put', 'post', 'delete')

    def __init__(self, request, response, **configuration):
        self.request = request
        self.response = response
        self.configuration = configuration

    def __getattr__(self, name):
        if name in self.__http_methods__:
            raise exceptions.HTTPMethodNotAllowed
        else:
            raise exceptions.HTTPForbidden