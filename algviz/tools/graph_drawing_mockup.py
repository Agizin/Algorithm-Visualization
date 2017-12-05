#!/usr/bin/env python3

"""
This is a toy script that reads a snapshot (with objects in algviz's JSON data
format) and directly uses PyGraphViz to create an SVG image of a graph from the
snapshot.

Run with --help for usage information.
"""

import argparse
import sys
import pygraphviz as pgv

from algviz.parsers import json_objects, structures

def graph_to_pgv(graph):
    """Make a `pygraphviz.AGraph` from the given `algviz.structures.Graph`"""
    G = pgv.AGraph(directed=True)
    # It's a shortcoming of pygraphviz that the nodes must be labeled with
    # their UID and not with their contents, since adding two nodes with the
    # same label is an error.  (I.e., graphviz makes more assumptions about
    # nodes' labels than we do.  It assumes they will be unique identifiers.)
    G.add_nodes_from(node.uid for node in graph.nodes)
    for edge in graph.edges:
        G.add_edge(edge.orig.uid, edge.dest.uid)
    return G

def main():
    """Run this script with --help for documenation"""
    parser = argparse.ArgumentParser(
        "Read from graph in algviz JSON format and write SVG using PyGraphViz")
    parser.add_argument("infile", type=argparse.FileType("r"),
                        help="input file.  - for stdin")
    parser.add_argument("outfile", type=argparse.FileType("wb"),
                        help="output file (to be overwritten).  - for stdout")
    parser.add_argument("--prog", "-p", type=str, default="neato", choices=[
        'neato', 'dot', 'twopi', 'circo', 'fdp', 'sfdp'],
                        help="A GraphViz graph-drawing algorithm to use")
    parser.add_argument("--uid", "-u", type=str, default=None,
                        help=("uid of graph to be drawn, if there is more than"
                              " one graph in the snapshot."))
    parser.add_argument("--var", "-r", default=None, type=str,
                        help="var name of graph.  Takes precedence over UID.")
    args = parser.parse_args()

    # Even though we asked for args.infile to be opened in binary mode, stdin
    # will be opened in text mode...
    if 'b' in args.outfile.mode:
        outfile = args.outfile
    else:
        # ... So we use the use the underlying buffer to write binary data to stdout
        outfile = args.outfile.buffer
        print(outfile, file=sys.stderr)
    # Now we can do the actual decoding and drawing
    snapshot = json_objects.decode_snapshot_text(args.infile.read())
    if args.var:
        graph = snapshot.names[args.var]
    elif args.uid:
        graph = snapshot.obj_table.getuid(args.uid)
    else:
        # Just search for the first graph we find in the snapshot
        graph = None
        for obj in snapshot.obj_table.values():
            if isinstance(obj, structures.Graph):
                graph = obj
                break
        if graph is None:
            raise Exception("No graph found in JSON input")

    gv_graph = graph_to_pgv(graph)
    gv_graph.layout(prog=args.prog)
    gv_graph.draw(path=outfile, format="svg")

if __name__ == "__main__":
    main()
