# standard libraries
pass
# third party libraries
pass
# first party libraries
from . import utilities


class Controller(object):
    def __init__(self, request, response, **configuration):
        self.request = request
        self.response = response
        self.configuration = configuration

    def view(self, handler_return=None):
        if isinstance(handler_return, str):
            self.response.text = handler_return
        elif isinstance(handler_return, bytes):
            self.response.body = handler_return

    get = utilities._raise_method_not_allowed
    head = utilities._raise_method_not_allowed
    put = utilities._raise_method_not_allowed
    post = utilities._raise_method_not_allowed
    delete = utilities._raise_method_not_allowed
