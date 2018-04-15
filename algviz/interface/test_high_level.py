#!/usr/bin/env python3

import unittest
from unittest import mock

from . import visitors
from .testutil import TempFileTestMixin
from algviz.parser import json_objects

import contextlib

class HighLevelTestCase(TempFileTestMixin, unittest.TestCase):

    def setUp(self):
        self.setup_tempfile()

    def tearDown(self):
        self.teardown_tempfile()

    @contextlib.contextmanager
    def patched_high_level(self):
        with self.patch_stdout():
            # Sorrow befalls the user of globals
            from . import high_level as hl
            hl._reset()
            yield hl

    def test_functional_show_interface(self):
        mylist = [1, 2, 3, 4, 5]
        with self.patched_high_level() as hl:  # replace stdout with self.tempfile
            hl.show(mylist, "myvarname", visitors.ArrayVisitor)
            hl.show("mystring", "stringname")
        self.assertEqual(mylist, [1, 2, 3, 4, 5], msg="We broke the list while printing it")
        text = self.read_tempfile()
        [list_snapshot, str_snapshot] = json_objects.reads(text)
        self.assertEqual(list(list_snapshot.names["myvarname"]),
                         [1, 2, 3, 4, 5])
        self.assertEqual(str(str_snapshot.names["stringname"]),
                         "mystring")

    def test_string_snapshot(self):
        mylist = [1, 2, 3, 4, 5]
        with self.patched_high_level() as hl:
            text = hl.string_snapshot(mylist)
        self.assertIsInstance(text, str)

    def test_string_snapshot_matches_normal_snapshot(self):
        mylist = [1, 2, 3, 4, 5]
        with self.patched_high_level():
            from . import high_level as hl
            text = hl.string_snapshot(mylist)
            hl.show(mylist)
        self.assertIsInstance(text, str)
        self.assertEqual(text, self.read_tempfile())
