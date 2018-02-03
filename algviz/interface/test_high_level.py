#!/usr/bin/env python3

import unittest
from unittest import mock

from . import visitors
from .testutil import TempFileTestMixin
from algviz.parser import json_objects

class HighLevelTestCase(TempFileTestMixin, unittest.TestCase):

    def setUp(self):
        self.setup_tempfile()

    def tearDown(self):
        self.teardown_tempfile()

    def test_functional_show_interface(self):
        mylist = [1, 2, 3, 4, 5]
        with self.patch_stdout():  # replace stdout with self.tempfile
            from . import high_level as hl
            hl.show(mylist, "myvarname", visitors.ArrayVisitor)
            hl.show("mystring", "stringname")
        self.assertEqual(mylist, [1, 2, 3, 4, 5], msg="We broke the list while printing it")
        text = self.read_tempfile()
        [list_snapshot, str_snapshot] = json_objects.reads(text)
        self.assertEqual(list(list_snapshot.names["myvarname"]),
                         [1, 2, 3, 4, 5])
        self.assertEqual(str(str_snapshot.names["stringname"]),
                         "mystring")
