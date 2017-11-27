import unittest

from . import json_objects
from . import structures
# from . import symbols  # too abstract, not useful in long term

def format_test_case(json_string):
    # In case we change json_objects.Tokens in early development,
    # we may want to have our keys be the names of attributes of json_objects.Tokens
    # instead of the values of those attributes
    # do this the silly way
    mapping = {attr: getattr(json_objects.Tokens, attr)
               for attr in dir(json_objects.Tokens) if not attr.startswith("_")}
    raise NotImplementedError("This could just be silly")

class JSONObjectsTestCase(unittest.TestCase):
    """Test decoding JSON into DataStructure instances"""

    def test_aliases_are_not_already_tokens(self):
        symbols = [getattr(json_objects.Tokens, name)
                   for name in dir(json_objects.Tokens)
                   if not name.startswith("_")]
        for alias in json_objects.aliases:
            self.assertNotIn(alias, symbols,
                             msg=("Alias {} for {} conflicts with existing symbol {}"
                                  .format(alias, json_objects.aliases[alias], alias)))

    def test_fix_aliases(self):
        obj = {"T": "null"}
        json_objects.fix_aliases(obj)
        self.assertEqual(obj, {"type": "null"})

    def test_graph_decoding(self):
        graph_test_case = """
        [{
            "type": "graph",
            "uid": "G123",
            "nodes": ["n0", "n1", "n2", "n3"],
            "edges": ["e0",
                      {"type": "edge", "uid": "thisone", "from": "n0", "to": "n1", "data": 1},
                      "e2",
                      "e3"
                     ]
        },
        {"uid": "n0", "type": "node", "data": {"type": "string", "data": "Node 0"}},
        {"uid": "n1", "type": "node", "data": 4},
        {"uid": "n2", "type": "node", "data": 100},
        {"uid": "n3", "type": "node", "data": {"T": "null"}},
        {"uid": "e0", "type": "edge", "from": "n1", "to": "n2"},
        {"uid": "e2", "type": "edge", "from": "n2", "to": "n0"},
        {"uid": "e3", "type": "edge", "from": "n2", "to": "n3"}
        ]
        """
        snapshot = json_objects.decode_snapshot(*json_objects.parse(graph_test_case))
        # raise NotImplementedError("Need to test decoding of the graph")
        decoded_graph = snapshot.obj_table[structures.ObjectTableReference("G123")]
        print(decoded_graph)
        raise NotImplementedError("Need to test decoding of the graph")

    def test_binary_tree(self):
#         bintree = """
#         [{
#            "type": "binarytree",
#            "uid": "mytree",
#            "root": "myroot",
#         },
#         {"uid": "myroot", "type": "node"},
#         {"uid": "n0", "type": "node", "data": 0},
#         {"uid": "n1", "type": "node", "data": 1},
#         {"uid": "n2", "type": "node", "data": 2},
#         {"uid": "n3", "type": "node", "data": 3},
#         {"uid": "e0", "type": "edge", "from": "myroot", "to": "n0", "metadata": {"direction": "left"}, "data": "foo"},
#         {"uid": "e1", "type": "edge", "from": "myroot", "to": "n1", "metadata": {"direction": "right"}, "data": "bar"},
#         {"uid": "e2", "type": "edge", "from": "n1", "to": "n2", "metadata": {"direction": "left"}, "data": "buz"},
#         {"uid": "e3", "type": "edge", "from": "n2", "to": "n3", "metadata": {"direction": "right"}, "data": "etc"},
#         {
#            "type": "binarytree",
#            "uid": "mysubtree",
#            "root": "n1",
#         },
#         ]
# """
        bintree_text = """[
            {
                "type": "bintree",
                "uid": "mytree",
                "root": "myroot"
            },
            {"uid": "myroot", "T": "btnode", "left": "n0", "right": "n1", "data": {"type": "null"}},
            {"uid": "n0", "T": "btnode", "data": 0},
            {"uid": "n1", "T": "btnode", "data": 1, "left": "n2", "right": "n3"},
            {"uid": "n2", "T": "btnode", "data": 2},
            {"uid": "n3", "T": "btnode", "data": 3}
        ]"""
        snapshot = json_objects.decode_snapshot(*json_objects.parse(bintree_text))
        mytree = snapshot.obj_table[structures.ObjectTableReference('mytree')]
        self.assertEqual(mytree,
                         structures.BinaryTree(
                             root=structures.BinaryTreeNode(
                                 structures.Null,
                                 left=structures.BinaryTreeNode(0),
                                 right=structures.BinaryTreeNode(
                                     1,
                                     left=structures.BinaryTreeNode(2),
                                     right=structures.BinaryTreeNode(3)
                                 )
                             )
                         ))

        #      (myroot)
        #  (n0)       (n1)
        #          (n2)  (n3)

if __name__ == "__main__":
    unittest.main()
