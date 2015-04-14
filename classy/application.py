# standard libraries
import traceback
import logging
# third party libraries
import webob
import waitress
# first party libraries
from . import (routing, utilities, exceptions, static)

class Application(object):

    configuration = {}
    routes = {}

    def __call__(self, environ, start_response):
        try:
            request = webob.Request(environ)
            response = webob.Response()
            # extract relevant details from request
            url = request.path
            method = request.method.lower()
            # find appropriate handler
            Controller, kwargs = routing.match(self.routes, url, method)
            if Controller is None:
                raise exceptions.HTTPNotFound
            controller = Controller(request, response, **self.configuration)
            handler = getattr(controller, method)
            handler_return = handler(**kwargs)
            controller.view(handler_return)
        except exceptions.HTTPException as http_exception:
            response = utilities.copy_headers(response, http_exception)
        except Exception as exception:
            # logging.error
            print(traceback.format_exc())
            http_exception = exceptions.HTTPInternalServerError()
            response = utilities.copy_headers(response, http_exception)
        finally:
            return response(environ, start_response)

    def add_route(self, route, Controller):
        route = utilities.Url(route)
        self.routes[route] = Controller

    def add_favicon(self, path):

        class FavIcon(static.FileController):
        
            filename = path

            def view(self, handler_return):
                self.response.content_type = 'image/x-icon'

        self.add_route('/favicon.ico', FavIcon)

app = application = Application()

def serve(host='127.0.0.1', port=8080, app=application, log_level=logging.INFO):
    logger = logging.getLogger('waitress')
    logger.setLevel(log_level)
    waitress.serve(app, host=host, port=port)