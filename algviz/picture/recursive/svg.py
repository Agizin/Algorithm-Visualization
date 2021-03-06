import abc
import collections
import math
import svgwrite

from . import elements, anchors

class StringHint(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def string_size(self, text):
        """Return the (width, height) for this string in the svg"""

class MarginHint(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def margin(self):
        """A standard minimum distance between adjacent elements in a layout"""
        # This is sort of a careless approach, honestly

class ArrayFrameHint(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def array_border_margin(self):
        """Amount of space to leave clear around the border of an array"""

    @property
    @abc.abstractmethod
    def array_cell_sep(self):
        """Amount of space to leave between adjacent cells of an array"""

class PointerHint(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def pointer_source_size(self):
        """The (width, height) of a Pointer"""

class NullHint(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def null_size(self):
        """The (width, height) of Null"""

class SVGHint(
        StringHint,
        MarginHint,
        PointerHint,
        NullHint,
        ArrayFrameHint,
):
    """In order to create a Layout, it's useful to know what size the components of the picture should be."""
    
class DelegatingSVGHint(SVGHint):
    def __init__(self, str_hint, ptr_hint, null_hint, array_frame_hint, margin):
        self.str_hint = str_hint
        self.ptr_hint = ptr_hint
        self._margin = margin
        self.null_hint = null_hint
        self.array_frame_hint = array_frame_hint

    @property
    def margin(self):
        return self._margin

    @property
    def pointer_source_size(self):
        return self.ptr_hint.pointer_source_size

    def string_size(self, text):
        return self.str_hint.string_size(text)

    @property
    def null_size(self):
        return self.null_hint.null_size

    @property
    def array_cell_sep(self):
        return self.array_frame_hint.array_cell_sep

    @property
    def array_border_margin(self):
        return self.array_frame_hint.array_border_margin

class ElementPainter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def draw(self, element, locations, svg_doc):
        """element is an element of the correct type.
        Locations is a map from elements to coordinates (top-left for
        rectangular elements), including the element to be drawn if
        appropriate.
        """

class RectangularElementPainter(ElementPainter):
    def draw(self, element, locations, svg_doc):
        return self.draw_at(element, locations[element], svg_doc)

    @abc.abstractmethod
    def draw_at(self, element, top_left_corner, svg_doc):
        """Draw the given element at the given location in the svg_doc"""

class StringPainter(RectangularElementPainter, StringHint):
    pass

class DefaultStringPainter(StringPainter):
    def __init__(self, font_pixel_size=15):
        self.font_pixel_size = 15
    def string_size(self, text):
        lines = text.split("\n")
        return (max(len(line) for line in lines) * self.font_pixel_size / 2,
                len(lines) * self.font_pixel_size)

    def draw_at(self, string, coord, svg_doc):
        svg_doc.add(svg_doc.text(string.text, insert=coord,
                                 font_size="{}px".format(self.font_pixel_size),
                                 dy=[self.font_pixel_size]))

class NullPainter(RectangularElementPainter, NullHint):
    pass

class ArrayFramePainter(RectangularElementPainter, ArrayFrameHint):
    pass

class BlackBorderArrayFramePainter(ArrayFramePainter):

    def __init__(self, stroke_width=1.5, stroke_color="black"):
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    @property
    def array_border_margin(self):
        return self.stroke_width * 4

    @property
    def array_cell_sep(self):
        return self.array_border_margin

    def _add_shape(self, factory, points, svg_doc):
        shape = factory(points=points)
        shape.stroke(width=self.stroke_width,
                     color=self.stroke_color)
        shape.fill(color="none")
        svg_doc.add(shape)

    def draw_at(self, frame, top_left, svg_doc):
        _A = anchors.Anchor
        # todo -- offset these points by half of stroke width
        corners = [tuple(anchors.from_top_left_corner(frame, top_left, anch))
                   for anch in [_A.top_left, _A.top_right,
                                _A.bottom_right, _A.bottom_left]]
        self._add_shape(svg_doc.polygon, corners, svg_doc)

        for i in range(1, frame.num_cols):
            x_coord = i * (frame.width - self.array_border_margin) / frame.num_cols + top_left[0] + self.array_border_margin / 2
            self._add_shape(svg_doc.polyline,
                            [(x_coord, top_left[1]),
                             (x_coord, top_left[1] + frame.height)],
                            svg_doc)
        for i in range(1, frame.num_rows):
            y_coord = i * (frame.height - self.stroke_width) / frame.num_rows + top_left[1]
            self._add_shape(svg_doc.polyline,
                            [(top_left[0], y_coord),
                             (top_left[0] + frame.width, y_coord)],
                            svg_doc)

class DefaultNullPainter(NullPainter):
    def __init__(self, null_size=(6, 8)):
        self._null_size = null_size

    @property
    def null_size(self):
        return self._null_size

    def draw_at(self, null, coord, svg_doc):
        svg_doc.add(svg_doc.polygon(points=list(
            anchors.from_top_left_corner(null, coord, anch)
            for anch in [anchors.Anchor.top,
                         anchors.Anchor.right,
                         anchors.Anchor.bottom,
                         anchors.Anchor.left])))

class NodeElementPainter(RectangularElementPainter):
    pass

class EllipseNodeElementPainter(NodeElementPainter):
    def draw_at(self, node_elt, top_left, svg_doc):
        svg_doc.add(svg_doc.ellipse(
            center=anchors.from_top_left_corner(node_elt, top_left,
                                                anchors.Anchor.center),
            r=(node_elt.width / 2, node_elt.height / 2),
            stroke="black",
            stroke_width="1",
            fill_opacity="0.10"))

class BoxNodeElementPainter(NodeElementPainter):
    def draw_at(self, node_elt, top_left, svg_doc):
        svg_doc.add(svg_doc.rect(insert=top_left,
                                 size=(node_elt.width, node_elt.height),
                                 stroke="black",
                                 stroke_width="1",
                                 fill_opacity="0.10"))

class InvisibleNodeElementPainter(NodeElementPainter):
    def draw_at(self, node, top_left, svg_doc):
        pass

class PointerElementPainter(RectangularElementPainter, PointerHint):
    pass

class DefaultPointerElementPainter(PointerElementPainter):
    def __init__(self, ptr_size=(4, 6)):
        self._ptr_size = ptr_size
    def draw_at(self, ptr_elt, top_left, svg_doc):
        svg_doc.add(svg_doc.ellipse(
            center=anchors.from_top_left_corner(
                ptr_elt, top_left, anchors.Anchor.center),
            r=(ptr_elt.width, ptr_elt.height),
        ))

    @property
    def pointer_source_size(self):
        return self._ptr_size


class ArrowElementPainter(ElementPainter):
    # maybe put code for arrowheads here, since people who want lots of
    # arrowhead options will just choose GraphViz anyway?
    # Also so we can delegate and have fancy behavior that subclasses don't know about.
    def draw_arrowhead(self, tip_coord, angle, svg_doc):
        gamma = math.pi / 6
        length = 8
        points = [tip_coord]
        for offset_angle in (angle + math.pi + gamma, angle + math.pi - gamma):
            points.append((tip_coord[0] + length * math.cos(offset_angle),
                           tip_coord[1] + length * math.sin(offset_angle)))
        svg_doc.add(svg_doc.polygon(points=points))

    def possible_endpoints(self, arrow, locations):
        for src_anch, dst_anch in arrow.anchor_pairs():
            yield tuple(anchors.from_top_left_corner(rect, locations[rect], anch)
                        for rect, anch in ((arrow.origin, src_anch),
                                           (arrow.destination, dst_anch)))

    def closest_connection_points(self, arrow, locations):
        def dist_squared(points):
            return sum((a-b)**2 for a, b in zip(*points))

        return min(self.possible_endpoints(arrow, locations),
                   key=dist_squared)

    def angle(self, src, dst):
        vector = (dst[0] - src[0], dst[1] - src[1])
        if vector[0] == 0:
            return math.copysign(math.pi / 2, vector[0])
        atan = math.atan(vector[1] / vector[0])
        return atan if vector[0] > 0 else atan + math.pi

class StraightArrowElementPainter(ArrowElementPainter):
    def draw(self, arrow, locations, svg_doc):
        src, dst = self.closest_connection_points(arrow, locations)
        svg_doc.add(svg_doc.line(src, dst, style="stroke:rgb(50,50,50);stroke-width:2"))
        self.draw_arrowhead(dst, self.angle(src, dst), svg_doc)

class SplineArrowElementPainter(StraightArrowElementPainter):
    pass  # TODO -- splines instead

class IncompleteLayoutError(Exception):
    pass

class FullSVGPainter:

    def __init__(self, delegates, margin=7):
        """Pass a dictionary mapping Element subclasses to ElementPainter subclasses"""
        delegates.setdefault(elements.NodeElement, BoxNodeElementPainter())
        delegates.setdefault(elements.StringElement, DefaultStringPainter())
        delegates.setdefault(elements.PointerSource, DefaultPointerElementPainter())
        delegates.setdefault(elements.NullElement, DefaultNullPainter())
        delegates.setdefault(elements.Arrow, StraightArrowElementPainter())
        delegates.setdefault(elements.SplineArrow, StraightArrowElementPainter())
        delegates.setdefault(elements.StraightArrow, delegates[elements.Arrow])
        delegates.setdefault(elements.ArrayFrame, BlackBorderArrayFramePainter())
        self._delegates = delegates
        self._margin = margin
        self._pending_arrows = collections.defaultdict(set)
        self._locations = collections.OrderedDict()
        self._svg_doc = None
        self.hint = self._make_hint()

    def layout_to_svg(self, layout):
        self._pending_arrows.clear()
        self._locations.clear()
        self._svg_doc = svgwrite.Drawing(size=(layout.width, layout.height))
        for elem in layout.elements():
            if isinstance(elem, tuple):
                coord, elem = elem
            else:
                coord = None
            self._draw_element(elem, coord=coord)
            self._draw_pending_arrows(elem)
        if any(self._pending_arrows.values()):
            raise  IncompleteLayoutError(
                "Some elements were never placed but were supposed to have "
                "arrows between them:  {}".format(
                    ", ".join(repr(elt) for elt, arrows
                              in self._pending_arrows.items() if arrows)))
        result = self._svg_doc.tostring()
        self._svg_doc = None
        return result

    def _draw_element(self, elem, coord=None):
        if isinstance(elem, elements.Arrow):
            ready = True
            for endpt in (elem.origin, elem.destination):
                if endpt not in self._locations:
                    ready = False
                    self._pending_arrows[endpt].add(elem)
            if not ready:
               return
        self._locations[elem] = coord
        self._delegates[type(elem)].draw(elem, self._locations, self._svg_doc)

    def _draw_pending_arrows(self, new_elt):
        for arrow in list(self._pending_arrows[new_elt]):
            self._pending_arrows[new_elt].discard(arrow)
            self._draw_element(arrow)

    def _make_hint(self):
        return DelegatingSVGHint(
            str_hint=self._delegates[elements.StringElement],
            ptr_hint=self._delegates[elements.PointerSource],
            null_hint=self._delegates[elements.NullElement],
            array_frame_hint=self._delegates[elements.ArrayFrame],
            margin=self._margin)

def default_full_drawer():
    return FullSVGPainter({})
