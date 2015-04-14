# standard libraries
import os
# third party libraries
pass
# first party libraries
from . import (routing, utilities, exceptions, application, controllers,
               static, authentication)

Controller = controllers.Controller
app = application.app
serve = application.serve
logger = application.logger
Application = application.Application
application = application.application

_where = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_where, '..', 'VERSION'), 'rb') as f:
    __version__ = f.read()

__all__ = ['__version__', 'routing', 'utilities', 'exceptions', 'app',
           'application', 'Application', 'authentication', 'Controller',
           'static', 'logger']
