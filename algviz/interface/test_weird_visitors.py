import unittest
import tempfile

from algviz.parser import json_objects, structures
from . import weird_visitors
from . import output

from .test_visitors import VisitorTestCaseMixin

class BitmapVisitorTestCase(VisitorTestCaseMixin, unittest.TestCase):
    visitor_cls = weird_visitors.BitmapArrayVisitor
    def setUp(self):
        super().setUp()
        self._next_sample_bool = True

    def test_bitmap_visit(self):
        with self.output_mngr.start_snapshot():
            self.visitor.traverse(123, var="mybits")  # traverse 123 == 0b1111011 as a bitmap
        _, snapshots = self.read_result()
        array = snapshots[0].names["mybits"]
        self.assertEqual(list(array), [1, 1, 0, 1, 1, 1, 1])

    def sample_instance(self):
        # This is a hack to make the number returned always be the same
        # but the UID of two consecutive instances be different.
        # (True == 1 but id(True) != id(1))
        self._next_sample_bool ^= True
        return True if self._next_sample_bool else 1


class ListTreeVisitorTestCase(VisitorTestCaseMixin, unittest.TestCase):
    visitor_cls = weird_visitors.ListTreeVisitor

    def test_tree_visit(self):
        tree = self.to_json_and_back([1, 2])
        self.assertEqual(tree.data, 1)
        self.assertEqual(tree.children[1], structures.Null)
        self.assertEqual(tree.children[0].data, 2)
        self.assertEqual(tree.children[0].children, [structures.Null] * 2)

    def sample_instance(self):
        return [4, 2, 6, 1, 3, 5, 7]
