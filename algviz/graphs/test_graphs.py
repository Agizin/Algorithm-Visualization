import unittest
from . import graphs


class GraphLayoutTestCase(unittest.TestCase):
    def test_layout_graph_nodes(self):
        nodes = [graphs.node_spec(w, h) for w, h in
                 [(1, 1), (2, 2), (3, 3), (1, 1)]]
        edges = []
        coords = graphs.layout_graph_nodes(nodes, edges)
        self._sanity_assertions(nodes, edges, coords)

    def test_layout_small_graph_nodes(self):
        nodes = [graphs.node_spec(w, h) for w, h in
                 [(1, 1)] * 100]
        edges = [(nodes[0], nodes[10])]
        coords = graphs.layout_graph_nodes(nodes, edges)
        self._sanity_assertions(nodes, edges, coords)

    def test_layout_edge_nodes_different_from_original_nodes(self):
        nodes = [graphs.node_spec(w, h) for w, h in
                 [(1, 1)] * 100]
        edges = [(graphs.node_spec(1, 1), graphs.node_spec(1, 1))]
        coords = graphs.layout_graph_nodes(nodes, edges)
        self.assertIsInstance(coords, dict)
        self.assertEqual(len(nodes) + len(edges)*2, len(coords))

    def _sanity_assertions(self, nodes, edges, coords):
        self.assertIsInstance(coords, dict)
        self.assertEqual(len(nodes), len(coords))
