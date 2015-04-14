# standard libraries
import os
import mimetypes
# third party libraries
pass
# first party libraries
from .. import controllers
from .. import exceptions

# do not load mimetypes from Windows registry
mimetypes._winreg = None
# stdlib default is application/x-javascript
mimetypes.add_type('text/javascript', '.js')
# not among defaults
mimetypes.add_type('image/x-icon', '.ico')


class FileIterator(object):
    def __init__(self, filename, block_size=65536):
        self.filename = filename
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
            # TODO: this really ought to be checked at metaclass instantiation
            error_message = 'Filename does not exist or is not a \
                             file: {}'.format(self.filename)
            raise ValueError(error_message)
        content_type, content_encoding = mimetypes.guess_type(self.filename)
        self.response.content_type = content_type
        self.response.content_encoding = content_encoding

    def get(self):
        try:
            file_iterator = FileIterator(self.filename)
        except (IOError, OSError):
            # the file used to exist, but no longer does
            raise exceptions.HTTPGone
        self.response.content_length = file_iterator.content_length
        self.response.app_iter = file_iterator
        return file_iterator

    def put(self, *args):
        raise exceptions.HTTPNotImplemented


class DirectoryController(controllers.Controller):

    path = ''

    def __init__(self, *args, **kwargs):
        super(DirectoryController, self).__init__(*args, **kwargs)
        path_is_directory = os.path.isdir(self.path)
        if not path_is_directory:
            error_message = 'Path does not exist or is not a \
                             directory: {}'.format(self.path)
            raise ValueError(error_message)

    def get(self, *path_segments):
        if len(path_segments) > 0:
            relative_path = os.path.join(*path_segments)
        else:
            relative_path = ''
        absolute_path = os.path.abspath(os.path.join(self.path, relative_path))
        path_not_subhierarchy = not absolute_path.startswith(self.path)
        if path_not_subhierarchy:
            raise exceptions.HTTPForbidden
        path_exists = os.path.exists(absolute_path)
        if not path_exists:
            raise exceptions.HTTPNotFound
        path_is_file = os.path.isfile(absolute_path)
        if not path_is_file:
            # TODO: return directory listing index (configurable via metaclass)
            raise exceptions.HTTPForbidden
        try:
            file_iterator = FileIterator(absolute_path)
        except (IOError, OSError):
            # the file used to exist, but no longer does
            raise exceptions.HTTPGone
        self.response.content_length = file_iterator.content_length
        content_type, content_encoding = mimetypes.guess_type(absolute_path)
        self.response.content_type = content_type
        self.response.content_encoding = content_encoding
        self.response.app_iter = file_iterator
        return file_iterator

    def put(self, *path_segments):
        raise exceptions.HTTPNotImplemented
