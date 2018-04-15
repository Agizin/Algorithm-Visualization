import collections
import enum
import math

from . import elements, anchors
from .anchors import Anchor, Coord

from algviz.parser import structures

class LayoutOperationError(Exception):
    pass

class AbstractLayout(object):

    def __init__(self, svg_hint=None, choose_child_cls=None, ptr_targets=None):
        self.svg_hint = svg_hint
        self._choose_child_cls = choose_child_cls
        self._placements = {}  # {placement: coordinate}
        self._children = {}  # Like placements, but for sub-pictures instead of primitives
        self._decorations = []  # these have no coordinates
        # ptr_targets is a map from DataStructure instances to the
        # PictureElement instances that have been placed to represent them.
        self._ptr_targets = {} if ptr_targets is None else ptr_targets
        self._finalized = False

    def finalize(self, width, height, ref_point=Coord(0, 0), ref_anchor=Anchor.top_left):
        self.width = width
        self.height = height
        self.top_left = anchors.top_left_corner(self, ref_point, ref_anchor)
        for child, coord in self._children.items():
            if coord[0] < self.top_left[0] or coord[1] < self.top_left[1]:
                raise Exception("child {} (at {}) is out of bounds in {} (at {})"
                                .format(child, coord, self, self.top_left))
        self._scale = 1
        self._element_scale = 1
        self._finalized = True

    def objects_in_layout(self):
        return self._ptr_targets.keys()

    def is_in_layout(self, obj):
        return obj in self._ptr_targets

    def make_child(self, obj, layout_cls=None, **subclass_kwargs):
        if layout_cls is None:
            layout_cls = self._choose_child_cls(obj)  # choose a picture class
        return layout_cls(obj, svg_hint=self.svg_hint,
                          choose_child_cls=self._choose_child_cls,
                          ptr_targets=self._ptr_targets,
                          **subclass_kwargs)

    def add_rect_element(self, rect_element, coord, anchor=Anchor.top_left, represents=None):
        """anchor must be a member of the `Anchor` enum"""
        assert isinstance(rect_element, elements.RectangularElement)
        if represents is not None:
            # assert isinstance(represents, structures.DataStructure)
            if represents in self._ptr_targets and should_draw_only_once(represents):
                warnings.warn("Object {} is duplicated in layout {}"
                              .format(obj.uid, self))
            self._ptr_targets[represents] = rect_element

        self._placements[rect_element] = anchors.top_left_corner(
            rect_element, coord, anchor)

    def scale(self, factor):
        if not self._finalized:
            raise LayoutOperationError(
                "Cannot scale {} until it is finalized (which should happen"
                " at the end of its __init__".format(self))
        self.width *= factor
        self.height *= factor
        self.top_left = Coord(*(factor * c for c in self.top_left))
        self._scale *= factor
        self._element_scale *= factor

    def add_child(self, child, coord, anchor=Anchor.top_left):
        # The x and y are the location in our coordinate system corresponding
        # to the origin in the child's coordinate system
        assert isinstance(child, AbstractLayout)
        self._check_can_add(child)
        # We store the location (in our coordinates) of the child's origin (0, 0).
        corner = anchors.top_left_corner(child, coord, anchor=anchor)
        origin = Coord(corner[0] - child.top_left[0],
                       corner[1] - child.top_left[1])
        self._children[child] = origin

    def add_decoration(self, decoration):
        assert isinstance(decoration, elements.Decoration)
        self._decorations.append(decoration)

    def _check_can_add(self, thing):
        if self._finalized:
            raise LayoutOperationError(
                "Cannot add {} to {} after calling finalize()"
                .format(thing, self))

    def elements(self):
        """Yield all the elements so the caller can draw them"""
        for thing in self._iter_and_scale_elements():
            if isinstance(thing, tuple):
                coord, _ = thing
                if coord[0] < self.top_left[0] or coord[1] < self.top_left[1]:
                    raise Exception("Element {} ({}) of layout {} ({}) is out-of-bounds"
                                    .format(thing[1], coord, self, self.top_left))
            yield thing

    def _iter_and_scale_elements(self):
        # This could be more efficient if we need it to be.
        # It's important that we do a pre-order traversal.
        def scale_coord(coord):
            return Coord(self._scale * coord.x, self._scale * coord.y)
        for element, coord in self._placements.items():
            # if isinstance(element, AbstractLayout):
            #     children.append((coord, element))
            # else:
            yield (scale_coord(coord), element)
        for element in self._decorations:
            yield element
        for child, origin in self._children.items():
            # origin = scale_coord(origin)
            for elem in child.elements():
                if isinstance(elem, elements.Decoration):
                    elem.scale(self._scale)
                    yield elem
                else:
                    # translate to our coordinate system, and then scale it
                    coord, element = elem
                    element.scale(self._element_scale)
                    yield (scale_coord(Coord(origin.x + coord.x, origin.y + coord.y)), element)
        self._element_scale = 1  # we scaled the elements in place, so don't repeat it

    def pointer_requirements(self):
        for child in self._children:
            yield from child.pointer_requirements()

class TerminalLayout(AbstractLayout):
    # A picture that just has one element and no children
    def __init__(self, obj, **kwargs):
        super().__init__(**kwargs)
        self.element = self.make_element(obj)
        self.add_rect_element(self.element, Coord(0, 0), represents=obj)
        self.finalize(self.element.width, self.element.height)

    def make_element(self, obj):
        raise NotImplementedError("Implement this in each subclass")

class PointerRequirement:
    # TODO -- Could be replaced by a namedtuple
    def __init__(self, ptr_element, ptr_obj, notify_owner):
        self.ptr_element = ptr_element
        self.ptr_obj = ptr_obj
        self._notify_owner = notify_owner

    def satisfy(self):
        self._notify_owner()

class PointerLayout(TerminalLayout):
    def make_element(self, ptr):
        width, height = self.svg_hint.pointer_size
        return elements.PointerSource(width, height)

    def __init__(self, ptr, **kwargs):
        super().__init__(ptr, **kwargs)
        def notify_ptr_is_connected_to_object():
            self._requirement = None
        self._requirement = PointerRequirement(self.element, ptr,
                                               notify_ptr_is_connected_to_object)

    def pointer_requirements(self):
        if self._requirement is not None:
            yield self._requirement
        yield from super().pointer_requirements()

class NullLayout(TerminalLayout):
    def make_element(self, null):
        width, height = self.svg_hint.null_size
        return elements.NullElement(width, height)

class StringLayout(TerminalLayout):
    def make_element(self, text):
        width, height = self.svg_hint.string_size(text)
        return elements.StringElement(width, height, text)

class StringReprLayout(StringLayout):
    def make_element(self, text):
        return super().make_element(repr(text))

class NodeLayout(AbstractLayout):
    def __init__(self, node, **kwargs):
        super().__init__(**kwargs)
        child = self.make_child(node.data)
        margin = self.svg_hint.margin
        self.add_child(child, Coord(margin, margin))
        width = 2 * margin + child.width
        height = 2 * margin + child.height
        self.node_element = elements.NodeElement(width, height)  # for public access
        self.add_rect_element(self.node_element, Coord(0, 0), anchor=Anchor.top_left,
                              represents=node)
        self.finalize(width, height)

class SimpleTreeLayout(AbstractLayout):

    def __init__(self, root, parent=None, **kwargs):
        super().__init__(**kwargs)
        if root == structures.Null:
            if parent is None:
                raise LayoutOperationError("SimpleTreeLayout fails if root of tree is Null")
            self.root_picture = None
            self.finalize(parent.root_picture.width,
                          parent.root_picture.height)
            return
        self.root_picture = self.make_child(root, layout_cls=NodeLayout)
        if root.is_leaf():
            self.add_child(self.root_picture, Coord(0, 0))
            self.finalize(self.root_picture.width,
                          self.root_picture.height)
            return
        else:
            child_pictures = [self.make_child(child, parent=self,
                                              layout_cls=SimpleTreeLayout)
                              for child in root.children]
            horiz_margin = self.svg_hint.margin  # horizontal space between children
            children_width = (sum(child.width for child in child_pictures)
                              + horiz_margin * (len(child_pictures) - 1))
            width = max(self.root_picture.width, children_width)
            self.add_child(self.root_picture, Coord(width / 2, 0), anchor=Anchor.top)
            next_child_x = (width - children_width) / 2
            child_y = self.root_picture.height + 3 * self.svg_hint.margin
            for child in child_pictures:
                self.add_child(child, Coord(next_child_x, child_y), anchor=Anchor.top_left)
                if child.root_picture is not None:
                    self.add_decoration(elements.StraightArrow(
                        self.root_picture.node_element,
                        child.root_picture.node_element,
                        orig_anchor=anchors.Anchor.bottom,
                        dest_anchor=anchors.Anchor.top,
                    ))
                next_child_x += child.width + horiz_margin
            height = child_y + max(child.height for child in child_pictures)
            self.finalize(width=width, height=height)

class StupidArrayLayout(AbstractLayout):
    def __init__(self, array, **kwargs):
        super().__init__(**kwargs)
        if array:
            self.data_pic = self.make_child(array[0])
        else:
            self.data_pic = self.make_child("")  # TODO fix this base case or don't use recursion
        width = self.data_pic.width
        height = self.data_pic.height
        if len(array) > 1:
            self.tail_pic = StupidArrayLayout(array[1:], **kwargs)
            width += self.svg_hint.margin
            height = max(height, self.data_pic.height)
            self.add_child(self.tail_pic, Coord(width, height / 2), anchor=Anchor.left)
            width += self.tail_pic.width
        self.add_child(self.data_pic, Coord(0, height / 2), anchor=Anchor.left)
        self.finalize(width, height, Coord(0, 0))

class CompositeLayout(AbstractLayout):

    def __init__(self, *sub_layouts, **kwargs):
        # TODO -- do the layout with pygraphviz
        # For now:  First we put all these pictures next to each other
        super().__init__(**kwargs)
        if len(sub_layouts) is 0:
            raise TypeError("{} requires at least one sub-picture".format(type(self)))
        self._ptr_targets = collections.ChainMap(self._ptr_targets)
        next_child_x = 0
        for child in sub_layouts:
            self.add_child(child, Coord(next_child_x, 0), anchor=Anchor.top_left)
            next_child_x += child.width + self.svg_hint.margin
            self._ptr_targets.maps.append(child._ptr_targets)
        for child in sub_layouts:
            for ptr_req in child.pointer_requirements():
                referent = ptr_req.ptr_obj.referent
                if referent in self._ptr_targets:
                    self.add_decoration(
                        elements.SplineArrow(ptr_req.ptr_element,
                                             self._ptr_targets[referent]))
                    ptr_req.satisfy()
        self.finalize(width=next_child_x - self.svg_hint.margin,
                      height=max(child.height for child in self._children))
        assert self.top_left[0] == 0

class CircularGraphLayout(AbstractLayout):
    def __init__(self, graph, **kwargs):
        super().__init__(**kwargs)
        self.node_layouts = [self.make_child(node) for node in graph.nodes]
        if not self.node_layouts:
            self.finalize(width=self.svg_hint.margin, height=self.svg_hint.margin)
            return
        node_radius = max(node.width**2 + node.height**2
                          for node in self.node_layouts) ** 0.5
        # This circumference approximation is better when there are many nodes:
        circumference = (node_radius * 2 + self.svg_hint.margin) * len(self.node_layouts)
        radius = circumference / (2 * math.pi)  # distance to centers of nodes
        for counter, node_layout in enumerate(self.node_layouts):
            angle = 2 * math.pi / len(self.node_layouts) * counter
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.add_child(node_layout, Coord(x, y), anchor=Anchor.center)
        if graph.edges:
            to_elt = {node: layout.node_element
                      for node, layout in zip(graph.nodes, self.node_layouts)}
            for edge in graph.edges:
                src, dst = edge.orig, edge.dest
                self.add_decoration(elements.StraightArrow(to_elt[src], to_elt[dst]))
        total_diameter = 2 * (radius + node_radius)
        self.finalize(width=total_diameter, height=total_diameter,
                      ref_point=Coord(0, 0), ref_anchor=Anchor.center)

def should_draw_only_once(obj):
    return not isinstance(obj, (float, int)) and obj.metadata.get("draw_once", True)

def add_to_disjoint_layouts(layouts, new_layout, may_be_redundant=True):
    def contained_in(layout0, layout1):
        return layout0.objects_in_layout() <= layout1.objects_in_layout()

    if (may_be_redundant and any(
            contained_in(new_layout, old_layout) for old_layout in layouts)):
        return layouts
    layouts = [lyt for lyt in layouts if not contained_in(lyt, new_layout)]
    layouts.append(new_layout)
    return layouts

# There's a case I missed, which is where A and B both contain C.  But there's
# not a huge amount we can about that, since it just means the model is wrong.

def make_unlinked_layout(obj, choose_layout, svg_hint):
    return choose_layout(obj)(obj, svg_hint=svg_hint,
                              choose_child_cls=choose_layout)

def create_layout(obj, choose_layout, svg_hint):
    def mk_layout(thing):
        return make_unlinked_layout(thing, choose_layout, svg_hint)
    layouts = []
    objects_drawn = set()
    objects_needed = set([obj])
    while objects_needed:
        nxt_obj = objects_needed.pop()
        if nxt_obj in objects_drawn:
            continue
        new_layout =  mk_layout(nxt_obj)
        layouts = add_to_disjoint_layouts(layouts, new_layout,
                                          may_be_redundant=False)
        objects_drawn.update(new_layout.objects_in_layout())
        objects_needed.update(req.ptr_obj.referent
                              for req in new_layout.pointer_requirements())
    return CompositeLayout(*layouts, choose_child_cls=choose_layout, svg_hint=svg_hint)
