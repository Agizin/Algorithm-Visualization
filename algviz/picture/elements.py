# The elements that pictures can have

# These picture elements don't hold information about their own location, since
# they'll be passed around by objects with different internal coordinate
# systems.

from . import anchors

from collections import namedtuple
class PictureElement(object):
    # These are all things that will be laid out inside pictures so that they can be drawn.
    pass

class RectangularElement(PictureElement):
    """Any element that takes up space.  For now, it gets a width and a height."""
    def __init__(self, width, height, **kwargs):
        self.width = width
        self.height = height

    def scale(self, factor):
        self.width *= factor
        self.height *= factor

class NodeElement(RectangularElement):
    """A node, which fits into a bounding box"""
    def __init__(self, *args, inner_width=None, inner_height=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inner_width = self.width if inner_width is None else inner_width
        self.inner_height = self.height if inner_height is None else inner_width
        # TODO -- make the NodeLayout figure inner_width and inner_height out for us.
        # Also, eventually, make both rectangles and ovals possible

class PointerSource(RectangularElement):
    """The start of a pointer, usually a big dot."""
    # def __init__(self, width, height, **kwargs):
    #     width, height = kwargs["engine"].pointer_size
    #     super().__init__(width, height, **kwargs)

class NullElement(RectangularElement):
    """A Null value"""

class StringElement(RectangularElement):
    """A string, geez"""
    def __init__(self, width, height, text, **kwargs):
        self.text = text
        super().__init__(width, height, **kwargs)

class Decoration(PictureElement):
    """Stuff that gets tacked on but doesn't take up space"""
    pass

class Arrow(Decoration):
    """Gets drawn as an arrow or line of some kind"""
    def __init__(self, origin, destination, orig_anchor=None, dest_anchor=None, **kwargs):
        self.origin = origin
        self.destination = destination
        self.orig_anchor = orig_anchor
        self.dest_anchor = dest_anchor
        super().__init__(**kwargs)

    def anchor_pairs(self):
        """Iterate through all allowed pairs of anchors
        (origin_anchor, dest_anchor)
        """
        # TODO unit test for this method
        def _anchors(given_anchor):
            if given_anchor is not None:
                yield given_anchor
            else:
                yield from anchors.Anchor
        for src_anch in _anchors(self.orig_anchor):
            for dest_anch in _anchors(self.dest_anchor):
                yield (src_anch, dest_anch)

    def scale(self, factor):
        pass


class StraightArrow(Arrow):
    pass

class SplineArrow(Arrow):
    pass
