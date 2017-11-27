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
    # __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def untablify(self, obj_table):
        """
        Replace attribute that are ObjectTableReferences with the actual
        object in the table.  This allows us to defer assignment until
        everything is defined, so we can have syntax equivalent to
        x = [x]
        {x|array|x}
        """
        pass  # no attributes on superclass

# make int and float literals appear to be DataStructure subclasses
DataStructure.register(int)
DataStructure.register(float)

class Pointer(DataStructure):
    def __init__(self, referand):
        self.referand = referand

    def untablify(self, obj_table):
        self.referand = obj_table[self.referand]

class Array(collections.UserList, DataStructure):
    """An array data structure"""

    def untablify(self, obj_table):
        # UserList has its underlying list accessible as a member
        self.data = [obj_table[elt] for elt in self.data]

class Null(DataStructure):
    """A null value.  Similar to python's None.  Should only ever be instantiated once."""
    __instance = None
    def __init__(self):
        if type(self).__instance is not None:
            return type(self).__instance
        else:
            type(self).__instance = self
            return super().__init__()

    def untablify(self, obj_table):
        pass
    def __bool__(self):
        return False
# Ensure that future attempts to make a Null will fail:
Null = Null()


class LinkedListNode(DataStructure):
    def __init__(self, value, successor=Null):
        self.value = value
        self.successor = successor

    def untablify(self, obj_table):
        self.value = obj_table[self.value]
        self.successor = obj_table[self.successor]

class Graph(DataStructure):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def untablify(self, obj_table):
        print(self.nodes)
        print(self.edges)
        self.nodes = [obj_table[n] for n in self.nodes]
        self.edges = [obj_table[e] for e in self.edges]

class Node(DataStructure):
    def __init__(self, data, edges, metadata=None):
        self.data = data
        # self.edges = edges  # no storing edges, I guess.  TODO: discuss this with people
        self.metadata = {} if metadata is None else metadata

    def untablify(self, obj_table):
        self.data = obj_table[self.data]
        # self.edges = list(obj_table[e] for e in self.edges)

class Edge(DataStructure):
    def __init__(self, orig, dest, data=Null, metadata=None):
        # The use of both Null and None is intentional, since metadata should
        # not be a DataStructure.
        self.orig = orig
        self.dest = dest
        self.data = data
        self.metadata = metadata
        if self.metadata is None:
            self.metadata = {}

    def untablify(self, obj_table):
        self.orig = obj_table[self.orig]
        self.dest = obj_table[self.dest]
        self.data = obj_table[self.data]

class Widget(DataStructure):
    # Potentially our most useful DataStructure
    def __init__(self, metadata=None):
        # metadata might be useful, e.g. if we want 2 types of widgets
        if metadata is None:
            self.metadata = {}
        else:
            self.metadata = metadata

    def untablify(self, obj_table):
        pass

class BinaryTree(DataStructure):
    def __init__(self, root):
        self.root = root

    def untablify(self, obj_table):
        self.root = obj_table[self.root]

    def __eq__(self, other):
        return isinstance(other, BinaryTree) and self.root == other.root

# class BinaryTreeEdge(Edge):
#     pass

class BinaryTreeNode(DataStructure):

    def __init__(self, data, left=None, right=None):
        # We don't handle storing data on the edges.  If somebody wants it, we'll add it.
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

class String(collections.UserString, DataStructure):
    def untablify(self, obj_table):
        pass

# class Struct(DataStructure):
#     """A bunch of stuff all in one place"""
#     # def __init__(self
#     TODO
