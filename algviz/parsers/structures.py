import collections
import abc

class ObjectTable(dict):
    """A table of references to objects.  Used to retrieve an object given its UID.

    May be extended later for more interesting parser behaviors.
    """
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
        return isinstance(other, Pointer) and other.referent == self.referent

    def untablify(self, obj_table):
        self.referent = obj_table[self.referent]

class Array(collections.UserList, DataStructure):
    """An array data structure"""
    def __init__(self, *args, **kwargs):
        collections.UserList.__init__(self, *args)
        DataStructure.__init__(self, **kwargs)

    def untablify(self, obj_table):
        # UserList has its underlying list accessible as a member
        self.data = [obj_table[elt] for elt in self.data]

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
    def __init__(self, value, successor=Null):
        self.value = value
        self.successor = successor

    def untablify(self, obj_table):
        self.value = obj_table[self.value]
        self.successor = obj_table[self.successor]

class Graph(DataStructure):
    def __init__(self, nodes, edges, **kwargs):
        super().__init__(**kwargs)
        self.nodes = nodes
        self.edges = edges

    def untablify(self, obj_table):
        self.nodes = [obj_table[n] for n in self.nodes]
        self.edges = [obj_table[e] for e in self.edges]

class Node(DataStructure):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        # self.edges = edges  # no storing edges, I guess.  TODO: discuss this with people

    def untablify(self, obj_table):
        self.data = obj_table[self.data]
        # self.edges = list(obj_table[e] for e in self.edges)

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

class Widget(DataStructure):
    # Potentially our most useful DataStructure

    def __eq__(self, other):
        return isinstance(other, Widget)

    def untablify(self, obj_table):
        pass

class BinaryTree(DataStructure):
    def __init__(self, root, **kwargs):
        super().__init__(**kwargs)
        self.root = root

    def untablify(self, obj_table):
        self.root = obj_table[self.root]

    def __eq__(self, other):
        return isinstance(other, BinaryTree) and self.root == other.root

    def __repr__(self):
        return "bintree(uid={},root={!r})".format(self.uid, self.root)

class BinaryTreeNode(DataStructure):

    def __init__(self, data, left=None, right=None, **kwargs):
        # We don't handle storing data on the edges.  If somebody wants it, we'll add it.
        super().__init__(**kwargs)
        if left is None:
            left = Null
        if right is None:
            right = Null
        self.left = left
        self.right = right
        self.data = data

    def untablify(self, obj_table):
        self.left = obj_table[self.left]
        self.right = obj_table[self.right]
        self.data = obj_table[self.data]

    def __eq__(self, other):
        return (isinstance(other, BinaryTreeNode) and
                other.data == self.data and
                other.left == self.left and
                other.right == self.right)

    def __repr__(self):
        return "btnode(uid={},{},left={!r},right={!r})".format(
            self.uid, self.data, self.left, self.right)

class String(collections.UserString, DataStructure):
    def __init__(self, *args, **kwargs):
        collections.UserString.__init__(self, *args)
        DataStructure.__init__(self, **kwargs)
    def untablify(self, obj_table):
        pass

# class Struct(DataStructure):
#     """A bunch of stuff all in one place"""
#     # def __init__(self
#     TODO
