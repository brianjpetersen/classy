# standard libraries
import unittest
# third party libraries
import webob
# first party libraries
import classy

class Root(classy.Controller):

    def get(self):
        pass

classy.app.add_route('/', Root)

class TestApp(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()