import json
from . import structures

class Tokens:
    # The same key used in a different context (i.e. a block of different type) might deserve a different symbol.
    UID = "uid"
    TYPE = "type"
    TO = "to"
    LEFT = "left"
    RIGHT = "right"
    FROM = "from"
    DATA = "data"
    GRAPH_NODES = "nodes"  # not a type, but an attribute of a graph
    GRAPH_EDGES = "edges"
    METADATA = "metadata"  # we probably should only use this for prototyping
    TREE_ROOT = "root"
    VARNAME = "var"  # the name of an object.  The VARNAME is what the user gives us to specify what we should draw.
    # Possible values for TYPE.  (Keep these alphabetized, please.)
    ARRAY = "array"
    BINARY_TREE = "bintree"
    BINARY_TREE_NODE = "btnode"
    EDGE = "edge"
    GRAPH = "graph"
    NODE = "node"
    NULL = "null"
    POINTER = "ptr"
    STRING = "string"
    WIDGET = "widget"

aliases = {
    # Shorter forms of tokens, to make it easier to handwrite these descriptions
    "T": Tokens.TYPE,
}

class JSONObjectError(Exception):
    pass

class Dispatcher(type):

    @staticmethod
    def dispatch(key):
        # decorate an object
        def _decorate(f):
            f._purpose = key
            return f
        return _decorate

    def __init__(cls, name, bases, namespace):
        # print(cls)
        # print(bases)
        cls._dispatcher = {}
        # cls._dispatch = lambda self, x: getattr(self, self._dispatcher[x])
        def _dispatch(self, key):
            if key not in self._dispatcher:
                raise JSONObjectError("{} is an invalid key or is not handled by {}"
                                      .format(key, type(self)))
            return getattr(self, self._dispatcher[key])

        cls._dispatch = _dispatch
        for attr_name, attr in namespace.items():
            if hasattr(attr, "_purpose"):
                assert attr._purpose not in cls._dispatcher, "Two functions for the same key in {}: {} and {}".format(name, attr, cls._dispatcher[attr._purpose])
                cls._dispatcher[attr._purpose] = attr_name
        return super(Dispatcher, cls).__init__(name, bases, namespace)

class SnapshotDecoder(metaclass=Dispatcher):
    # __metaclass__ = Dispatcher

    def __init__(self, *args, **kwargs):
        # at time of writing, args and kwargs should probably be empty
        self.objects = []  # maybe redundant
        self.table = structures.ObjectTable(*args, **kwargs)
        self.namespace = {}
        self._next_auto_uid = 0

    def auto_uid(self):
        result = "#{}".format(self._next_auto_uid)  # user-supplied tokens may not contain "#"
        self._next_auto_uid += 1
        return result

    def obj_hook(self, obj):
        if isinstance(obj, str):
            return structures.ObjectTableReference(uid=obj)
        elif isinstance(obj, (list, float, int)):
            # note that we may return a structures.Array if obj is a dict with "type": "array"
            return obj
        # fix_aliases(obj)
        # call the appropriate method for the type of the thing
        ref = structures.ObjectTableReference(obj.get(Tokens.UID,
                                                      self.auto_uid()))
        assert isinstance(obj[Tokens.TYPE], str), obj
        self.table[ref] = self._dispatch(obj[Tokens.TYPE])(obj)
        if Tokens.VARNAME in obj:
            self.namespace[obj[Tokens.VARNAME]] = ref
        return self.table[ref]

    # def tabulate(self, ref, obj):
    #     assert isinstance(ref, (structures.ObjectTableReference, str))
    #     if isinstance(ref, structures.ObjectTableReference):
    #         self.table[ref] = obj
    #     elif isinstance(ref, str):
    #         self.table[structures.ObjectTableReference(ref)] = obj

    @Dispatcher.dispatch(Tokens.ARRAY)
    def array_hook(self, array):
        return structures.Array(array[Tokens.DATA])

    @Dispatcher.dispatch(Tokens.BINARY_TREE)
    def binary_tree_hook(self, bintree):
        return structures.BinaryTree(root=bintree[Tokens.TREE_ROOT])

    @Dispatcher.dispatch(Tokens.BINARY_TREE_NODE)
    def binary_tree_node_hook(self, btnode):
        return structures.BinaryTreeNode(
            btnode.get(Tokens.DATA, structures.Null),
            left=btnode.get(Tokens.LEFT),
            right=btnode.get(Tokens.RIGHT),
        )

    @Dispatcher.dispatch(Tokens.EDGE)
    def edge_hook(self, edge):
        return structures.Edge(edge[Tokens.FROM], edge[Tokens.TO],
                               data=edge.get(Tokens.DATA, structures.Null),
                               metadata=edge.get(Tokens.METADATA, None))

    @Dispatcher.dispatch(Tokens.GRAPH)
    def graph_hook(self, graph):
        return structures.Graph(graph[Tokens.GRAPH_NODES], graph[Tokens.GRAPH_EDGES])

    @Dispatcher.dispatch(Tokens.NODE)
    def node_hook(self, node):
        return structures.Node(node.get(Tokens.DATA, structures.Null),
                               node.get(Tokens.GRAPH_EDGES, None))

    @Dispatcher.dispatch(Tokens.NULL)
    def null_hook(self, null):
        return structures.Null

    @Dispatcher.dispatch(Tokens.POINTER)
    def pointer_hook(self, ptr):
        return structures.Pointer(ptr[Tokens.DATA])

    @Dispatcher.dispatch(Tokens.STRING)
    def string_hook(self, string):
        return structures.String(string[Tokens.DATA])

    @Dispatcher.dispatch(Tokens.WIDGET)
    def widget_hook(self, widget):
        return structures.Widget(widget.metadata)

    def finalize(self):
        self.table.finalize()
        self.namespace = {key: self.table[val]
                          for key, val in self.namespace.items()}
        return structures.Snapshot(obj_table=self.table, names=self.namespace)

def post_order_visit(node, visit=lambda x: x, skip=lambda x: []):
    # traverse the dictionary.  post-order traversal
    if isinstance(node, dict):
        keys_to_skip = tuple(skip(node))
        return visit({key: (val if key in keys_to_skip
                            else post_order_visit(val, visit=visit, skip=skip))
                      for key, val in node.items()})
    elif isinstance(node, list):
        return visit([post_order_visit(elt, visit=visit, skip=skip) for elt in node])
    else:
        # node is a str, int, float
        return visit(node)

# keys_to_skip = frozenset((
#     Tokens.STRING,  # the value of a 

# def should_skip_json_node(parent_key, key):
#     if parent_key == Tokens.STRING and :
#         #  on our first pass, we should ignore

def json_keys_to_skip(json_node):
    # Some nodes shouldn't be visited during our post_order_visit
    if not isinstance(json_node, dict):
        pass
    else:
        # METADATA holds extra information like the direction of an edge in a
        # binary tree
        yield Tokens.TYPE
        yield Tokens.UID
        yield Tokens.METADATA
        yield Tokens.VARNAME
        if json_node.get(Tokens.TYPE) == Tokens.STRING:
            yield Tokens.DATA  # don't turn a string literal into a label

def decode_json(text):
    raw_stuff = parse(text)
    validate(raw_stuff)
    # If no exception has been raised, then we have a list of snapshots in chronological order.
    snapshots = []
    for raw_snapshot in raw_stuff:
        # sd = SnapshotDecoder()
        # for raw_obj in raw_snapshot:
        #     post_order_visit(raw_obj,
        #                      visit=sd.obj_hook,
        #                      skip=json_keys_to_skip)
        snapshots.append(decode_snapshot(*raw_snapshot))
    return snapshots

def decode_snapshot(*objects):
    sd = SnapshotDecoder()
    for raw_obj in objects:
        post_order_visit(raw_obj,
                         visit=sd.obj_hook,
                         skip=json_keys_to_skip)
    return sd.finalize()

def validate(json_stuff):
    # We will want to check stuff here, but obviously we don't yet.
    # TODO open an issue for this.
    # This is just for example:
    if isinstance(json_stuff, dict):
        if json_stuff.get(Tokens.TYPE) == Tokens.NULL:
            validate_null(json_stuff)

def parse(text):
    return json.loads(text, object_hook=fix_aliases)

def fix_aliases(obj):
    if isinstance(obj, dict):
        for token in aliases:
            if token in obj:
                if aliases[token] in obj:
                    # This check should happen during validation instead
                    raise JSONObjectError(
                        "{} and {} mean the same thing and shouldn't both be"
                        " specified in the block with {} = {}".format(
                            token, aliases[token], Tokens.UID,
                            obj.get(Tokens.UID, "???")))
                else:
                    obj[aliases[token]] = obj[token]
                    del obj[token]
    return obj

class ValidationError(JSONObjectError):
    pass

def validate_null(obj):
    if Tokens.UID in obj:
        raise ValidationError("objects of type {} should have no {} field.  Has: {}"
                              .format(obj[Tokens.TYPE], Tokens.UID, obj[Tokens.UID]))
