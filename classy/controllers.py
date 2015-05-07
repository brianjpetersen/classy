# standard libraries
import copy
import inspect
# third party libraries
pass
# first party libraries
from . import utilities


__all__ = ('Controller', )


_Class = type('_', (object, ), {})
_Instance = _Class()
_class_attrs = dir(_Class)
_instance_attrs = dir(_Instance)


class ControllerMetaclass(type):
    """ Deep copy class attributes upon inheritence and instantiation.
    
        This is necessary specifically for mutable objects that are defined
        prior to instantiation or inheritence.  If it were not done, there
        could be shared references among controller instances and between
        children and parent classes.  Using this metaclass creates context
        locals of any class attributes during subclassing and instantiation.
    
    """
    def __new__(cls, name, bases, attrs):
        Controller = type.__new__(cls, name, bases, attrs)
        for attr, value in inspect.getmembers(Controller):
            if attr in _class_attrs or callable(value):
                continue
            try:
                value = copy.deepcopy(value)
            except:
                continue
            setattr(Controller, attr, value)
        return Controller

    def __setattr__(cls, attr, value):
        try:
            value = copy.deepcopy(value)
        except:
            pass
        type.__setattr__(cls, attr, value)
        
    def __call__(cls, *args, **kwargs):
        instance = type.__call__(cls, *args, **kwargs)
        for attr, value in inspect.getmembers(instance):
            if attr in _instance_attrs or callable(value):
                continue
            try:
                value = copy.deepcopy(value)
            except:
                continue
            setattr(instance, attr, value)
        return instance


class Controller(metaclass=ControllerMetaclass):

    configuration = {}
    allowed_methods = set(('get', 'head', 'put', 'post', 'patch', 'delete'))

    def __init__(self, request, response):
        self.request = request
        self.response = response

    @classmethod
    def configure(cls, configuration):
        cls.configuration.update(configuration)
    
    def before(self):
        pass

    def after(self, returned):
        if isinstance(returned, str):
            self.response.text = returned
        elif isinstance(returned, bytes):
            self.response.body = returned

    def lastly(self, response):
        pass
    
    get = utilities._raise_method_not_allowed
    head = utilities._raise_method_not_allowed
    put = utilities._raise_method_not_allowed
    post = utilities._raise_method_not_allowed
    patch = utilities._raise_method_not_allowed
    delete = utilities._raise_method_not_allowed
