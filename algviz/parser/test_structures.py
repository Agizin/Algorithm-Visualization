import unittest
from . import structures

class NullTestCase(unittest.TestCase):

    def test_Null(self):
        self.assertIsNot(None, structures.Null)
        self.assertIs(structures.Null,  # can't make a new, distinct Null
                      type(structures.Null)())
        self.assertEqual(structures.Null, structures.Null)
        self.assertNotEqual(structures.Null, None)
        self.assertFalse(structures.Null)
        self.assertEqual(hash(structures.Null), hash(structures.Null))

class DataStructuresTestMixin:

    def test_hashable(self):
        self.assertIsInstance(hash(self.instance()), int)

    def test_equality(self):
        self.assertEqual(self.instance(), self.instance())

class PointerTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.Pointer(structures.String("foo", uid="s"),
                                  uid="p")

class StringTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.String("foo", uid="s")

class WidgetTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.Widget(uid="w")

class ArrayTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.Array([], uid='arr')

class LinkedListNodeTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.LinkedListNode(0,
                                         structures.LinkedListNode(1, uid="t"),
                                         uid="h")

class GraphTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.Graph([], [], uid="g")

class NodeTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.Node(structures.Null, uid="n")

class EdgeTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.Edge(structures.Node(0, uid="n0"),
                               structures.Node(1, uid="n1"),
                               uid="e")

class TreeNodeTestCase(DataStructuresTestMixin, unittest.TestCase):
    def instance(self):
        return structures.TreeNode(5, children=[structures.Null,
                                                structures.Null],
                                   uid="tree")

class ObjectTableTestCase(unittest.TestCase):

    def setUp(self):
        self.obj_tab = structures.ObjectTable()

    def test_null_always_in_table(self):
        self.assertIn(structures.ObjectTableReference(structures.Null.uid),
                      self.obj_tab)

    def test_keys_must_be_object_table_references(self):
        obj = structures.Widget(uid="some_kinda_widget")
        with self.assertRaises(TypeError):
            self.obj_tab[obj.uid] = obj
        # make sure the key didn't go in before the error got thrown
        self.assertNotIn(obj.uid, self.obj_tab)

    def test_getuid_convenience_method(self):
        self.assertEqual(self.obj_tab.getuid(structures.Null.uid),
                         structures.Null)

if __name__ == "__main__":
    unittest.main()
