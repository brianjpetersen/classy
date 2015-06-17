# standard libraries
import unittest
# third party libraries
import webob
# first party libraries
import classy

class Root(classy.Controller):

    def get(self):
        return 'Hello World!'

classy.app.add_route('/', Root)

if __name__ == '__main__':
    classy.app.serve()