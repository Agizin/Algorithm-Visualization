import sys

from algviz.parser import json_objects
from algviz.picture.fabulous import picture

def make_picture_from_json(json_file, object_uid, outfile):
    json_contents = None
    with open(json_file,'r') as f:
        json_contents = f.read()
    assert(json_contents is not None)
    print(json_contents)
    snapshot = json_objects.decode_json(json_contents)[0] #assumes only given single snapshot
    try:
         structure = snapshot.obj_table.getuid(object_uid)
    except KeyError:
         raise KeyError("uid '{}' not found in structure or structure json not properly formatted".format(object_uid))
    pic = picture.Picture.make_picture(structure)
    pic.draw()
    pic.save(outfile)

if __name__ == "__main__":
    json_file = sys.argv[1]
    uid = sys.argv[2]
    if len(sys.argv) > 3:
        outfile = sys.argv[3]
    else:
        outfile = "picture.svg"
    make_picture_from_json(json_file,uid,outfile)
