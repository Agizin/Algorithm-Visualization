import collections.abc
import json
import unittest

from . import json_objects
from . import structures

def _text_to_snapshot(text):
    return json_objects.decode_snapshot(*json_objects.parse(text))

def _list_to_snapshot(lst):
    return _text_to_snapshot(json.dumps(lst))

def _get_from_table(obj_table, str_key):
    return obj_table[structures.ObjectTableReference(str_key)]


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

    def test_literal_decoding(self):
        num_snapshot = _list_to_snapshot([1, 2, 3, 4, 4.0, 4])
        # currently we don't bother storing numeric literals in the object table.
        empty_snapshot = _list_to_snapshot([])
        self.assertEqual(len(num_snapshot.obj_table), len(empty_snapshot.obj_table))
        self.assertEqual(len(num_snapshot.names), len(empty_snapshot.names))

    def test_var_key_shows_up_in_namespace(self):
        widg_list_desc = '''[{"T": "array", "uid": "testuid", "var": "mylist", "data": [1, 2, 3, {"type": "widget", "var": "my_widget"}]}]'''
        snapshot = _text_to_snapshot(widg_list_desc)
        self.assertEqual(snapshot.names["mylist"],
                         structures.Array([1, 2, 3, snapshot.names["my_widget"]],
                                          uid="testuid"))

    def test_can_handle_missing_outermost_close_bracket(self):
        """Sometimes it's more trouble than it's worth to print the last
        closing brace, since that amounts to saying "I'm confident there will
        be no more printing after this!"
        """
        self.assertEqual(json_objects.reads('[[{"T": "widget"}]]'),
                         json_objects.reads('[[{"T": "widget"}]'))

class GenericDecodingTestCase(unittest.TestCase):
    """Make a subclass of this to test decoding of a specific type of object.

    The superclass tests Widgets, rather minimally.

    __eq__ methods on DataStructures are only useful for these (and maybe other) test cases, since we rarely do any computation with data structures.
    """
    expected_uid = "expected_uid"
    expected_metadata = {"success": True, "metadata can have": ["arbitrary json !@#$%^&*()"]}
    cls_under_test = structures.Widget

    def setUp(self):
        # It's not necessary to override this method in subclass
        self.set_up_expectations()
        self.actual_snapshot = _list_to_snapshot(self.snapshot_input)
        self.actual_object = self.actual_snapshot.obj_table[
            structures.ObjectTableReference(self.expected_uid)]

    def set_up_expectations(self):
        #  subclass should override this method
        self.snapshot_input = [{"T": "widget",
                                "metadata": self.expected_metadata,
                                "uid": self.expected_uid}]
        self.expected_object = self.factory()
        self.unexpected_object = self.factory(uid=(self.expected_uid + "asdf"))
        self.same_uid_object = self.factory(metadata=None)

    def factory(self, *args, **kwargs):
        """Prefered way to make instances of `self.cls_under_test`"""
        kwargs.setdefault("uid", self.expected_uid)
        kwargs.setdefault("metadata", self.expected_metadata)
        return self.cls_under_test(*args, **kwargs)

    def test_has_proper_type(self):
        self.assertIsInstance(self.actual_object, self.cls_under_test)

    def test_has_proper_metadata(self):
        self.assertEqual(self.actual_object.metadata, self.expected_metadata)

    def test_same_object_method_works_based_on_uid(self):
        self.assertTrue(self.actual_object.same_object(self.same_uid_object))

    def test_matches_expected_object(self):
        self.assertEqual(self.actual_object, self.expected_object)
        self.assertNotEqual(self.actual_object, self.unexpected_object)

    def test_has_proper_uid(self):
        self.assertEqual(self.actual_object.uid, self.expected_uid)

    def test_hash_matches_hash_of_placeholder(self):
        # To keep life simple, if our objects are hashable, then the hash
        # should be equal to the hash of the ObjectTableReference placeholder.
        if isinstance(self.actual_object, collections.abc.Hashable):
            self.assertEqual(hash(self.actual_object),
                             hash(structures.ObjectTableReference(self.actual_object.uid)))

    def test_equality_depends_on_uid(self):
        different_uid = "a totally different uid"
        # make sure equality fails when uid is different (and everything else is the same)
        self.assertNotEqual(self.actual_object,
                            self._decode_with_different_uid(different_uid))
        # make sure equality holds when uid is the same
        self.assertEqual(self._decode_with_different_uid(different_uid),
                         self._decode_with_different_uid(different_uid))

    def _decode_with_different_uid(self, new_uid):
        copy_of_snapshot_input = json.loads(json.dumps(self.snapshot_input))
        def _replace_uid(obj):
            if isinstance(obj, dict):
                self.assertNotIn(new_uid, obj.values(),
                                 msg=("Test code falsely assumed that the uid {}"
                                      " was not in use".format(new_uid)))
                return {key: new_uid if val == self.expected_uid else val
                        for key, val in obj.items()}
            else:
                return obj
        new_snapshot_input = json_objects.post_order_visit(
            copy_of_snapshot_input, visit=_replace_uid, skip=lambda x: ("metadata",))
        return _get_from_table(_list_to_snapshot(new_snapshot_input).obj_table,
                                  new_uid)

class ArrayDecodingTestCase(GenericDecodingTestCase):
    cls_under_test = structures.Array

    def set_up_expectations(self):
        self.snapshot_input = [{
            "T": "array", "uid": self.expected_uid, "metadata": self.expected_metadata,
            "data": [1, 2, 3, 4, {"T": "string", "data": "hello", "uid": "s"}],
        }]
        self.expected_object = self.factory([1, 2, 3, 4, structures.String("hello", uid="s")])
        self.unexpected_object = self.factory([1, 2, 3, 4, structures.String("goodbye")])
        self.same_uid_object = self.factory([1, 2, 3])

class TreeDecodingTestCase(GenericDecodingTestCase):
    cls_under_test = structures.Tree
    def set_up_expectations(self):
        self.snapshot_input = [
            {"T": "treenode", "uid": "L", "children": ["LL", "#null"], "data": 1},
            {"T": "treenode", "uid": self.expected_uid, "children": ["L", "R"], "data": 4,
             "metadata": self.expected_metadata},
            {"T": "treenode", "uid": "LL", "data": 1},
            {"T": "treenode", "uid": "R", "data": "#null"},
        ]
        R = self.factory(structures.Null, uid="R")
        LL = self.factory(1, uid="LL")
        L = self.factory(1, uid="L", children=[LL, structures.Null])
        self.expected_object = self.factory(4, children=[L, R])
        self.unexpected_object = self.factory(4, children=[R, L])
        self.same_uid_object = self.factory(4, children=[R])

class NullDecodingTestCase(GenericDecodingTestCase):
    expected_uid = "#null"
    cls_under_test = structures.NullType
    def set_up_expectations(self):
        self.snapshot_input = [{"T": "null"}]
        self.expected_object = structures.Null
        self.unexpected_object = structures.Pointer(structures.Null)
        self.same_uid_object = structures.Null

    def test_equality_depends_on_uid(self):
        """This shouldn't test anything for Null"""
        pass

    def test_has_proper_metadata(self):
        self.assertIs(getattr(self.actual_object, "metadata", None), None)

    def test_decodes_to_singleton(self):
        self.assertIs(self.actual_object, self.expected_object)

class OtherNullDecodingTestCase(NullDecodingTestCase):

    def set_up_expectations(self):
        super().set_up_expectations()
        self.snapshot_input = ["#null"]

class StringDecodingTestCase(GenericDecodingTestCase):
    cls_under_test = structures.String
    def set_up_expectations(self):
        text = r"Blah blah blah \n \\weird stuff\\\\"
        self.snapshot_input = [{"T": "string",
                                "uid": self.expected_uid,
                                "metadata": self.expected_metadata,
                                "data": text}]
        self.expected_object = self.factory(text)
        self.unexpected_object = self.factory(text, uid="not same")
        self.same_uid_object = self.factory("hello, world")

class PointerDecodingTestCase(GenericDecodingTestCase):

    cls_under_test = structures.Pointer
    def set_up_expectations(self):
        self.snapshot_input = [
            {"T": "array", "uid": "asdf", "data": [1, 2, 3, 4, 5]},
            {"T": "ptr", "uid": self.expected_uid, "data": "asdf",
             "metadata": self.expected_metadata}
        ]
        self.expected_object = self.factory(structures.Array([1, 2, 3, 4, 5], uid="asdf"))
        self.unexpected_object = self.factory(self.factory(structures.Widget(),
                                                           uid="different"))
        self.same_uid_object = self.factory(structures.Widget)

class GraphDecodingTestCase(GenericDecodingTestCase):
    cls_under_test = structures.Graph
    def set_up_expectations(self):
        self.snapshot_input = [
            {"T": "graph", "uid": self.expected_uid, "metadata": self.expected_metadata,
             "nodes": [
                 {"T": "node", "uid": "n0", "data": 0},
                 {"T": "node", "uid": "n1", "data": {"T": "ptr", "data": 3, "uid": "p0"}},
                 {"T": "node", "uid": "n2", "data": 10},
             ],
             "edges": [
                 {"T": "edge", "uid": "e0", "from": "n0", "to": "n1"},
                 {"T": "edge", "uid": "e1", "from": "n0", "to": "n2"},
                 {"T": "edge", "uid": "e2", "from": "n2", "to": "n2", "data": 100},
                 {"T": "edge", "uid": "e3", "from": "n2", "to": "n0"},
             ]}]
        n0 = structures.Node(0, uid="n0")
        n1 = structures.Node(structures.Pointer(3, uid="p0"), uid="n1")
        n2 = structures.Node(10, uid="n2")
        e0 = structures.Edge(n0, n1, uid="e0")
        e1 = structures.Edge(n0, n2, uid="e1")
        e2 = structures.Edge(n2, n2, uid="e2", data=100)
        e3 = structures.Edge(n2, n0, uid="e3")

        self.expected_object = self.factory(
            nodes=[n0, n2, n1],
            edges=[e0, e2, e1, e3])  # order shouldn't matter
        self.unexpected_object = self.factory(
            nodes=[n0, n1, n2],
            edges=[e0, e1, structures.Edge(n2, n2), e3])
        self.same_uid_object = self.unexpected_object

class NodeDecodingTestCase(GenericDecodingTestCase):
    cls_under_test = structures.Node
    def set_up_expectations(self):
        self.snapshot_input = [
            {"T": "node", "uid": self.expected_uid, "metadata": self.expected_metadata,
             "data": 1200},
        ]
        self.expected_object = self.factory(1200)
        self.same_uid_object = self.factory(-10)
        self.unexpected_object = self.factory(100, uid=(self.expected_uid + "not"))

class EdgeDecodingTestCase(GenericDecodingTestCase):
    cls_under_test = structures.Edge
    def set_up_expectations(self):
        self.snapshot_input = [
            {"T": "edge", "uid": self.expected_uid, "metadata": self.expected_metadata,
             "data": 1200, "from": "n0", "to": "n1"},
            {"T": "node", "uid": "n0", "data": 3},
            {"T": "node", "uid": "n1", "data": 10},
        ]
        n0 = structures.Node(3, uid="n0")
        n1 = structures.Node(10, uid="n1")
        self.expected_object = self.factory(orig=n0, dest=n1, data=1200)
        self.same_uid_object = self.factory(orig=n1, dest=n0, data=-10)
        self.unexpected_object = self.factory(orig=n1, dest=n0, data=1200)

if __name__ == "__main__":
    unittest.main()
