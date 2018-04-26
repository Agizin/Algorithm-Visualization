from collections import namedtuple
import enum

# TODO
# This same framework can be used for much more.
# Notice that Anchor.top, Anchor.bottom, Anchor.right, and Anchor.left
# all lie on the unit circle.
# This is basically a transformation (and translation) of the rectangle to a
# coordinate system where its width and height are normalized, and where it's
# centered at 0.
# So if we have an ellipse with a width and height, any pair (cos(t), sin(t))
# is a valid anchor that corresponds to a point on the boundary of the ellipse.

# Maybe call the enum Grid and have Anchor be a namedtuple or similar.

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

PseudoAnchor = namedtuple("PseudoAnchor", ("x", "y"))

def top_left_corner(rectangle, coord, anchor):
    if not isinstance(anchor, (Anchor, PseudoAnchor)):
        # (Members of an Enum are also instances of that Enum.)
        raise TypeError("{} is not an anchor.  Use an element of {}".format(anchor, Anchor))
    def fix_one_dimension(given, anchor_val, side_length):
        return given + side_length / (_HIGH - _LOW) * (_LOW - anchor_val)

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
