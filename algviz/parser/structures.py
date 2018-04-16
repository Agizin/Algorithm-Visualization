import collections
import abc

class ObjectTable(dict):
    """A table of references to objects.  Used to retrieve an object given its UID.

    May be extended later for more interesting parser behaviors.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self[ObjectTableReference(Null.uid)] = Null

    def __setitem__(self, key, val):
        if not isinstance(key, ObjectTableReference):
            raise TypeError("Key must be an `ObjectTableReference`, not {}".format(key))
        return super().__setitem__(key, val)

    def __getitem__(self, key):
        if isinstance(key, ObjectTableReference):
            return super().__getitem__(key)
        elif isinstance(key, DataStructure):
            return key
        else:
            raise TypeError("Expected a DataStructure or an ObjectTableReference, not {!r}"
                            .format(key))

    def finalize(self):
        for obj in self.values():
            if hasattr(obj, 'untablify'):
                obj.untablify(self)

    def getuid(self, uid):
        """Convenience method to return the object with the given uid (`str` type)"""
        if not isinstance(uid, str):
            raise TypeError("uid must be a string, not {}".format(uid))
        return self[ObjectTableReference(uid=uid)]

ObjectTableReference = collections.namedtuple("ObjectTableReference", ("uid",))

Snapshot = collections.namedtuple("Snapshot", ("names", "obj_table"))

class DataStructure(metaclass=abc.ABCMeta):

    def __init__(self, uid=None, metadata=None):
        self.uid = uid
        if metadata is not None:
            self.metadata = metadata
        else:
            self.metadata = {}

    def same_object(self, other):
        """Does `other` represent the same object, possibly at a different
        moment in time?

        The values of `self.__eq__(other)` and `self.same_object(other)`
        are independent.
        """
        return type(self) == type(other) and self.uid == other.uid

    @abc.abstractmethod
    def untablify(self, obj_table):
        """
        Replace attribute that are `ObjectTableReference`s with the actual
        object in the table.  This allows us to defer assignment until
        everything is defined, so circular references can never cause problems.
        """
        pass

    def __eq__(self, other):
        return (isinstance(other, DataStructure) and
                # registered subclasses may have no uid attribute
                hasattr(other, "uid") and
                other.uid == self.uid)

    def __hash__(self):
        return hash(ObjectTableReference(self.uid))

# make int and float literals appear to be DataStructure subclasses
DataStructure.register(int)
DataStructure.register(float)

class Pointer(DataStructure):
    def __init__(self, referent, **kwargs):
        super().__init__(**kwargs)
        self.referent = referent

    def __eq__(self, other):
        # Usually we want to compare pointers by UID, not by the value of referent.
        # However, these __eq__ methods are very useful for testing
        return (super().__eq__(other) and
                isinstance(other, Pointer) and
                other.referent == self.referent)

    def untablify(self, obj_table):
        self.referent = obj_table[self.referent]

    def __hash__(self):
        return super().__hash__()

class Array(collections.UserList, DataStructure):
    """An array data structure"""
    def __init__(self, *args, **kwargs):
        collections.UserList.__init__(self, *args)
        DataStructure.__init__(self, **kwargs)

    def untablify(self, obj_table):
        # UserList has its underlying list accessible as a member
        self.data = [obj_table[elt] for elt in self.data]

    def __eq__(self, other):
        return (isinstance(other, Array) and
                DataStructure.__eq__(self, other) and
                collections.UserList.__eq__(self, other))

    def __hash__(self):
        return DataStructure.__hash__(self)

class _Singleton(abc.ABCMeta):
    # Embarassingly copied from https://stackoverflow.com/questions/6760685
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class NullType(DataStructure, metaclass=_Singleton):
    """A null value.  Similar to python's None.  Fun to make."""
    def __init__(self):
        super().__init__(uid="#null")
        del self.metadata  # no static dictionary allowed

    def untablify(self, obj_table):
        pass

    def __bool__(self):
        return False

    def __repr__(self):
        return "Null"

Null = NullType()

class LinkedListNode(DataStructure):
    def __init__(self, value, successor=Null, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.successor = successor

    def untablify(self, obj_table):
        self.value = obj_table[self.value]
        self.successor = obj_table[self.successor]

class Graph(DataStructure):
    def __init__(self, nodes, edges, **kwargs):
        super().__init__(**kwargs)
        self.nodes = frozenset(nodes)
        self.edges = frozenset(edges)

    def untablify(self, obj_table):
        self.nodes = frozenset(obj_table[n] for n in self.nodes)
        self.edges = frozenset(obj_table[e] for e in self.edges)

    def __eq__(self, other):
        return (isinstance(other, Graph) and
                super().__eq__(other) and
                self.nodes == other.nodes and
                self.edges == other.edges)

    def __hash__(self):
        return super().__hash__()

class Node(DataStructure):
    # This is a minimal node that isn't responsible for its own edges.  This
    # allows for a more flexible graph implementation (i.e. allowing subgraphs
    # over the same nodes).  If you want to store edges within your node, use
    # TreeNode or a subclass instead of this.
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    def untablify(self, obj_table):
        self.data = obj_table[self.data]

    def __eq__(self, other):
        return (super().__eq__(other) and
                isinstance(other, Node) and
                other.data == self.data)

    def __hash__(self):
        return super().__hash__()

class Edge(DataStructure):
    def __init__(self, orig, dest, data=Null, **kwargs):
        super().__init__(**kwargs)
        self.orig = orig
        self.dest = dest
        self.data = data

    def untablify(self, obj_table):
        self.orig = obj_table[self.orig]
        self.dest = obj_table[self.dest]
        self.data = obj_table[self.data]

    def __eq__(self, other):
        return (super().__eq__(other) and
                isinstance(other, Edge) and
                other.orig == self.orig and
                other.dest == self.dest and
                other.data == self.data)

    def __hash__(self):
        return super().__hash__()

class Widget(DataStructure):
    # Potentially our most useful DataStructure
    # Represents a `void` or "don't care" type.
    def __eq__(self, other):
        return isinstance(other, Widget) and super().__eq__(other)

    def untablify(self, obj_table):
        pass

    def __hash__(self):
        return super().__hash__()

class TreeNode(DataStructure):
    """A node with some number of children in a fixed order.  Edges are implicit."""
    # A common superclass could be used for linked-list nodes, since linked
    # lists are just skinny trees

    def __init__(self, data, children=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.children = [] if children is None else children

    def is_leaf(self):
        return len(self.children) == 0
        
    def width(self):
        if self.is_leaf():
            return 1
        width = max(len(self.children),1)
        for child in self.children:
            child_width = child.width()
            width = max(width, child_width)
        return width

    def height(self):
        if self.is_leaf():
            return 1
        height = 0
        for child in self.children:
            if child is not None:
                child_height = child.height()
                height = max(height,child_height)
        return height + 1

    def untablify(self, obj_table):
        self.data = obj_table[self.data]
        self.children = [obj_table[child] for child in self.children]

    def __eq__(self, other):
        return (super().__eq__(other) and
                isinstance(other, TreeNode) and
                self.data == other.data and
                self.children == other.children)

    def __hash__(self):
        return super().__hash__()

class String(collections.UserString, DataStructure):

    def __init__(self, value, **kwargs):
        collections.UserString.__init__(self, value)
        DataStructure.__init__(self, **kwargs)

    def untablify(self, obj_table):
        pass

    def __eq__(self, other):
        return (isinstance(other, String) and
                DataStructure.__eq__(self, other) and
                collections.UserString.__eq__(self, other))

    def __hash__(self):
        return DataStructure.__hash__(self)
