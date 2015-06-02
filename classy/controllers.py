# standard libraries
import datetime
import logging
import traceback
# third party libraries
pass
# first party libraries
from . import (utilities, exceptions)


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
    def __configure__(configuration):
        pass

    def __view__(self, returned):
        if isinstance(returned, str):
            self.response.text = returned
        elif isinstance(returned, bytes):
            self.response.body = returned

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        logger = self.configuration.get('logger', None)
        if logger is None:
            logger = logging.NullHandler()
        # log and handle any errors
        if exception_value is None:
            log = self.__log__(exception_type, exception_value, 
                               exception_traceback)
            logger.info(log)
        elif isinstance(exception_value, exceptions.HTTPException):
            self.response = exception_value
            log = self.__log__(exception_type, exception_value, 
                               exception_traceback)
            logger.warning(log)
        elif isinstance(exception_value, Exception):
            self.response = exceptions.HTTPInternalServerError()
            log = self.__log__(exception_type, exception_value, 
                               exception_traceback)
            logger.error(log)
        # suppress exception reraise in calling routine
        return True
        
    def __log__(self, *exception_tuple):
        exception_is_none = any(map(lambda e: e is None, exception_tuple))
        if exception_is_none:
            exception_message = ''
        else:
            exception_message = traceback.format_exception(*exception_tuple)
            exception_message = '\n\n    ' + '    '.join(exception_message)
        now = datetime.datetime.utcnow().isoformat()[:23]
        status = self.response.status_code
        client_address = self.request.client_addr
        method = self.request.method
        path = self.request.path
        return '{} {} {} {} {} {}'.format(now, client_address.ljust(15),
                                          status, method, path, 
                                          exception_message)
    
    get = utilities._raise_method_not_allowed
    head = utilities._raise_method_not_allowed
    put = utilities._raise_method_not_allowed
    post = utilities._raise_method_not_allowed
    patch = utilities._raise_method_not_allowed
    delete = utilities._raise_method_not_allowed
