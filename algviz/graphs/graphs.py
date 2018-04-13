from collections import namedtuple
import pygraphviz as pgv
import warnings
import io

from typing import List, Tuple, Dict


class _NodeSpec():
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.pinned_loc = None
        # self.label = None

    def pin_center(self, x, y):
        """Fix the position of this node"""
        self.pinned_loc = (x, y)

    # def __str__(self):
    #     return self.label


def node_spec(width: float = .75, height: float = .50) -> _NodeSpec:
    """Use this to make nodes"""
    # can extend with keyword arguments if we extend node
    # without breaking existing client code
    return _NodeSpec(width, height)


Edge = Tuple[_NodeSpec, _NodeSpec]
Attrs = Dict[str, str]
Location = Tuple[int, int]
NodesToLocations = Dict[str, Location]

class NotLaidOutError(Exception):
    pass

class GraphVizSeed:
    def __init__(self, seed=-1):
        self.value = int(seed)
        if self.value != -1 and not self.is_deterministic():
            warnings.warn("Seed {} will be ignored because it is not a positive integer"
                          .format(self.value))

    def is_deterministic(self):
        return self.value > 0

    def to_startType(self):
        return "random" + str(self.value)

class GraphVizGraph:
    def __init__(self,
                 nodes: List[_NodeSpec] = None,
                 edges: List[Edge] = None,
                 nodeAttrs: Attrs = None,
                 edgeAttrs: Attrs = None,
                 algo: str="neato",  # only "neato" allows us to pin nodes
                 seed=None,
                 directed=True,
    ):
        if isinstance(seed, GraphVizSeed):
            self._seed = seed
        elif seed is None:
            self._seed = GraphVizSeed()
        else:
            self._seed = GraphVizSeed(seed)
        self._node_attrs = nodeAttrs or {}
        self._edge_attrs = edgeAttrs or {}
        self._edge_attrs.setdefault("minlen", 1)
        self._edge_attrs.setdefault("len", 1)
        self._init_graph(nodes, edges)
        self.layout(algo)

    def _init_graph(self, nodes, edges):
        self._next_label = 0
        self._name_to_node = {}
        self.nodes = {}
        self.graph = pgv.AGraph(start=self._seed.to_startType())
        if nodes is not None:
            for node in nodes:
                self.add_node(node)
        self.edges = set()
        if edges is not None:
            for edge in edges:
                self.add_edge(*edge)

    def add_edge(self, src: _NodeSpec, dst: _NodeSpec):
        if src not in self.nodes:
            self.add_node(src)
        if dst not in self.nodes:
            self.add_node(dst)
        self.edges.add((src, dst))
        self.graph.add_edge(self._get_node_label(src),
                            self._get_node_label(dst),
                            **self._edge_attrs)

    def add_node(self, node: _NodeSpec):
        if self._get_node_label(node) is not None:
            raise ValueError("new nodes should have None labels")
        self._label_node(node)
        extra_kwargs = {}
        if node.pinned_loc is not None:
            extra_kwargs["pin"] = True
            extra_kwargs["pos"] = "{:f},{:f}!".format(*node.pinned_loc)
        if node.width is not None:
            extra_kwargs["width"] = node.width
        if node.height is not None:
            extra_kwargs["height"] = node.height
        if node.height is not None and node.width is not None:
            extra_kwargs["fixedsize"] = True
        self.graph.add_node(self._get_node_label(node),
                            **extra_kwargs, **self._node_attrs)

    def _label_node(self, node):
        label = str(self._next_label)
        self.nodes[node] = label
        self._next_label += 1
        self._name_to_node[label] = node

    def _get_node_label(self, node):
        return self.nodes.get(node, None)

    def layout(self, algo: str):
        self.graph.layout(prog=algo)

    def get_node_locations(self) -> Dict[_NodeSpec, Tuple[float, float]]:
        locations = {}
        def get_position(gv_node):
            return tuple(float(x) for x in gv_node.attr['pos'].split(','))

        for gv_node in self.graph.nodes():
            locations[self._name_to_node[gv_node.get_name()]] = get_position(gv_node)
        return locations

    def _get_gv_edge(self, edge: Tuple[_NodeSpec, _NodeSpec]):
        return self.graph.get_edge(self._get_node_label(edge[0]),
                                   self._get_node_label(edge[1]))

    def get_edge_splines(self):
        splines = {}
        for edge in self.edges:
            attr = self._get_gv_edge(edge).attr
            if 'pos' not in attr:
                raise NotLaidOutError("edges were added after calling `layout`")
            splines[edge] = parse_graphviz_spline(attr['pos'])
        return splines

    def get_full_svg(self):
        with io.BytesIO() as f:
            f.name = "noname.svg"
            self.graph.draw(f)
            return f.getvalue().decode()

def layout_graph_nodes(nodes: List[_NodeSpec],
                       edges: List[Edge],
                       nodeAttrs: Attrs=None,
                       edgeAttrs: Attrs=None,
                       algo: str="dot") -> NodesToLocations:
    """ Maps nodes to their coordinates.

    Applicable values for nodeAttrs, edgeAttrs, and algo can be found in the
    pygraphviz/graphviz docs.
    """
    return GraphVizGraph(nodes, edges, nodeAttrs, edgeAttrs, algo).get_node_locations()

def parse_graphviz_spline(edge_pos):
    splines = [Spline.from_graphviz(s) for s in edge_pos.split(';')]
    if len(splines) != 1:
        # If we start getting this, we'll need to figure out how to put
        # multiple splines in one SVG path attribute, and we can make another
        # spline class to do it for us
        raise NotImplementedError("We don't know what to do when a graphviz "
                                  "SplineType contains more than one spline")
    return splines[0]

Point = namedtuple("Point", ("x", "y"))


def point_from_graphviz(graphviz_pt: str):
    return Point(*(float(t) for t in graphviz_pt.split(",")))

# BezierCurve = namedtuple("BezierCurve", ("ctrl0", "ctrl1", "endpoint"))


def pt_to_svg(point):
    return "{} {}".format(*point)


class BezierCurve:
    def __init__(self, ctrl0, ctrl1, endpoint):
        self.ctrl0 = ctrl0
        self.ctrl1 = ctrl1
        self.endpoint = endpoint

    def to_svg(self):
        return "C" + ", ".join("{} {}".format(*point) for point in
                               [self.ctrl0, self.ctrl1, self.endpoint])

class Spline():
    def __init__(self, start_pt, *curves, arrow_tips=(None, None)):
        self.start_pt = start_pt
        self.curves = curves
        if len(self.curves) < 1:
            raise ValueError("Something's up -- this spline is empty!")
        self.arrow_tips = arrow_tips

    def get_arrows(self):
        for base, tip in zip([self.start_pt, self.curves[-1].endpoint],
                             self.arrow_tips):
            if tip is not None:
                yield (base, tip)

    def to_svg_path(self):
        curvesPaths = []
        for curve in self.curves:
            # TODO: explore if we can use S instead of C after the first curve:
            # https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
            curvesPaths.append(curve.to_svg())
        return " ".join(curvesPaths)

    @classmethod
    def from_graphviz(cls, edge_pos: str):
        if ';' in edge_pos:
            raise ValueError("{} has separators.  Use parse_graphviz_splines"
                             .format(edge_pos))
        if edge_pos.strip() == "":
            raise ValueError("Can't make an empty spline")
        # '27,71.831 27,61 27,47.288 27,36.413'
        # return Spline(*(to_point(edge_pos.split(" "))
        startp, endp = None, None
        pt_strings = list(edge_pos.split(" "))
        if "e" in pt_strings[0]:
            endp = point_from_graphviz(pt_strings[0].strip("e,"))
            pt_strings = pt_strings[1:]
        if "s" in pt_strings[0]:
            startp = point_from_graphviz(pt_strings[0].strip("s,"))
            pt_strings = pt_strings[1:]
        beziers = []
        points = [point_from_graphviz(pt_str) for pt_str in pt_strings]
        start_point = points[0]
        for c0, c1, endpt in zip(points[1::3],
                                 points[2::3],
                                 points[3::3]):
            beziers.append(BezierCurve(c0, c1, endpt))
        return Spline(start_point, *beziers, arrow_tips=(startp, endp))
