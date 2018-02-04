from . import rec_picture
from algviz.parser import structures

def map_metadata_key_to_picture_subclass(config):
    return {}

_default_mapping = {
    structures.TreeNode: rec_picture.SimpleTreePicture,
    structures.String: rec_picture.StringPicture,
    int: rec_picture.StringReprPicture,
    float: rec_picture.StringReprPicture,
    str: rec_picture.StringPicture,
    structures.Array: rec_picture.StupidArrayPicture,
}

def add_defaults(mapping):
    global _default_mapping
    for key, default in _default_mapping.items():
        mapping.setdefault(key, default)

def make_drawing_function(config):
    mapping = map_metadata_key_to_picture_subclass(config)
    add_defaults(mapping)
    def choose_picture(obj):
        return mapping[type(obj)]
    return choose_picture
