# standard libraries
import os
# third party libraries
pass
# first party libraries
import http_exceptions as exceptions
import routing
from controllers import Controller
from application import Application, application, serve

_where = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_where, '..', 'VERSION'), 'rb') as f:
    __version__ = f.read()