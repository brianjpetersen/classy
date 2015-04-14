import classy
import os

_where = os.path.dirname(os.path.abspath(__file__))

class ImportAntigravity(classy.static.FileController):

    filename = os.path.join(_where, 'python.png')

class Root(classy.controllers.Controller):

    anti_gravity = ImportAntigravity

    def get(self):
        return 'Sampling everything in the medicine cabinet!'

classy.app.add_route('/', Root)
classy.app.add_favicon(os.path.join(_where, 'python.ico'))
classy.serve()