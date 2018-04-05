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
    snapshots = json_objects.read(args.infile)
    config = {"module": "recursive"}
    if args.var is not None:
        config[pic_main._keys.var] = args.var
    else:
        config[pic_main._keys.uid] = args.uid
    config[pic_main._keys.snapshot] = "0"
    print(pic_main.make_svg(snapshots, config), file=args.outfile, end="")

if __name__ == "__main__":
    main()
