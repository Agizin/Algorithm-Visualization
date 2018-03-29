import sys

from algviz.parser import json_objects
from algviz.picture import picture

json = sys.argv[1]
if len(ays.argv) > 2:
    outfile = sys.argv[2]
else:
    outfile = "picture.svg"
    
structure = json_objects.decode_json(text)[0] #assumes only given single snapshot
pic = picture.Picture.make_picture(structure, filename=outfile)
pic.draw()
