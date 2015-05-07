# standard libraries
import collections
# third party libraries
pass
# first party libraries
from . import exceptions


def _raise_method_not_allowed(self, *args, **kwargs):
    raise exceptions.HTTPMethodNotAllowed


def copy_headers(source, destination):
    source_headers = source.headers.copy()
    destination.headers.update(source_headers)
    return destination


class UrlSegment:
    """ Convenience class that encapsulates logic for fuzzy comparison of 
        path segments and facilitates lookup of handlers by replacing invalid
        URL characters with underscores.

        >>> UrlSegment('patient-id') == UrlSegment('patient_id')
        True
        >>> UrlSegment('patient-id').normalized == 'patient_id'
        True

    """

    def __init__(self, segment):
        self.segment = segment
        self.normalized = segment.replace('-', '_').replace('.', '_')

    def __eq__(self, other):
        return self.normalized == other.normalized

    def __str__(self):
        return self.segment

    def __repr__(self):
        return "UrlPathSegment('{}')".format(self.segment)


class Url(collections.MutableSequence):
    """ Supports URL path traversal and comparison.  This doesn't 
        necessarily accurately reflect absolute paths 
        (ie, '/a/b/c' and 'a/b/c' are equivalent).

        >>> url1 = Url('/a/b/c')
        >>> url2 = Url('/a')
        >>> url3 = Url('/')
        >>> url4 = Url('/d')
        >>> url1.starts_with(url2)
        True
        >>> url2.starts_with(url1)
        False
        >>> url2.starts_with(url3)
        True
        >>> url2.starts_with(url4)
        False

    """

    def __init__(self, url):
        super().__init__()
        # may want to change this to a deque for efficiencies sake
        self.url_segments = [UrlSegment(u) for u in url.split('/') if u != '']

    def starts_with(self, other):
        if len(other) > len(self):
            return False
        else:
            return all([s == o
                        for s, o in zip(self.url_segments, other.url_segments)
                        ])

    def _get_url(self):
        return '/'.join(map(str, self.url_segments))
    url = property(_get_url)

    def insert(self, item, value):
        self.url_segments.insert(item, value)

    def __delitem__(self, item):
        del self.url_segments[item]

    def __setitem__(self, item):
        pass

    def __getitem__(self, item):
        if isinstance(item, slice):
            return Url('/'.join(map(str, self.url_segments[item])))
        else:
            return self.url_segments[item]

    def __len__(self):
        return len(self.url_segments)

    def __str__(self):
        return self.url

    def __repr__(self):
        return "Url('{}')".format(self.url)
