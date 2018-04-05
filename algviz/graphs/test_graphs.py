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
                 [(1, 1)] * 200]
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
        for node, coord in coords.items():
            self.assertIsInstance(node, graphs.NodeSpec)
            x, y = coord
            self.assertIsInstance(x, (int, float))
            self.assertIsInstance(y, (int, float))
        self._assert_none_overlap(coords)

    def _assert_nodes_do_not_overlap(self, node0, loc0, node1, loc1):
        self.assertFalse(
            (loc1[0] - node0.width <= loc0[0] <= loc1[0] + node1.width) and
            (loc1[1] - node0.height <= loc0[1] <= loc1[1] + node1.height),
            msg="node {} (at {}) overlaps node {} (at {})".format(
                node0, loc0, node1, loc1))

    def _assert_none_overlap(self, node_locations):
        for node, corner in node_locations.items():
            for other_node, other_corner in node_locations.items():
                if node is not other_node:
                    self._assert_nodes_do_not_overlap(node, corner, other_node, other_corner)

if __name__ == "__main__":
    unittest.main()
