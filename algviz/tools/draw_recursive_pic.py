import argparse
import collections
import contextlib
import math
import svgwrite
import sys

from algviz.parser import json_objects
from algviz.picture import elements, pic_dispatch

# This is just sort of a toss-off to see if recursive pictures work at all

class AwfulSVGPlotter:

    def __init__(self, font_px=15):
        self.font_px = 15
        self.margin = 7
        self.things_drawn = {}
        self.pending_arrows = collections.defaultdict(set)
        self.pointer_size = (30, 30)
        self.doc = None

    def string_size(self, text):
        lines = text.split("\n")
        return (max(len(line) for line in lines) * self.font_px / 2,
                len(lines) * self.font_px)
        
    @contextlib.contextmanager
    def make_svg(self, filename):
        if self.doc is not None:
            raise Exception("We're already writing a doc, and I'm just not smart enough for this crap")
        try:
            self.doc = svgwrite.Drawing(filename)
            yield
        finally:
            all_pending_arrows = set()
            for arrow_set in self.pending_arrows.values():
                all_pending_arrows.union(arrow_set)
            for arrow in all_pending_arrows:
                self.draw_arrow(arrow)
            self.doc.save()
            self.pending_arrows.clear()
            self.things_drawn.clear()
            self.doc = None

    def draw_arrow(self, arrow):
        src, dest = arrow.origin, arrow.destination  # nodes
        def distance(pt1, pt2):
            return sum((x - y) ** 2 for x, y in zip(pt1, pt2))
        def iter_connections(rect):
            top_left = self.things_drawn[rect]
            for anch in elements.Anchor:
                yield elements.from_top_left_corner(rect, top_left, anch)
        src_pt, dest_pt = min(((s, d)
                               for s in iter_connections(src)
                               for d in iter_connections(dest)),
                              key=lambda pair: distance(*pair))
        self.doc.add(self.doc.line(src_pt, dest_pt, style="stroke:rgb(50,50,50);stroke-width:2"))
        self.pending_arrows[src].discard(arrow)
        self.pending_arrows[dest].discard(arrow)

    def draw_arrow_soon(self, arrow):
        # Maybe the endpoints for the arrow aren't present yet
        src, dest = arrow.origin, arrow.destination
        if src in self.things_drawn and dest in self.things_drawn:
            self.draw_arrow(arrow)
        else:
            self.pending_arrows[src].add(arrow)
            self.pending_arrows[dest].add(arrow)

    def draw_thing(self, thing, coord=None):
        """actually draw an element in self.doc.  Call this in a self.make_svg block"""
        self.things_drawn[thing] = coord
        if isinstance(thing, elements.StringElement):
            self.doc.add(self.doc.text(thing.text, insert=coord, font_size="{}px".format(self.font_px),
                                       dy=[self.font_px]))
        elif isinstance(thing, elements.NodeElement):
            self.doc.add(self.doc.rect(insert=coord, size=(thing.width, thing.height),
                                       fill_opacity="0.5"))
        elif isinstance(thing, elements.Arrow):
            self.draw_arrow_soon(thing)
        elif isinstance(thing, elements.PointerSource):
            self.doc.add(self.doc.rect(coord, self.pointer_size))
        else:
            raise ValueError("I don't know how to draw {}".format(thing))

        if thing in self.pending_arrows:
            for arrow in set(self.pending_arrows[thing]):
                self.draw_arrow_soon(arrow)


def main():
    parser = argparse.ArgumentParser("Draw a picture of an object from JSON")
    parser.add_argument("infile", type=argparse.FileType("r"),
                        help="input file.  - for stdin")
    parser.add_argument("outfile", type=str,
                        help="output file (to be overwritten).")
    parser.add_argument("--uid", "-u", type=str, default=None,
                        help="uid of object to be drawn")
    parser.add_argument("--var", "-r", default=None, type=str,
                        help="var name of object to be drawn.  Takes precedence over UID.")
    args = parser.parse_args()
    snapshot = json_objects.decode_snapshot_text(args.infile.read())
    choose_pic = pic_dispatch.make_drawing_function(None)
    if args.var:
        obj = snapshot.names[args.var]
    else:
        obj = snapshot.obj_table[args.uid]
    pic_cls = choose_pic(obj)
    engine = AwfulSVGPlotter(font_px=15, )
    pic = pic_cls(obj, engine=engine, make_child=choose_pic)
    with engine.make_svg(args.outfile):
        for elem in pic.elements():
            if isinstance(elem, tuple):
                coord, elem = elem
                coord = tuple(c + 200 for c in coord)
            else:
                coord = None
            engine.draw_thing(elem, coord=coord)

if __name__ == "__main__":
    main()
