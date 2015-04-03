# standard libraries
import inspect
import collections
import copy
# third party libraries
pass
# first party libraries
import http_exceptions
import controllers

class UrlSegment(object):
    """ Convenience class that encapsulates logic for fuzzy comparison of path segments and
        facilitates lookup of handlers by replacing invalid URL characters with underscores.

        >>> UrlSegment('patient-id') == UrlSegment('patient_id')
        True
        >>> UrlSegment('patient-id').normalized == 'patient_id'
        True

    """
    def __init__(self, segment):
        self.segment = segment
        self.normalized = segment.replace('-', '_')

    def __eq__(self, other):
        return self.normalized == other.normalized

    def __str__(self):
        return self.segment

    def __repr__(self):
        return "UrlPathSegment('{}')".format(self.segment)

class Url(collections.MutableSequence):
    """ Supports URL path traversal and comparison.  This doesn't necessarily accurately reflect 
        absolute paths (ie, '/a/b/c' and 'a/b/c' are equivalent).

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
        # may want to change this to a deque for efficiencies sake
        self.url_segments = map(UrlSegment, [u for u in url.split('/') if u <> ''])
    
    def starts_with(self, other):
        if len(other) > len(self):
            return False
        else:
            return all([s == o for s, o in zip(self.url_segments, other.url_segments)])

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

def _match_controller(controller, url, method, match_depth=0, previously_matched_arguments=None):
    if previously_matched_arguments is None:
        previously_matched_arguments = {}
    # 
    matches = []
    # attempt to match controller
    if len(url) > 0:
        url_segment = url[0]
        potential_controller = getattr(controller, str(url_segment), type(None))
        if issubclass(potential_controller, controllers.Controller):
            controller = potential_controller
            match_depth += 1
            match = _match_method_handler(controller, url[1:], method, match_depth, 
                                          previously_matched_arguments.copy())
            matches.extend(match)
            match = _match_controller(controller, url[1:], method, match_depth, 
                                      previously_matched_arguments.copy())
            matches.extend(match)
    return matches

def _match_method_handler(controller, url, method, match_depth=0, previously_matched_arguments=None):
    # pre-process arguments
    if previously_matched_arguments is None:
        previously_matched_arguments = {}
    # attempt to match method handler
    matches = []
    potential_method_handler = getattr(controller, method, None)
    valid_method_handler_exists = callable(potential_method_handler) and (method in valid_methods)
    if valid_method_handler_exists:
        # retrieve specifics on method handler signature
        method_signature = inspect.getargspec(potential_method_handler)
        accepts_args = method_signature.varargs is not None
        accepts_kwargs = method_signature.keywords is not None
        arguments = method_signature.args
        defaults = method_signature.defaults
        # nb: the if statement is necessary to avoid arguments_without_defaults being empty when
        #     len(defaults) is zero (ie, arguments[1:-len(defaults)] = arguments[1:-0] = [])
        if defaults is None:
            arguments_without_defaults = arguments[1:]
            arguments_with_defaults = []
        else:
            arguments_without_defaults = arguments[1:-len(defaults)]
            arguments_with_defaults = arguments[-len(defaults):]
        # is this method handler is consistent with previously matched arguments?
        accepts_previously_matched_arguments = all(arg in arguments_with_defaults
                                                   for arg in previously_matched_arguments)
        if accepts_previously_matched_arguments or accepts_kwargs:
            # is it possible for the URL to match all arguments without defaults?
            all_arguments_without_defaults_matched = len(url) >= len(arguments_without_defaults)
            if all_arguments_without_defaults_matched:
                # match the URL segments to arguments without defaults
                matched_kwargs = previously_matched_arguments.copy()
                for argument in arguments_without_defaults:
                    matched_kwargs[argument] = str(url.pop(0))
                # attempt to match either the next controller branch attribute or
                # consume arguments until
                matched_args = []
                for url_position, url_segment in enumerate(url):
                    match = _match_controller(controller, url[url_position:], method, 
                                              match_depth, matched_kwargs.copy())
                    matches.extend(match)
                    if len(arguments_with_defaults) > 0:
                        matched_kwargs[arguments_with_defaults.pop(0)] = str(url_segment)
                    elif accepts_args:
                        matched_args.extend(map(str, url[url_position:]))
                        break
                    else:
                        return matches
                # normalize matched_kwargs and matched_args so that the kwargs that are actually
                # positional arguments 
                matches.append((match_depth, controller, matched_args, matched_kwargs))
                # for argument, default in zip(arguments, defaults):
                #     
                #matches.append((match_depth, controller, args, kwargs))
                #matches.append((match_depth, controller, [], {}))
    return matches

def match(controller_routes, url, method):
    # pre-process arguments
    method = method.lower()
    if not isinstance(url, Url):
        url = Url(url)
    # search for matches
    matches = []
    for route, controller in controller_routes.iteritems():
        if not isinstance(route, Url):
            route = Url(route)
        route_matches_url = url.starts_with(route)
        if route_matches_url:
            match_depth = len(route)
            unmatched_url = url[match_depth:]
            # attempt matches against the controller and the method handler, if any
            match = _match_method_handler(controller, unmatched_url, method, match_depth)
            matches.extend(match)
            match = _match_controller(controller, unmatched_url, method, match_depth)
            matches.extend(match)
    if matches:
        best_match = max(matches)
        _, controller, args, kwargs = best_match
        return controller, args, kwargs
    else:
        return None, [], {}

# TODO: cleanup match_depth
#       cleanup matched_kwargs and matched_args
#       use dict instead of list for matches
#       controller match (if len(url) > 0:) prefix is ugly
#       not found vs method not allowed
#       error handling in wsgi app is wonky

if __name__ == '__main__':

    import doctest
    doctest.testmod()

    class Scans(controllers.Controller):

        def get(self, scan_id, **kwargs):
            pass

    class Patients(controllers.Controller):
        
        scans = Scans

        def get(self, patient_id=None, *args, **kwargs):
            pass

    class Api(controllers.Controller):
        
        scans = Scans
        patients = Patients
        
        def get(self):
            pass

    import datetime
    start = datetime.datetime.now()
    for i in xrange(1):
        match = match({'/api': Api}, '/api/patients/patient_id/scans/scan_id', 'GET')
    end = datetime.datetime.now()
    print (end - start).total_seconds()
    print match