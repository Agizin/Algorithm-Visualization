import argparse

from algviz.parser import json_objects
from algviz.picture.picture import Picture

def main():
    """Run this script with --help for documenation"""
    parser = argparse.ArgumentParser(
        "Read data structure in algviz JSON format and write SVG")
    parser.add_argument("infile", type=argparse.FileType("r"),
                        help="input file.  - for stdin")
    parser.add_argument("outfile", type=argparse.FileType("wb"),
                        help="output file (to be overwritten).  - for stdout")
    # parser.add_argument("--prog", "-p", type=str, default="neato", choices=[
    #     'neato', 'dot', 'twopi', 'circo', 'fdp', 'sfdp'],
    #                     help="A GraphViz graph-drawing algorithm to use")
    parser.add_argument("--uid", "-u", type=str, default=None,
                        help=("uid of graph to be drawn, if there is more than"
                              " one graph in the snapshot."))
    parser.add_argument("--var", "-r", default=None, type=str,
                        help="var name of object to be drawn.  Takes "
                        "precedence over UID.")
    args = parser.parse_args()
    # Even though we asked for args.infile to be opened in binary mode, stdin
    # will be opened in text mode...
    if 'b' in args.outfile.mode:
        outfile = args.outfile
    else:
        # ... So we use the use the underlying buffer to write binary data to stdout
        outfile = args.outfile.buffer
    print("Ignoring the outfile argument and writing to banana.svg instead!")
    snapshot = json_objects.read(args.infile)[0]
    if args.var:
        obj = snapshot.names[args.var]
    else:
        obj = snapshot.obj_table.getuid(args.uid)
    pic = Picture.make_picture(obj, filename="banana.svg")
    pic.draw()

if __name__ == "__main__":
    main()
