# standard libraries
import os
import mimetypes
# third party libraries
pass
# first party libraries
from .. import controllers

# do not load mimetypes from Windows registry
mimetypes._winreg = None
# stdlib default is application/x-javascript
mimetypes.add_type('text/javascript', '.js')
# not among defaults
mimetypes.add_type('image/x-icon', '.ico')

__all__ = ['FileController', 'DirectoryController', ]

class FileIterator(object):

    def __init__(self, filename, block_size=65536):
        self.block_size = block_size
        self.file = open(filename, 'rb')
        self.last_modified = os.path.getmtime(filename)
        self.content_length = os.path.getsize(filename)

    def __iter__(self):
        try:
            data = self.file.read(self.block_size)
            while data:
                yield data
                data = self.file.read(self.block_size)
        finally:
            self.file.close()

class FileController(controllers.Controller):

    filename = ''

    def __init__(self, *args, **kwargs):
        super(FileController, self).__init__(*args, **kwargs)
        filename_is_file = os.path.isfile(self.filename)
        if not filename_is_file:
            raise ValueError('Filename does not exist or is not a file: {}'.format(self.filename))
        response = self.response
        response.content_type, response.content_encoding = mimetypes.guess_type(self.filename)

    def get(self):
        try:
            file_iterator = FileIterator(self.filename)
        except (IOError, OSError):
            # the file used to exit, but no longer does
            raise classy.exceptions.HTTPGone
        self.response.content_length = file_iterator.content_length
        self.response.app_iter = file_iterator

    def put(self, *args):
        raise NotImplemented

class DirectoryController(controllers.Controller):
    
    path = ''

    def get(self, *path_segments):
        relative_path = os.path.join(path_segments)
        absolute_path = os.path.abspath(os.path.join(self.path, relative_path))
        path_not_subhierarchy = not absolute_path.startswith(self.path)
        if path_not_subhierarchy:
            raise classy.exceptions.HTTPForbidden
        path_is_directory = os.path.isdir(absolute_path)
        if not path_is_directory:
            raise ValueError('Directory does not exist or is not a directory: {}'.format(self.path))

    def put(self, *path_segments):
        raise NotImplemented