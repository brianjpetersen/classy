# standard libraries
import traceback
# third party libraries
import webob
# first party libraries
import routing
import http_exceptions as exceptions

class Application(object):

    config = {}
    routes = {}

    def __call__(self, environ, start_response):
        request = webob.Request(environ)
        response = webob.Response()
        #
        url = request.path
        method = request.method.lower()
        try:
            # find appropriate handler
            controller, args, kwargs = routing.match(self.routes, url, method)
            if controller is None:
                raise exceptions.HTTPMethodNotAllowed
            instance = controller(request, response, **self.config)
            handler = getattr(instance, method)
            instance.before_handler_called()
            response.body = handler(*args, **kwargs) or ''
            instance.before_response_returned()
        except exceptions.HTTPException, http_exception:
            response = http_exception
        except Exception, exception:
            response = exceptions.HTTPInternalServerError(exception)
            print traceback.format_exc()
        finally:
            return response(environ, start_response)

    def add_route(self, route, controller):
        route = routing.Url(route)
        self.routes[route] = controller

application = Application()

def serve(app=application, host='127.0.0.1', port=8080):
    try:
        import waitress
        waitress.serve(app, host=host, port=port)
    except:
        from wsgiref.simple_server import make_server
        server = make_server(host, port, app)
        server.serve_forever()

if __name__ == '__main__':
    request = webob.Request.blank('https://brian:pw@www.podimetrics.com/test/b/a?a=b&c=d&a=c')
    print dir(request)
    print request.cookies
    print request.path
    print request.params
    print request.method