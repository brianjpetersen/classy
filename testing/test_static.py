import classy
import os

_where = os.path.dirname(os.path.abspath(__file__))

class ImportAntigravity(classy.static.FileController):

    filename = os.path.join(_where, 'python.png')

class MontyPython(classy.static.DirectoryController):

    path = os.path.join(_where, 'static')

class Root(classy.controllers.Controller):

    anti_gravity = ImportAntigravity
    monty_python = MontyPython

    def get(self):
        return 'Sampling everything in the medicine cabinet!'

classy.app.add_route('/', Root)
classy.app.add_favicon(os.path.join(_where, 'python.ico'))
classy.serve()