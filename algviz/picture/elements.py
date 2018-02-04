# The elements that pictures can have

# These picture elements don't hold information about their own location, since
# they'll be passed around by objects with different internal coordinate
# systems.

from collections import namedtuple
import enum

_LOW = -1
_MID = 0
_HIGH = 1

@enum.unique
class Anchor(enum.Enum):
    top_left = (_LOW, _LOW)
    top = (_MID, _LOW)
    top_right = (_HIGH, _LOW)
    left = (_LOW, _MID)
    center = (_MID, _MID)
    right = (_HIGH, _MID)
    bottom_left = (_LOW, _HIGH)
    bottom = (_MID, _HIGH)
    bottom_right = (_HIGH, _HIGH)

Coord = namedtuple("Coord", ("x", "y"))

def top_left_corner(rectangle, coord, anchor):
    if not isinstance(anchor, Anchor):
        # (Members of an Enum are also instances of that Enum.)
        raise TypeError("{} is not an anchor.  Use an element of {}".format(anchor, Anchor))
    def fix_one_dimension(given, anchor_val, side_length):
        if anchor_val is _LOW:
            return given
        elif anchor_val is _HIGH:
            return given - side_length
        else:
            return given - side_length / 2

    x, y = coord
    x_anch, y_anch = anchor.value
    return Coord(fix_one_dimension(x, x_anch, rectangle.width),
                 fix_one_dimension(y, y_anch, rectangle.height))


def from_top_left_corner(rect, tlc, anchor):
    class Namespace:
        pass
    new_rect = Namespace()
    new_rect.width = - rect.width
    new_rect.height = - rect.height
    return top_left_corner(new_rect, tlc, anchor)

def anchor_translate(rect, coord, from_anch, to_anch):
    return from_top_left_corner(rect,
                                top_left_corner(rect, coord, from_anch),
                                to_anch)

class PictureElement(object):
    # These are all things that will be laid out inside pictures so that they can be drawn.
    pass

class RectangularElement(PictureElement):
    """Any element that takes up space.  For now, it gets a width and a height."""
    def __init__(self, width, height, **kwargs):
        self.width = width
        self.height = height

    def place(self, point):
        self.location = point

class NodeElement(RectangularElement):
    """A node, which fits into a bounding box"""
    # def __init__(self, width, height, **kwargs):
    #     self.width = width
    #     self.height = height
    #     super().__init__(**kwargs)

class PointerSource(RectangularElement):
    """The start of a pointer, usually a big dot."""
    def __init__(self, **kwargs):
        width, height = kwargs["engine"].pointer_size
        super().__init__(width, height, **kwargs)

class StringElement(RectangularElement):
    """A string, geez"""
    def __init__(self, text, engine=None, **kwargs):
        self.text = text
        width, height = engine.string_size(text)
        super().__init__(width, height, engine=engine, **kwargs)

class Decoration(PictureElement):
    """Stuff that gets tacked on but doesn't take up space"""
    pass

class Arrow(Decoration):
    """Gets drawn as an arrow or line of some kind"""
    def __init__(self, origin, destination, **kwargs):
        self.origin = origin
        self.destination = destination
        super().__init__(**kwargs)

class StraightArrow(Arrow):
    pass

class SplineArrow(Arrow):
    pass
