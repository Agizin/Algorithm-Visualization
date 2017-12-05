import json
from . import structures

class Tokens:
    """Tokens we expect to see in the JSON"""
    # First, keys we expect to see.
    UID = "uid"
    TYPE = "type"
    FROM = "from"
    TO = "to"
    CHILDREN = "children"  # children of a tree node
    DATA = "data"
    GRAPH_NODES = "nodes"  # not a type, but an attribute of a graph
    GRAPH_EDGES = "edges"
    VARNAME = "var"
    METADATA = "metadata"  # we probably should only use this for prototyping
    # Possible values for TYPE.  Keep these alphabetized and give them all the
    # _T suffix, please.
    ARRAY_T = "array"
    TREE_NODE_T = "treenode"
    EDGE_T = "edge"
    GRAPH_T = "graph"
    NODE_T = "node"
    NULL_T = "null"
    POINTER_T = "ptr"
    STRING_T = "string"
    WIDGET_T = "widget"

aliases = {
    # Shorter forms of tokens, to make it easier to handwrite these descriptions
    "T": Tokens.TYPE,
}

_type_tokens = tuple(getattr(Tokens, name) for name in dir(Tokens)
                     if name.endswith("_T") and not name.startswith("_"))
_key_tokens = tuple(getattr(Tokens, name) for name in dir(Tokens)
                    if not name.startswith("_") and not name.endswith("_T"))

class JSONObjectError(Exception):
    pass

class Dispatcher(type):
    @staticmethod
    def dispatch(key):
        """Decorate a method of class `X`, where the metaclass of X must be Dispatcher.

        `X.dispatch(key)` will return the decorated method.
        """
        def _decorate(f):
            f._purpose = key
            return f
        return _decorate

    def __init__(cls, name, bases, namespace):
        """Muck about with the class under construction to give it the desired
        `dispatch` function.
        """
        cls._dispatcher = {}
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
    """Decodes a list of json objects and eventually produces a snapshot with
    the `finalize` method.
    """
    def __init__(self):
        self.table = structures.ObjectTable()
        self.namespace = {}
        self._next_auto_uid = 0

    def _auto_uid(self, type_=None):
        # Produce a suitable UID if the user didn't specify one.
        if type_ == Tokens.NULL_T:
            return structures.Null.uid
        else:
            # Guaranteed unique because user-supplied tokens may not contain "#"
            result = "#{}".format(self._next_auto_uid)
            self._next_auto_uid += 1
            return result

    def obj_hook(self, obj):
        if isinstance(obj, str):
            return structures.ObjectTableReference(uid=obj)
        elif isinstance(obj, (list, float, int)):
            # note that we may return a structures.Array if obj is a dict with "type": "array"
            return obj
        elif not isinstance(obj, dict):
            raise TypeError("Expected a dict but got {!r}".format(obj))
        # call the appropriate method for the type of the thing
        ref = structures.ObjectTableReference(
            obj.get(Tokens.UID, self._auto_uid(type_=obj.get(Tokens.TYPE))))
        # assert isinstance(obj[Tokens.TYPE], str), obj  # Should happen during validation
        self.table[ref] = self._dispatch(obj[Tokens.TYPE])(
            obj, uid=ref.uid, metadata=obj.get(Tokens.METADATA))
        if Tokens.VARNAME in obj:
            self.namespace[obj[Tokens.VARNAME]] = ref
        return self.table[ref]

    @Dispatcher.dispatch(Tokens.ARRAY_T)
    def array_hook(self, array, **kwargs):
        return structures.Array(array[Tokens.DATA], **kwargs)

    @Dispatcher.dispatch(Tokens.TREE_NODE_T)
    def tree_node_hook(self, tree_node, **kwargs):
        return structures.TreeNode(data=tree_node.get(Tokens.DATA, structures.Null),
                                   children=tree_node.get(Tokens.CHILDREN),
                                   **kwargs)

    @Dispatcher.dispatch(Tokens.EDGE_T)
    def edge_hook(self, edge, **kwargs):
        return structures.Edge(edge[Tokens.FROM], edge[Tokens.TO],
                               data=edge.get(Tokens.DATA, structures.Null),
                               **kwargs)

    @Dispatcher.dispatch(Tokens.GRAPH_T)
    def graph_hook(self, graph, **kwargs):
        return structures.Graph(graph[Tokens.GRAPH_NODES],
                                graph[Tokens.GRAPH_EDGES], **kwargs)

    @Dispatcher.dispatch(Tokens.NODE_T)
    def node_hook(self, node, **kwargs):
        return structures.Node(node.get(Tokens.DATA, structures.Null),
                               **kwargs)

    @Dispatcher.dispatch(Tokens.NULL_T)
    def null_hook(self, null, **kwargs):
        return structures.Null

    @Dispatcher.dispatch(Tokens.POINTER_T)
    def pointer_hook(self, ptr, **kwargs):
        return structures.Pointer(ptr[Tokens.DATA], **kwargs)

    @Dispatcher.dispatch(Tokens.STRING_T)
    def string_hook(self, string, **kwargs):
        return structures.String(string[Tokens.DATA], **kwargs)

    @Dispatcher.dispatch(Tokens.WIDGET_T)
    def widget_hook(self, widget, **kwargs):
        return structures.Widget(**kwargs)

    def finalize(self):
        self.table.finalize()
        self.namespace = {key: self.table[val]
                          for key, val in self.namespace.items()}
        return structures.Snapshot(obj_table=self.table, names=self.namespace)

def post_order_visit(node, visit=lambda x: x, skip=lambda x: ()):
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

def json_keys_to_skip(json_node):
    # Some nodes shouldn't be visited during our post_order_visit
    if not isinstance(json_node, dict):
        pass
    else:
        # These string values shouldn't be turned into ObjectTableReferences
        yield Tokens.TYPE
        yield Tokens.VARNAME
        yield Tokens.UID
        yield Tokens.METADATA
        if json_node.get(Tokens.TYPE) == Tokens.STRING_T:
            yield Tokens.DATA  # don't turn a string literal into a label

def decode_json(text):
    raw_stuff = parse(text)
    validate(raw_stuff)
    # If no exception has been raised, then we have a list of snapshots in chronological order.
    snapshots = []
    for raw_snapshot in raw_stuff:
        snapshots.append(decode_snapshot(*raw_snapshot))
    return snapshots

def decode_snapshot_text(text):
    raw_snapshot = parse(text)
    validate_snapshot(raw_snapshot)
    return decode_snapshot(*raw_snapshot)

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
        if json_stuff.get(Tokens.TYPE) == Tokens.NULL_T:
            validate_null(json_stuff)

def validate_snapshot(snapshot):
    pass  # TODO

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
