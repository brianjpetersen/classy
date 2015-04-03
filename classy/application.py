# standard libraries
import traceback
# third party libraries
import webob
import waitress
# first party libraries
import routing
import utilities
import http_exceptions as exceptions

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
            controller, args, kwargs = routing.match(self.routes, url, method)
            if controller is None:
                raise exceptions.HTTPNotFound
            instance = controller(request, response, **self.configuration)
            handler = getattr(instance, method)
            response.content = handler(*args, **kwargs) or ''
        except exceptions.HTTPException, http_exception:
            response = utilities.copy_headers(response, http_exception)
        except Exception, exception:
            print(traceback.format_exc())
            http_exception = exceptions.HTTPInternalServerError()
            response = utilities.copy_headers(response, http_exception)
        finally:
            return response(environ, start_response)

    def add_route(self, route, controller):
        route = routing.Url(route)
        self.routes[route] = controller

app = application = Application()

def serve(host='127.0.0.1', port=8080, app=application):
    waitress.serve(app, host=host, port=port)