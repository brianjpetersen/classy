# standard libraries
pass
# third party libraries
pass
# first party libraries
pass

class Controller(object):
    
    def __init__(self, request, response, **config):
        self.request = request
        self.response = response
        self.config = config

    def before_handler_called(self):
        pass

    def before_response_returned(self):
        pass

    def before_error_returned(self):
        pass