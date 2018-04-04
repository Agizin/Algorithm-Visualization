import pygraphviz as pgv


class NodeSpec():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.label = None

    def __str__(self):
        return self.label


def node_spec(width, height):
    # can extend with keyword arguments if we extend node
    # without breaking existing client code
    return NodeSpec(width, height)


def layout_graph_nodes(nodes, edges, nodeAttrs=None,
                       edgeAttrs=None, algo="dot"):
    """ Maps node to their coordinates.

    nodeNames: a list of names for the nodes
    nodeWidths: a dictionary mapping the name of a node to a width specified
        by the caller. Default .75.
    nodeHeights: a dictionary mapping the names of a node to a height specified
        by the caller. Default .50.
    nodeAttrs: a dictionary that can specify the attributes of a given node
    edges: a list of tuples of 2 node names which represents an edge between
        the two of them
    edgeAttrs: a dictionary that can specify the attributes of a given edge
    algo: The algorithm to use when assigning positions to nodes in the graph
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
