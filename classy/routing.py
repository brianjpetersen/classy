# standard libraries
import inspect
import collections
import copy
# third party libraries
import webob
# first party libraries
from . import (exceptions, controllers, utilities)


def _match_controller(controller, url, http_method,
                      previously_matched_depth=0,
                      previously_matched_arguments=None):
    """ Attempts a single-pass match of the URL against the controller.

        This helper function is intended to be called only from the more 
        general match function defined below and from itself, recursively.
        It takes as input a URL (assumed to be a utilities.Url object) and 
        attempts to match this URL against a controller object (which is a 
        subclass of controller.Controller).  

        First, the controller object is introspected to determine if it has 
        an attribute named http_method.  If it does have an attribute named 
        http_method that is callable, it is a potentially-matching method's 
        and this method's signature is extracted.  If not, this controller 
        cannot match the URL and an empty list is returned.
        
        If the signature of the potentially-matching method matches the 
        entirety of the URL in addition to any additional previously-matched 
        arguments (supplied as input in the previously_matched_arguments 
        dict), then the match is successful.  The format of a match is a 
        tuple with the following elements:

        1. previously_matched_depth: how many controllers have been consumed 
           to construct this match?
        2. unmatched_wildcard_arguments: how many segments of the URL were 
           ultimately matched as unnamed args?
        3. controller: the matching controller that has as an attribute the 
           matching method handler
        4. keyword_arguments: a dict of URL segments that have been matched 
           against the matching method handler's signature

        This match object is appended to the matches list which is ultimately 
        returned by this function.

        After attempting a match on the entirety of the URL, this function 
        then attempts to incrementally match the URL against branching child 
        controllers; if one is found, the function recurses against the child
        controller and the unmatched portion of the URL.  For a portion of 
        the URL to match a child controller, the following conditions must 
        be met:

        1. a segment of the URL must be an attribute of the parent controller
        2. the attribute must be a subclass of controllers.Controller
        3. the segments of the URL preceding 

        If these three conditions are satisifed, the URL matches the child 
        controller, and this function is called recursively on the unmatched 
        segments of the URL with the following arguments:

        1. controller: the potentially-matching child controller
        2. url: the portion of the URL that wasn't matched against 
           the method handler siganture
        3. http_method: unchanged
        4. previously_matched_depth: incremented by one
        5. previously_matched_arguments: all arguments matched against 
           the method handler signature (including the currently 
           previously_matched_arguments and any default arguments to 
           the method handler)
        
        The returned values from recursing on these potentially-matching 
        controllers extend the matches list.

    >>> class People(controllers.Controller):
    ...
    ...     def get(self, person_id=None):
    ...         pass
    ...
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/'), 
    ...                             http_method='get')
    >>> matches == [(0, 0, People, {})]
    True
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/brianjpetersen'), 
    ...                             http_method='get')
    >>> matches == [(0, 0, People, {'person_id': 'brianjpetersen'})]
    True
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/brianjpetersen/settings'), 
    ...                             http_method='get')
    >>> matches == []
    True


    >>> class People(controllers.Controller):
    ...
    ...     def get(self, person_id, *args, **kwargs):
    ...         pass
    ...
    >>> matches = _match_controller(People, utilities.Url('/'),
    ...                             http_method='get')
    >>> matches == []
    True
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/brianjpetersen/settings'), 
    ...                             http_method='get')
    >>> matches == [(0, 1, People, {'person_id': 'brianjpetersen', 
    ...                             'args': ('settings', )})]
    True


    >>> class Scans(controllers.Controller):
    ...
    ...     def get(self, scan_id=None, person_id=None):
    ...         pass
    ...
    >>> class People(controllers.Controller):
    ...
    ...     scans = Scans
    ...     
    ...     def get(self, person_id, *args, **kwargs):
    ...         pass
    ...
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/brianjpetersen/settings'), 
    ...                             http_method='get')
    >>> matches == [(0, 1, People, {'person_id': 'brianjpetersen', 
    ...                             'args': ('settings',)})]
    True
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/brianjpetersen/scans'), 
    ...                             http_method='get')
    >>> matches == [(0, 1, People, {'person_id': 'brianjpetersen', 
    ...                             'args': ('scans',)}), 
    ...             (1, 0, Scans,  {'person_id': 'brianjpetersen'})]
    True
    >>> matches = _match_controller(People, 
    ...                             utilities.Url('/brianjpetersen/scans/12345'), 
    ...                             http_method='get')
    >>> matches == [(0, 2, People, {'person_id': 'brianjpetersen', 
    ...                             'args': ('scans', '12345')}), 
    ...             (1, 0, Scans,  {'person_id': 'brianjpetersen', 
    ...                             'scan_id': '12345'})]
    True
    >>> _url = '/brianjpetersen/scans/12345/extra/url/args'
    >>> matches = _match_controller(People,
    ...                             utilities.Url(_url),
    ...                             http_method='get')
    >>> matches == [(0, 5, People, {'person_id': 'brianjpetersen', 
    ...                             'args': ('scans', '12345', 'extra', 
    ...                                      'url', 'args')})]
    True

    """
    # pre-process arguments
    if previously_matched_arguments is None:
        previously_matched_arguments = {}
    # define return list
    matches = []
    # does the supplied controller have a child (which is a subclass of 
    # controllers.Controller) that matches the first element of the URL?
    # if so, recurse
    url_has_depth = len(url) > 0
    if url_has_depth:
        url_segment = url[0]
        url_attribute = getattr(controller, url_segment.normalized, type(None))
        attribute_is_controller = issubclass(url_attribute,
                                             controllers.Controller)
        if attribute_is_controller:
            potential_controller = url_attribute
            branched_matches = _match_controller(potential_controller, 
                                                 url[1:], http_method,
                                                 (previously_matched_depth + 1), 
                                                 previously_matched_arguments)
            matches.extend(branched_matches)
    # does controller have a method matching the HTTP method?
    # if so, extract method signature details and attempt to match the URL
    # against the method
    handler = getattr(controller, http_method, None)
    handler_is_method = callable(handler)
    if handler_is_method:
        method_handler = handler
        # extract method signature details
        method_signature = inspect.signature(method_handler)
        # attempt to match the the entirety of the URL against the method 
        # handler's signature
        try:
            # skipping the first method argument, which is self and is
            # implicitly matched to the controller class; adding it here
            # and deleting it from the returned bound arguments
            positional_arguments = ['self', ]
            positional_arguments.extend([str(u) for u in url])
            bound_arguments = method_signature.bind(*positional_arguments, 
                                                    **previously_matched_arguments)
            # if we delete self, the returned bound arguments no longer match the
            # signature, and all positional arguments are defined in kwargs;
            # any wildcard positional arguments are also explicitly defined as 
            # a kwarg
            # for example, foo(a, *args) evaluated as foo(1, 2, 3) yields 
            # kwargs={'a': 1, 'args': (2, 3)}
            del bound_arguments.arguments['self']
            # we seek first to maximize the match depth, then to minimize the 
            # number of unmatched wildcard arguments.  at this stage of the 
            # matching process, the match depth is the same as the controller 
            # passed as input to this function
            unmatched_wildcard_arguments = 0
            for argument in bound_arguments.signature.parameters.values():
                argument_is_wildcard_positional = (argument.kind ==
                                                   argument.VAR_POSITIONAL)
                argument_is_bound = (argument.name in bound_arguments.arguments)
                if argument_is_bound and argument_is_wildcard_positional:
                    unmatched_wildcard_arguments = len(bound_arguments.kwargs[argument.name])
                    break
            matches.append((previously_matched_depth,
                            unmatched_wildcard_arguments, controller,
                            bound_arguments.kwargs))
        except TypeError:
            pass
        # incrementally attempt to match the URL against controller attributes
        for url_position, url_segment in enumerate(url):
            url_attribute = getattr(controller, url_segment.normalized,
                                    type(None))
            attribute_is_controller = issubclass(url_attribute,
                                                 controllers.Controller)
            if attribute_is_controller:
                # if the url up to this controller match also matches the 
                # method signature, branch and recurse
                potential_controller = url_attribute
                # see comments above related to skipping the first method 
                # argument and how deleting self after the match results 
                # in all arguments (even wildcard positionals) being defined 
                # as kwargs
                positional_arguments = ['self', ]
                positional_arguments.extend([str(u)
                                             for u in url[:url_position]])
                try:
                    bound_arguments = method_signature.bind(
                        *positional_arguments, **previously_matched_arguments)
                except TypeError:
                    continue
                del bound_arguments.arguments['self']
                # extract relevant data so previously_matched_arguments can 
                # be correctly set for the next branch
                for argument in bound_arguments.signature.parameters.values():
                    # bound_arguments doesn't include default arguments, but 
                    # we need to pass them as previously_matched_arguments 
                    # when we recurse and branch
                    argument_not_bound = (argument.name not in
                                          bound_arguments.arguments)
                    argument_has_default = (argument.default is not
                                            argument.empty)
                    if argument_not_bound and argument_has_default:
                        name = argument.name
                        default = argument.default
                        bound_arguments.arguments[name] = default
                    # if any wildcard positional arguments have been matched, 
                    # then this controller is actually not a potential match 
                    # because it is ambiguous how the URL segments consumed 
                    # to fill *args should be marshalled to the next 
                    # potential handler as previously_matched_arguments 
                    # because once *args has been bound, binding adding 
                    # additional arguments to the cannot cause it to be 
                    # unbound, we are able to break out at this point
                    argument_is_wildcard_positional = (argument.kind ==
                                                       argument.VAR_POSITIONAL)
                    argument_is_bound = (argument.name in
                                         bound_arguments.arguments)
                    if argument_is_bound and argument_is_wildcard_positional:
                        return matches
                newly_matched_arguments = previously_matched_arguments.copy()
                newly_matched_arguments.update(bound_arguments.kwargs)
                # add arguments with defaults to previously_matched_arguments
                branched_matches = _match_controller(
                    potential_controller, url[(url_position + 1):],
                    http_method, (previously_matched_depth + 1),
                    newly_matched_arguments)
                matches.extend(branched_matches)
    return matches


def _extract_matches_sort_invariant(match):
    """ Given a match object (see _match_controller above), return a key 
        that when sorted on results in a list of match objects being sorted 
        on fitness.

        Note, we want to first maximize match_depth, and then minimize the 
        number of unmatched wildcard arguments.  Ties should be broken by 
        the order in which the routes were added and the controllers 
        processed, so the sorting algorithm ought to be stable.
    """
    matched_depth, unmatched_wildcard_arguments, _, _ = match
    return (matched_depth, -unmatched_wildcard_arguments)


def match(routes, url, method):
    """ Returns the best matching controller (and matched arguments to 
        the handler method) to the supplied URL.

    >>> class Scans(controllers.Controller):
    ...
    ...     def get(self, scan_id=None, person_id=None):
    ...         pass
    ...
    >>> class People(controllers.Controller):
    ...
    ...     scans = Scans
    ...     
    ...     def get(self, person_id, *args, **kwargs):
    ...         pass
    ...
    >>> routes = {'/people': People, '/scans': Scans}
    >>> Controller, kwargs = match(routes, '/', 'GET')
    >>> (Controller, kwargs) == (None, {})
    True
    >>> Controller, kwargs = match(routes, 
    ...                            '/people/brianjpetersen', 
    ...                            'GET')
    >>> (Controller, kwargs) == (People, {'person_id': 'brianjpetersen'})
    True
    >>> Controller, kwargs = match(routes, 
    ...                            '/people/brianjpetersen', 
    ...                            'POST')
    >>> controller = Controller(None, None)
    >>> handler = getattr(controller, 'post')
    >>> try:
    ...     handler(**kwargs)
    ... except exceptions.HTTPMethodNotAllowed:
    ...     print(True)
    True
    >>> Controller, kwargs = match(routes, 
    ...                            '/people/brianjpetersen/settings', 
    ...                            'GET')
    >>> (Controller, kwargs) == (People, {'person_id': 'brianjpetersen', 
    ...                                   'args': ('settings', )})
    True
    >>> Controller, kwargs = match(routes, 
    ...                            '/people/brianjpetersen/scans', 
    ...                            'GET')
    >>> (Controller, kwargs) == (Scans, {'person_id': 'brianjpetersen'})
    True
    >>> Controller, kwargs = match(routes, '/scans', 'GET')
    >>> (Controller, kwargs) == (Scans, {})
    True
    
    """
    # pre-process arguments
    method = method.lower()
    if not isinstance(url, utilities.Url):
        url = utilities.Url(url)
    # iterate over the routes dictionary, recursively looking in the parent 
    # controller for matches
    matches = []
    for route, controller in routes.items():
        # because this method is general, we shouldn't assume the URL will
        # come in as type utilities.URL; casting here as appropriate
        if not isinstance(route, utilities.Url):
            route = utilities.Url(route)
        route_matches_url = url.starts_with(route)
        if route_matches_url:
            match_depth = len(route)
            unmatched_url = url[match_depth:]
            # attempt matches against the root controller
            match = _match_controller(controller, unmatched_url, method,
                                      match_depth)
            matches.extend(match)
    if matches:
        best_match = max(matches, key=_extract_matches_sort_invariant)
        _, _, controller, kwargs = best_match
        return controller, kwargs
    else:
        return None, {}


if __name__ == '__main__':

    import doctest
    doctest.testmod()
