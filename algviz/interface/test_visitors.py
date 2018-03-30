import unittest

from algviz.parser import json_objects, structures
from . import output
from . import visitors
from .testutil import TempFileMixin

class VisitorTestCaseMixin(TempFileMixin):

    def setUp(self):
        self.setup_tempfile()
        self.output_mngr = output.OutputManager(outfile=self.tempfile)
        self.visitor = self.visitor_cls(self.output_mngr)

    def tearDown(self):
        self.teardown_tempfile()

    def read_result(self):
        self.output_mngr.end()
        text = self.read_tempfile()
        return text, json_objects.decode_json(text)

    def to_json_and_back_full_result(self, instance, **kwargs):
        """Convenience for test cases where you only need to encode and decode
        one instance.  Returns (json_text, decoded_object)
        """
        with self.output_mngr.start_snapshot():
            self.visitor.traverse(instance, **kwargs)
        return self.read_result()

    def to_json_and_back(self, instance, **kwargs):
        """Visit the object, print it out, decode it, and return the resulting object"""
        _, snapshots = self.to_json_and_back_full_result(instance, **kwargs)
        return snapshots[-1].obj_table.getuid(self.visitor.uid(instance))

    def test_metadata(self):
        """Make sure metadata makes it through the process the way it should"""
        def mk_metadata():
            return {"I": {"AM": ["metadataaaaaaaaaaa", 1]},
                    "the number eight": 8, "note": "keys must be strings"}
        self.assertIsNot(mk_metadata(), mk_metadata(),
                         msg="""This test doesn't work.  We want different
                         instances of identical dictionaries, or else the test
                         can be passed by calling `metadata.clear()`.""")
        result = self.to_json_and_back(self.sample_instance(),
                                       metadata=mk_metadata())
        self.assertEqual(mk_metadata(), result.metadata)

    def test_varnames(self):
        """Ensure the correct object has the correct variable name"""
        inst1 = self.sample_instance()
        inst2 = self.sample_instance()
        with self.output_mngr.start_snapshot():
            self.visitor.traverse(inst1, var="inst1")
            self.visitor.traverse(inst2, var="inst2")
        _, [snapshot] = self.read_result()
        for inst, name in [(inst1, "inst1"), (inst2, "inst2")]:
            self.assertEqual(snapshot.names[name],
                             snapshot.obj_table.getuid(self.visitor.uid(inst)))

    def sample_instance(self):
        """Should return an object suitable for `self.visitor` to traverse.

        Successive calls should return distinct objects.
        """
        raise NotImplementedError("Implement in each subclass.  See docstring")


class WidgetVisitorTestCase(VisitorTestCaseMixin, unittest.TestCase):
    visitor_cls = visitors.WidgetVisitor

    def test_widget_export_and_import(self):
        with self.output_mngr.start_snapshot():
            self.visitor.traverse("Some string", var="first")
            self.visitor.traverse(7, var="second", metadata={"hello": "world"})
        _, snapshots = self.read_result()
        first = snapshots[0].names["first"]
        self.assertIsInstance(first, structures.Widget)
        snd = snapshots[0].names["second"]
        self.assertIsInstance(snd, structures.Widget)
        self.assertEqual(snd.metadata, {"hello": "world"})

    def sample_instance(self):
        return object()

class ArrayVisitorTestCase(VisitorTestCaseMixin, unittest.TestCase):
    visitor_cls = visitors.ArrayVisitor

    def sample_instance(self):
        return [1, 2, 3]

    def test_array_export_and_import(self):
        arr = self.to_json_and_back([1, 2, 3])
        self.assertIsInstance(arr, structures.Array)
        self.assertEqual(list(arr), [1, 2, 3])
