"""
a base class whose attributes are read-only,
unless use the context  _context_allow_change to change attributes
"""
from contextlib import contextmanager


class AttributeReadOnlyError(Exception):
    def __init__(self, obj: object, attr: str):
        self.obj = obj
        self.attr = attr

    def __str__(self):
        return "'%s' attribute '%s' is read-only" % (type(self.obj).__name__, self.attr)


class ReadOnlySpace(object):
    """
    a base class whose attributes are read-only,
    unless use the context  _context_allow_change to change attributes
    """

    def __setattr__(self, name, value):
        """ attributes could not be change, unless in context _context_allow_change"""
        if name == 'ALLOW_CHANGE':
            raise AttributeError("attribute name 'ALLOW_CHANGE' has been occupied, please use another name")
        if getattr(self, 'ALLOW_CHANGE', None):
            self.__dict__[name] = value
        else:
            raise AttributeReadOnlyError(self, name)

    @contextmanager
    def _context_allow_change(self):
        """
        the context in which attributes could be change
        for example:

        1.wrong way: would raise AttributeReadOnlyError
            self.name = "hello"

        2.correct way: could change attribute
            with self._context_allow_change():
                self.name = "hello
        """
        try:
            self.__dict__['ALLOW_CHANGE'] = True
            yield
        finally:
            del self.__dict__['ALLOW_CHANGE']
