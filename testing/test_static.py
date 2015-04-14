import classy
import os

_where = os.path.dirname(os.path.abspath(__file__))

class ImportAntigravity(classy.static.FileController):

    filename = os.path.join(_where, 'python.png')

class Root(classy.controllers.Controller):

    anti_gravity = ImportAntigravity

    def get(self):
        return u'Hello World!'# chr(0) #'here'

classy.app.add_route('/', Root)
classy.app.add_favicon(os.path.join(_where, 'python.ico'))
classy.serve()

"""
if self.cache:
    etag_hash = hash((file_iterator.last_modified,
                      file_iterator.content_length,
                      self.filename))
    self.response.etag = str(etag_hash)
    self.response.conditional_response = True
    self.response.last_modified = file_iterator.last_modified
"""