import abc

from algviz.parser.json_objects import Tokens

class Visitor(metaclass=abc.ABCMeta):

    def __init__(self, output_mngr, data_visitor=None):
        """Positional parameters:
        * An `algviz.interface.output.OutputManager` to use for output

        Keyword parameters:
        * data_visitor -- an instance of visitor to use on any data by default.
        If this is None, DispatchVisitor will be used.
        """
        self.output_mngr = output_mngr
        # assert hasattr(self, "type_"), "Visitor subclasses need a 'type_' attribute"
        self.data_visitor = data_visitor
        if data_visitor is None:
            self.data_visitor = DispatchVisitor(self.output_mngr)

    def uid(self, obj):
        """Return a unique identifier for this object.

        The identifier is guaranteed unique until the state of the objects
        under inspection is altered, i.e. until the objects are mutated,
        overwritten, or recounted.
        """
        return str(id(obj))

    def traverse(self, obj, **kwargs):
        # To traverse most simple objects, we can just visit them.
        # More complicated objects like graphs will require actual traversal
        if self.uid(obj) in self.output_mngr.uids:
            self.output_mngr.next_val(self.uid(obj))
        else:
            with self.output_mngr.push():
                self.visit(obj, **kwargs)

    @abc.abstractmethod
    def visit(self, obj, metadata=None, var=None):
        """
        Emit the inside of the JSON dictionary representing the given object.
        I.e. print out all the key-value pairs that represent the object.

        `visit()` shouldn't be called directly but may be called from within
        `traverse`.  Therefore when you implement `visit()` in subclasses, call
        `traverse` to visit your attributes.  (Or just use @algviz macros so
        you don't have to think about it.)
        """
        self.output_mngr.next_key(Tokens.TYPE)
        self.output_mngr.next_val(self.type_)
        self.output_mngr.next_key(Tokens.UID)
        self.output_mngr.next_val(self.uid(obj))
        if metadata is not None:
            self.output_mngr.next_key(Tokens.METADATA)
            self.output_mngr.next_val(metadata)
        if var is not None:
            self.output_mngr.next_key(Tokens.VARNAME)
            self.output_mngr.next_val(var)


class DispatchVisitor(Visitor):
    """Handle objects with a default handler.  Useful when data stored is of mixed types.

    Methods are dispatched to instances of an appropriate visitor based on the
    class of the given object.  The MRO is checked so that, e.g., a subclass of
    Foo will be handled by the Foo handler unless it has its own handler.

    By default, the handlers are given in `_dispatch_visit_dict`.  The
    `updates` keyword argument to `__init__` is used to modify the instance's
    copy of that dictionary for more customized behavior.
    """

    def __init__(self, output_mngr, updates=None, **kwargs):
        # If data_visitor is unspecified, a new instance of this class is
        # created.  So we must use `self` instead to prevent a crash.
        kwargs.setdefault("data_visitor", self)
        super().__init__(output_mngr, **kwargs)
        self.dispatch_dict = _dispatch_visit_dict.copy()
        if updates is not None:
            # This lets us do interesting things like choose non-default handlers for some data structure.  E.g. assume a `list` instance represents a heap
            self.dispatch_dict.update(updates)

    def _dispatch_method(self, methodname, obj, *args, **kwargs):
        # Call the named method on the appropriate visitor subclass
        for superclass in type(obj).mro():
            if superclass in self.dispatch_dict:
                # Get an appropriate visitor
                visitor = self.dispatch_dict[superclass](self.output_mngr, data_visitor=self)
                # Call the desired method on that visitor
                return getattr(visitor, methodname)(obj, *args, **kwargs)

    def uid(self, obj, **kwargs):
        return self._dispatch_method("uid", obj, **kwargs)

    def traverse(self, obj, *args, **kwargs):
        return self._dispatch_method("traverse", obj, *args, **kwargs)

    def visit(self, obj, *args, **kwargs):
        return self._dispatch_method("visit", obj, *args, **kwargs)

_dispatch_visit_dict = {
    # list: ArrayVisitor,
    # int: NumberVisitor,
}
def default_for_type(*types):
    """Decorated class will become the default visitor for the given type(s).
    See DispatchVisitor.

    Returns a decorator
    """
    def _decorator(cls):
        for type_ in types:
            assert type_ not in _dispatch_visit_dict, (
                "Multiple handlers for type {}: {} and {}".format(
                    type_, cls, _dispatch_visit_dict[type_]))
            _dispatch_visit_dict[type_] = cls
        return cls
    return _decorator

@default_for_type(list)
class ArrayVisitor(Visitor):
    """Visit an array, letting `self.data_visitor` traverse each item in the array.

    This visitor handles the array with `self.length` and `self.get_item`.  If
    your object implements __len__ and __getitem__, then you won't need to
    change those methods.  (On the other hand, you could override these methods
    to do something cool, e.g. treat an int as an array of True and False
    values.)
    """
    type_ = Tokens.ARRAY_T
    # We don't assume the object being treated as an Array is reasonable.
    # E.g. you could easily have an Array of bits represented by an int.

    def length(self, array):
        return len(array)

    def get_item(self, array, i):
        return array[i]

    def visit(self, array, *args, **kwargs):
        """
        context is guaranteed to be a dictionary context where the array body should go, or else
        If we make it here, somebody already checked that the uid hasn't been included in this snapshot yet.
        """
        super().visit(array, *args, **kwargs)  # UID and TYPE
        self.output_mngr.next_key(Tokens.DATA)
        with self.output_mngr.push(mapping=False):
            for i in range(self.length(array)):
                self.data_visitor.traverse(self.get_item(array, i))

# class TreeVisitor

@default_for_type(int, float)
class NumberVisitor(Visitor):

    def traverse(self, i, **kwargs):
        # A float or int can be handed straight to the output manager
        # This is a rare case where it's appropriate to reimplement `traverse`
        assert isinstance(i, (float, int))
        self.output_mngr.next_val(i)

    def visit(self, i, *args, **kwargs):
        raise NotImplementedError("Something has gone wrong if we're visiting an int (since visiting it implies making a JSON dictionary for it)")


@default_for_type(str)
class StringVisitor(Visitor):

    type_ = Tokens.STRING_T

    def to_str(self, obj):
        """Override this if you have some non-string object that you want to
        display as a string, and if calling `__str__` on it isn't good enough.
        (E.g. if you need to do `bytes.to_string(encoding="UTF-8")` instead.)

        `to_str` should return a string.
        """
        return str(obj)

    def visit(self, str_, *args, **kwargs):
        super().visit(str_, *args, **kwargs)
        self.output_mngr.next_key(Tokens.DATA)
        self.output_mngr.next_val(self.to_str(str_))

@default_for_type(object)
class WidgetVisitor(Visitor):
    """A Widget is a "don't care" object, quite like a `void*`"""
    type_ = Tokens.WIDGET_T

    def visit(self, *args, **kwargs):
        return super().visit(*args, **kwargs)

class LinkedListVisitor(Visitor):
    """Linked lists are represented as an array of an array and a current index, i.e.,
    [[1, 2, 3], 0]."""
    type_ = Tokens.ARRAY_T#treat this as an array, at least for now.

    def has_current(self, ll):
        return len(ll[0]) > ll[1] and ll[1] >= 0
    
    def has_next(self, ll):
        return ((len(ll[0]) - 1) > ll[1]) and ll[1] >= 0

    def get_item(self, ll):
        return ll[0][ll[1]]
    
    def get_next(self, ll):
        return [ll[0], ll[1] + 1]
        
    def visit(self, ll, *args, **kwargs):
        super().visit(ll, *args, **kwargs)  # UID and TYPE
        self.output_mngr.next_key(Tokens.DATA)
        with self.output_mngr.push(mapping=False):
            while self.has_current(ll):#make sure list has an element in it
                self.data_visitor.traverse(self.get_item(ll))
                ll = self.get_next(ll)

