from . import rec_layout
from algviz.parser import structures

def map_metadata_key_to_layout_subclass(config):
    # TODO - interpret user config here
    return {}

_default_mapping = {
    structures.Tree: rec_layout.SimpleTreeLayout,
    structures.String: rec_layout.StringLayout,
    int: rec_layout.StringReprLayout,
    float: rec_layout.StringReprLayout,
    str: rec_layout.StringLayout,
    structures.Array: rec_layout.SimpleArrayLayout,
    structures.Graph: rec_layout.CircularGraphLayout,
    structures.Node: rec_layout.NodeLayout,
    structures.NullType: rec_layout.NullLayout,
    structures.Pointer: rec_layout.PointerLayout,
}

def add_defaults(mapping):
    for key, default in _default_mapping.items():
        mapping.setdefault(key, default)

def make_layout_chooser(config):
    mapping = map_metadata_key_to_layout_subclass(config)
    add_defaults(mapping)
    def choose_layout(obj):
        # TODO - consider metadata
        return mapping[type(obj)]
    return choose_layout
