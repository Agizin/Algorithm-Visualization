import argparse
import collections
import contextlib
import math
import svgwrite
import sys

from algviz.parser import json_objects
from algviz.picture import main as pic_main

def main():
    parser = argparse.ArgumentParser("Draw a picture of an object from JSON")
    parser.add_argument("infile", type=argparse.FileType("r"),
                        help="input file.  - for stdin")
    parser.add_argument("outfile", type=argparse.FileType("w"),
                        help="output file (to be overwritten).")
    parser.add_argument("--uid", "-u", type=str, default=None,
                        help="uid of object to be drawn")
    parser.add_argument("--var", "-r", default=None, type=str,
                        help="var name of object to be drawn.  Takes precedence over UID.")
    args = parser.parse_args()
    snapshot = json_objects.decode_snapshot_text(args.infile.read())
    if args.var:
        obj = snapshot.names[args.var]
    else:
        obj = snapshot.obj_table.getuid(args.uid)
    print(pic_main.layout_and_draw(obj), file=args.outfile, end="")

if __name__ == "__main__":
    main()
