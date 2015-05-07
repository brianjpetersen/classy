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

    configuration = {}
    routes = {}
    
    def configure(self):
        def _configure(Controller, configuration):
            configuration = copy.deepcopy(configuration)
            Controller.configure(configuration)
            for _, potential_controller in inspect.getmembers(Controller):
                if isinstance(potential_controller, controllers.Controller):
                    child_controller = potential_controller
                    _configure(child_controller, Controller.configuration)
        for Controller in self.routes.values():
            _configure(Controller, self.configuration)
        
    def __call__(self, environ, start_response):
        try:
            request = webob.Request(environ)
            response = webob.Response()
            # extract relevant details from request
            url = request.path
            method = request.method.lower()
            # find appropriate handler
            Controller, args, kwargs = routing.match(self.routes, url, method)
            # Controller will be None if there is no appropriate match
            if Controller is None:
                raise exceptions.HTTPNotFound
            # Controller configuration should allow this method
            allowed_methods = getattr(Controller, 'allowed_methods', set())
            if method not in allowed_methods:
                raise exceptions.HTTPMethodNotAllowed
            # extract appropriate handler an call it (should never fail)
            controller = Controller(request, response)
            handler = getattr(controller, method)
            controller.before()
            returned = handler(*args, **kwargs)
            controller.after(returned)
            logger.info(self.format_log(request, response))
        except exceptions.HTTPException as http_exception:
            response = utilities.copy_headers(response, http_exception)
            logger.warning(self.format_log(request, response))
        except Exception as exception:
            http_exception = exceptions.HTTPInternalServerError
            response = utilities.copy_headers(response, http_exception)
            logger.error(self.format_err(traceback.format_exc(), request, 
                                         response))
        finally:
            try:
                controller.lastly(response)
            except:
                error_message = '\n{}\n\n{}'.format('Exception in lastly.',
                                                    traceback.format_exc())
                logger.error(error_message)
            finally:
                return response(environ, start_response)

    def add_route(self, route, Controller):
        route = utilities.Url(route)
        self.routes[route] = Controller
        
    def add_asset(self, route, path):
        pass

    def format_log(self, request, response):
        now = datetime.datetime.utcnow().isoformat()[:23]
        return '{} {} {} {} {}'.format(now, request.client_addr.ljust(15),
                                       response.status_code,
                                       request.method,
                                       request.path)

    def format_err(self, err, request, response):
        return '\n{}\n\n{}'.format(self.format_log(request, response), err)


app = application = Application()


def serve(port=8080, host='127.0.0.1', threads=10, app=application):
    application.configure()
    waitress.serve(app, host=host, port=port)
