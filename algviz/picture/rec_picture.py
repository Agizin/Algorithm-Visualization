from collections import namedtuple
import enum

from . import elements
from .elements import Anchor, Coord

class PictureOperationError(Exception):
    pass

class AbstractPicture(object):

    def __init__(self, engine=None, make_child=None, parent=None):
        self.engine = engine
        self.parent = parent
        self._make_child = make_child  # TODO make a method that calls this with arguments to draw a sub-picture
        self._placements = {}  # {placement: coordinate}
        self._children = {}  # Like placements, but for sub-pictures instead of primitives
        self._decorations = []  # these have no coordinates
        # TODO maybe have a finalize method that gets called at the end of the constructor
        # Raise error if self.elements() is called before `self.finalize`.
        self._finalized = False

    def finalize(self, width, height, top_left=Coord(0, 0)):
        self.width = width
        self.height = height
        self.top_left = top_left
        self._scale = 1
        self._finalized = True

    def make_child(self, obj):
        cls = self._make_child(obj)  # choose a picture class
        return cls(obj, engine=self.engine, make_child=self._make_child, parent=self)

    def is_root(self):
        return self.parent is None

    def add_rect_element(self, rect_element, coord, anchor=Anchor.top_left):
        """anchor must be a member of the `Anchor` enum"""
        assert isinstance(rect_element, elements.RectangularElement)
        self._placements[rect_element] = elements.top_left_corner(
            rect_element, coord, anchor)

    def scale(self, factor):
        if not self._finalized:
            raise PictureOperationError(
                "Cannot scale {} until it is finalized (which should happen"
                " at the end of its __init__".format(self))
        self.width *= factor
        self.height *= factor
        self.top_left = Coord(*(factor * c for c in self.top_left))
        self._scale *= factor

    def add_child(self, child, coord, anchor=Anchor.top_left):
        # The x and y are the location in our coordinate system corresponding
        # to the origin in the child's coordinate system
        assert isinstance(child, AbstractPicture)
        # We store the location (in our coordinates) of the child's origin (0, 0).
        corner = elements.top_left_corner(child, coord, anchor=anchor)
        origin = Coord(corner[0] - child.top_left[0],
                       corner[1] - child.top_left[1])
        self._children[child] = origin

    def add_decoration(self, decoration):
        assert isinstance(decoration, elements.Decoration)
        self._decorations.append(decoration)

    def elements(self):
        # This could be more efficient if we need it to be.
        # It's important that we do a pre-order traversal.
        def scale_coord(coord):
            return Coord(self._scale * coord.x, self._scale * coord.y)
        for element, coord in self._placements.items():
            # if isinstance(element, AbstractPicture):
            #     children.append((coord, element))
            # else:
            yield (scale_coord(coord), element)
        for element in self._decorations:
            yield element
        for child, origin in self._children.items():
            # origin = scale_coord(origin)
            for elem in child.elements():
                if isinstance(elem, elements.Decoration):
                    yield elem
                else:
                    # translate to our coordinate system, and then scale it
                    coord, element = elem
                    # TODO have a scale method on RectangularElements
                    element.width *= self._scale
                    element.height *= self._scale
                    # coord = scale_coord(coord)
                    yield (scale_coord(Coord(origin.x + coord.x, origin.y + coord.y)), element)

class TerminalPicture(AbstractPicture):
    # A picture that just has one element and no children
    def __init__(self, obj, **kwargs):
        super().__init__(**kwargs)
        self.element = self.make_element(obj)
        self.add_rect_element(self.element, Coord(0, 0))
        self.finalize(self.element.width, self.element.height)

    def make_element(self, obj):
        raise NotImplementedError("Implement this in each subclass")

class StringPicture(TerminalPicture):
    def make_element(self, text):
        return elements.StringElement(text, engine=self.engine)

class StringReprPicture(TerminalPicture):
    def make_element(self, text):
        return elements.StringElement(repr(text), engine=self.engine)

class NodePicture(AbstractPicture):
    def __init__(self, node, **kwargs):
        super().__init__(**kwargs)
        child = self.make_child(node.data)
        margin = self.engine.margin
        self.add_child(child, Coord(margin, margin))
        width = 2 * margin + child.width
        height = 2 * margin + child.height
        self.node_element = elements.NodeElement(width, height)  # for public access
        self.add_rect_element(self.node_element, Coord(0, 0), anchor=Anchor.top_left)
        self.finalize(width, height, top_left=Coord(0, 0))

class SimpleTreePicture(AbstractPicture):

    def __init__(self, root, **kwargs):
        super().__init__(**kwargs)
        self.root_picture = NodePicture(root, **kwargs)
        if root.is_leaf():
            self.add_child(self.root_picture, Coord(0, 0))
            self.finalize(self.root_picture.width,
                          self.root_picture.height)
        else:
            child_pictures = [SimpleTreePicture(child, **kwargs) for child in root.children]
            # for child in child_pictures:
            #     child.scale(1)  # hehe
            horiz_margin = self.engine.margin  # horizontal space between children
            children_width = (sum(child.width for child in child_pictures)
                              + horiz_margin * (len(child_pictures) - 1))
            width = max(self.root_picture.width, children_width)
            self.add_child(self.root_picture, Coord(width / 2, 0), anchor=Anchor.top)
            next_child_x = (width - children_width) / 2
            child_y = self.root_picture.height + 3 * self.engine.margin
            for child in child_pictures:
                self.add_child(child, Coord(next_child_x, child_y), anchor=Anchor.top_left)
                self.add_decoration(elements.StraightArrow(
                    self.root_picture.node_element,
                    child.root_picture.node_element))
                next_child_x += child.width + horiz_margin
            height = child_y + max(child.height for child in child_pictures)
            self.finalize(width=width, height=height)


class StupidArrayPicture(AbstractPicture):
    def __init__(self, array, **kwargs):
        super().__init__(**kwargs)
        self.data_pic = self.make_child(array[0])
        width = self.data_pic.width
        height = self.data_pic.height
        if len(array) > 1:
            self.tail_pic = StupidArrayPicture(array[1:], **kwargs)
            width += self.engine.margin
            height = max(height, self.data_pic.height)
            self.add_child(self.tail_pic, Coord(width, height / 2), anchor=Anchor.left)
            width += self.tail_pic.width
        self.add_child(self.data_pic, Coord(0, height / 2), anchor=Anchor.left)
        self.finalize(width, height, Coord(0, 0))
