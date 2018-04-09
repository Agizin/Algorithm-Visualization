from collections import namedtuple
import pygraphviz as pgv

from typing import List, Tuple, Dict, String


class NodeSpec():
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.label = None

    def __str__(self):
        return self.label


def node_spec(width: float = .75, height: float = .50) -> NodeSpec:
    # can extend with keyword arguments if we extend node
    # without breaking existing client code
    return NodeSpec(width, height)


Edge = Tuple[NodeSpec, NodeSpec]
Attrs = Dict[str, str]
Location = Tuple[int, int]
NodesToLocations = Dict[str, Location]


def layout_graph_nodes(nodes: List[NodeSpec],
                       edges: List[Edge],
                       nodeAttrs: Attrs=None,
                       edgeAttrs: Attrs=None,
                       algo: str="dot") -> NodesToLocations:
    """ Maps nodes to their coordinates.

    Applicable values for nodeAttrs, edgeAttrs, and algo can be found in the
    pygraphviz/graphviz docs.
    """
    if nodeAttrs is None:
        nodeAttrs = {}
    if edgeAttrs is None:
        edgeAttrs = {}
    G = pgv.AGraph()

    c = 0
    name_to_node = {}

    def label_node(node):
        nonlocal c, name_to_node
        if node.label is None:
            node.label = str(c)
            c += 1
        name_to_node[node.label] = node

    for node in nodes:
        label_node(node)
        G.add_node(node, fixedsize=True,
                   width=node.width, height=node.height, **nodeAttrs)
        c += 1
    for (node1, node2) in edges:
        label_node(node1)
        label_node(node2)
        G.add_edge(node1, node2, **edgeAttrs)

    G.layout(prog=algo)
    dictNodesLocations = {}

    def get_position(node):
        return tuple(int(x) for x in node.attr['pos'].split(','))
    for node in G.nodes():
        dictNodesLocations[name_to_node[node.get_name()]] = get_position(node)
    return dictNodesLocations


def parse_graphviz_splines(edge_pos):
    return [Spline(s) for s in edge_pos.split(';')]


Point = namedtuple("Point", ("x", "y"))


def point_from_graphviz(graphviz_pt: String):
    return Point(float(t) for t in graphviz_pt.split(","))

# BezierCurve = namedtuple("BezierCurve", ("ctrl0", "ctrl1", "endpoint"))


def pt_to_svg(point):
    return "{} {}".format(*point)


class BezierCurve:
    def __init__(self, ctrl0, ctrl1, endpoint):
        self.ctrl0 = ctrl0
        self.ctrl1 = ctrl1
        self.endpoint = endpoint

    def to_svg(self):
        return "C{} {} {}".format(self.ctrl0, self.ctrl1, self.endpoint)


class Spline():
    def __init__(self, start_pt, *curves, arrow_tips=(None, None)):
        self.start_pt = start_pt
        self.curves = curves
        self.arrow_tips = arrow_tips

    def get_arrows(self):
        for base, tip in zip([self.start_pt, self.curves[-1].endpoint],
                             self.arrow_tips):
            if tip is not None:
                yield (base, tip)

    def get_svg_path(self):
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
        # '27,71.831 27,61 27,47.288 27,36.413'
        # return Spline(*(to_point(edge_pos.split(" "))
        startp, endp = None, None
        pt_strings = edge_pos.split(" ")
        if "e" in pt_strings[0]:
            endp = point_from_graphviz(pt_strings[0].strip("e,"))
            pt_strings = pt_strings[1:]
        if "s" in pt_strings[0]:
            startp = point_from_graphviz(pt_strings[0].strip("s,"))
            pt_strings = pt_strings[1:]
        beziers = []
        points = [point_from_graphviz(pt_str for pt_str in pt_strings)]
        start_point = points[0]
        for c0, c1, endpt in zip(points[1::3],
                                 points[2::3],
                                 points[3::3]):
            beziers.append(BezierCurve(c0, c1, endpt))
        return Spline(start_point, *beziers, arrow_tips=(startp, endp))
