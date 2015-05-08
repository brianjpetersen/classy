# standard libraries
pass
# third party libraries
pass
# first party libraries
from . import utilities


__all__ = ('Controller', )


class Controller:
    
    allowed_methods = set(('get', 'head', 'put', 'post', 'patch', 'delete'))
    
    def __init__(self, request, response, configuration=None):
        self.request = request
        self.response = response
        if configuration is None:
            configuration = {}
        self.configuration = configuration

    @staticmethod
    def configure(configuration):
        pass

    def view(self, returned):
        if isinstance(returned, str):
            self.response.text = returned
        elif isinstance(returned, bytes):
            self.response.body = returned

    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass
    
    get = utilities._raise_method_not_allowed
    head = utilities._raise_method_not_allowed
    put = utilities._raise_method_not_allowed
    post = utilities._raise_method_not_allowed
    patch = utilities._raise_method_not_allowed
    delete = utilities._raise_method_not_allowed
