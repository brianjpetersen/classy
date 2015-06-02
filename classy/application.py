# standard libraries
import copy
import traceback
import datetime
import logging
import inspect
# third party libraries
import webob
import waitress
# first party libraries
from . import (routing, utilities, exceptions, static, controllers)


logger = logging.getLogger('classy')
logger.setLevel(logging.INFO)


class Application:

    configuration = {'logger': logger}
    routes = {}
    
    def configure(self):
        def _configure(Controller):
            Controller.__configure__(self.configuration)
            for _, potential_controller in inspect.getmembers(Controller):
                if not isinstance(potential_controller, type):
                    continue
                if issubclass(potential_controller, controllers.Controller):
                    child_controller = potential_controller
                    _configure(child_controller)
        for Controller in self.routes.values():
            _configure(Controller)
        
    def __call__(self, environ, start_response):
        request = webob.Request(environ)
        response = webob.Response()
        # extract relevant details from request
        url = request.path
        method = request.method.lower()
        # find appropriate handler
        Controller, args, kwargs = routing.match(self.routes, url, method)
        if Controller is None:
            response = exceptions.HTTPNotFound()
            return response(environ, start_response)
        # instantiate controller and set up handler context
        try:
            controller = Controller(request, response, self.configuration)
        except:
            response = classy.exceptions.HTTPServiceUnavailable()
            return response(environ, start_response)
        with controller:
            # Controller configuration should allow this method
            # NB: this could go outside the with context, but including it here
            # captures all exceptions except 404 and those related to instantiation
            allowed_methods = getattr(Controller, 'allowed_methods', set())
            if method not in allowed_methods:
                raise exceptions.HTTPMethodNotAllowed
            # extract appropriate handler (this should never fail)
            handler = getattr(controller, method)
            # call controller and view method
            returned = handler(*args, **kwargs)
            controller.__view__(returned)
        return controller.response(environ, start_response)

    def add_route(self, route, Controller):
        route = utilities.Url(route)
        self.routes[route] = Controller
        
    def add_asset(self, route, path):
        pass
        
    def serve(self, *args, **kwargs):
        self.configure()
        waitress.serve(self, *args, **kwargs)


app = application = Application()
serve = app.serve
