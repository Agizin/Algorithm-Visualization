import unittest
import json

from . import json_objects
from . import structures


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

    @unittest.expectedFailure
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
        decoded_graph = snapshot.obj_table[structures.ObjectTableReference("G123")]
        raise NotImplementedError("Need to test decoding of the graph")

    def test_binary_tree(self):
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

    def test_array_decoding(self):
        snapshot = self._list_to_snapshot(
            [{"T": "array", "uid": "my_array", "data": [1, 2, 3, "my_array"]}])
        my_array = self._get_from_table(snapshot.obj_table, "my_array")
        self.assertEqual(my_array, my_array[3])
        other_array = structures.Array([1, 2, 3])
        self.assertEqual(my_array[:3], other_array)
        self.assertNotEqual(my_array, other_array)

    def test_literal_decoding(self):
        num_snapshot = self._text_to_snapshot(
            '''[1, 2, 3, 4, 4.0, 4]''')
        # currently we don't bother storing numeric literals in the object table.
        self.assertEqual(len(num_snapshot.obj_table), 0)
        self.assertEqual(len(num_snapshot.names), 0)
        str_snapshot = self._list_to_snapshot(
            [{"T": "string", "data": "Hello, world!", "uid": "s"}])
        my_str = self._get_from_table(str_snapshot.obj_table, "s")
        self.assertEqual(my_str, structures.String("Hello, world!"))

    def test_var_key_shows_up_in_namespace(self):
        widg_list_desc = '''[{"T": "array", "var": "mylist", "data": [1, 2, 3, {"type": "widget", "var": "my_widget", "uid": "testuid"}]}]'''
        snapshot = self._text_to_snapshot(widg_list_desc)
        self.assertEqual(snapshot.names["mylist"],
                         structures.Array([1, 2, 3, snapshot.names["my_widget"]]))

    def _get_from_table(self, obj_table, str_key):
        return obj_table[structures.ObjectTableReference(str_key)]

    def _list_to_snapshot(self, lst):
        return self._text_to_snapshot(json.dumps(lst))

    def _text_to_snapshot(self, text):
        return json_objects.decode_snapshot(*json_objects.parse(text))

class GenericDecodingTestCase(unittest.TestCase):
    """Make a subclass of this to test decoding of a specific type of object.

    The superclass tests Widgets, rather minimally.
    """
    expected_uid = "expected_uid"
    expected_metadata = {"success": True, "metadata can have": ["arbitrary json !@#$%^&*()"]}
    def setUp(self):
        # It's not necessary to override this method in subclass
        self.set_up_expectations()
        self.actual_snapshot = json_objects.decode_snapshot(
            *json_objects.parse(json.dumps(self.snapshot_input)))
        self.actual_object = self.actual_snapshot.obj_table[
            structures.ObjectTableReference(self.expected_uid)]

    def set_up_expectations(self):
        #  subclass should override this method
        self.snapshot_input = [{"T": "widget",
                                "metadata": self.expected_metadata,
                                "uid": self.expected_uid}]
        self.expected_object = structures.Widget()

    def test_has_proper_metadata(self):
        self.assertEqual(self.actual_object.metadata, self.expected_metadata)

    def test_matches_expected_object(self):
        self.assertEqual(self.actual_object, self.expected_object)

    def test_has_proper_uid(self):
        self.assertEqual(self.actual_object.uid, self.expected_uid)

class ArrayDecodingTestCase(GenericDecodingTestCase):

    def set_up_expectations(self):
        self.snapshot_input = [{
            "T": "array", "uid": self.expected_uid, "metadata": self.expected_metadata,
            "data": [1, 2, 3, 4, {"T": "string", "data": "hello"}],
        }]
        self.expected_object = structures.Array([1, 2, 3, 4, structures.String("hello")])

class BinaryTreeDecodingTestCase(GenericDecodingTestCase):

    def set_up_expectations(self):
        self.snapshot_input = [
            {
                "T": "bintree", "uid": self.expected_uid,
                "metadata": self.expected_metadata,
                "root": "myroot"
            }, {
                "T": "btnode", "uid": "myroot", "left": "n0", "data": {"T": "null"}
            }, {
                "T": "btnode", "uid": "n0", "data": 3
            }]
        self.expected_object = structures.BinaryTree(
            root=structures.BinaryTreeNode(
                structures.Null,
                left=structures.BinaryTree(3)))

class BinaryTreeDecodingTestCase(GenericDecodingTestCase):
    expected_uid = "#null"

    def set_up_expectations(self):
        self.snapshot_input = [{"T": "null"}]
        self.expected_object = structures.Null

    def test_has_proper_metadata(self):
        self.assertIs(getattr(self.actual_object, "metadata", None), None)

if __name__ == "__main__":
    unittest.main()
