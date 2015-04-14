# standard libraries
import traceback
import datetime
import logging
# third party libraries
import webob
import waitress
# first party libraries
from . import (routing, utilities, exceptions, static)

logger = logging.getLogger('classy')
logger.setLevel(logging.INFO)

class Application(object):

    configuration = {}
    routes = {}

    def __call__(self, environ, start_response):
        try:
            request = self.request = webob.Request(environ)
            response = self.response = webob.Response()
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
            logger.info(self.format_log())
        except exceptions.HTTPException as http_exception:
            response = utilities.copy_headers(response, http_exception)
            logger.warning(self.format_log())
        except Exception as exception:
            logger.error(self.format_err(traceback.format_exc()))
            http_exception = exceptions.HTTPInternalServerError()
            response = utilities.copy_headers(response, http_exception)
        finally:
            return response(environ, start_response)

    def add_route(self, route, Controller):
        route = utilities.Url(route)
        self.routes[route] = Controller

    def format_log(self):
        now = datetime.datetime.utcnow().isoformat()[:23]
        request = self.request
        response = self.response
        return '{} {} {} {} {}'.format(now, request.client_addr.ljust(15),
                                       response.status_code,
                                       request.method,
                                       request.path)

    def format_err(self, err):
        sep = 20*'='
        return '\n{}\n{}\n\n{}{}'.format(sep, self.format_log(), err, sep)

    def add_favicon(self, path):
        class FavIcon(static.FileController):

            filename = path

            def view(self, handler_return):
                self.response.content_type = 'image/x-icon'

            put = utilities._raise_method_not_allowed

        self.add_route('/favicon.ico', FavIcon)


app = application = Application()


def serve(host='127.0.0.1', port=8080, app=application):
    waitress.serve(app, host=host, port=port)
