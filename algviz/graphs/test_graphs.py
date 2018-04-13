import unittest
from . import graphs
import re

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

    def test_edges_can_include_new_nodes(self):
        nodes = [graphs.node_spec(w, h) for w, h in
                 [(1, 1)] * 100]
        edges = [(graphs.node_spec(1, 1), graphs.node_spec(1, 1))]
        coords = graphs.layout_graph_nodes(nodes, edges)
        self.assertIsInstance(coords, dict)
        self.assertEqual(len(nodes) + len(edges)*2, len(coords))

    def test_node_sizes_are_respected(self):
        nodes = [graphs.node_spec(w, h) for w, h in
                 [(i, 1000 - i) for i in range(1, 1000, 100)]]
        edges = [(a, b) for a in nodes for b in nodes if a != b]
        coords = graphs.layout_graph_nodes(nodes, edges)
        self._sanity_assertions(nodes, edges, coords)

    def test_graph_layout_is_repeatable(self):
        nodes = [graphs.node_spec(w, h) for w, h in
                 [(i, 1000 - i) for i in range(1, 1000, 50)]]
        edges = [(a, b) for a in nodes for b in nodes if a != b and b != nodes[0]]
        coords = [graphs.GraphVizGraph(nodes, edges, seed=100).get_node_locations()
                  for _ in range(6)]
        for coord0, coord1 in zip(coords, coords[1:]):
            self.assertEqual(coord0, coord1)
        different = graphs.GraphVizGraph(nodes, edges, seed=9999).get_node_locations()
        self.assertNotEqual(coords[0], different)

    def _sanity_assertions(self, nodes, edges, coords):
        self.assertIsInstance(coords, dict)
        self.assertEqual(len(nodes), len(coords))
        for node, coord in coords.items():
            self.assertIsInstance(node, graphs._NodeSpec)
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

    def test_getting_edge_splines(self):
        nodes = [graphs.node_spec(w, h) for w, h in [(1, 2)] * 100]
        edges = []
        for a, b, c in zip(nodes, nodes[::-1], nodes[:1]):
            edges.extend([(a, b), (b, c), (c, a)])
        G = graphs.GraphVizGraph(nodes, edges, algo="circo")
        edge_to_splines = G.get_edge_splines()
        self.assertIsInstance(edge_to_splines, dict)
        for edge in edges:
            self.assertIn(edge, edge_to_splines)
            spline = edge_to_splines[edge]
            self.assertIsInstance(spline, graphs.Spline)
            self._assert_svg_spline_reasonable(spline.to_svg_path())

    def _assert_svg_spline_reasonable(self, svg_spline):
        self.assertIsInstance(svg_spline, str)
        self.assertGreater(len(svg_spline), 10)
        self.assertTrue(re.match("^[A-Za-z0-9\\., ]+$", svg_spline), msg=svg_spline)
        # TODO ... figure out syntax for splines

if __name__ == "__main__":
    unittest.main()
