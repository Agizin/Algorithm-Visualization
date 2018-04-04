from typing import List, Tuple, Dict
import pygraphviz as pgv


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
