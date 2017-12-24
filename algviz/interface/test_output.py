import unittest
import tempfile
import contextlib

from . import output

class OutputManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.TemporaryFile("r+")
        self.outman = output.OutputManager(outfile=self.tmpfile)

    def tearDown(self):
        self.tmpfile.close()

    def test_basic_usage(self):
        with self.outman.start_snapshot():  # start a snapshot
            with self.outman.push():  # start an object
                self.outman.next_key("mykey")
                with self.outman.push(mapping=False):
                    for i in range(5):
                        self.outman.next_val(i)
                self.outman.next_key("other")
                self.outman.next_val("thingy")
        self.outman.end()  # close the list of snapshots
        result = self._get_text()
        self.assertEqual(result.strip(),
                         """
[
  [
    {
      "mykey": [
        0,
        1,
        2,
        3,
        4
      ],
      "other": "thingy"
    }
  ]
]
                         """.strip())

    def test_error_for_duplicate_key(self):
        with self.assertRaisesRegex(output.OutputStateError,
                                     "Key .data. is a duplicate.*"):
            with self.outman.start_snapshot():
                with self.outman.push():  # start an object
                    self.outman.next_key("data")
                    self.outman.next_val(1)
                    self.outman.next_key("data")
                    self.outman.next_val(2)

    def test_error_for_invalid_key(self):
        with self.assertRaisesRegex(TypeError,
                                    "JSON keys must be string.*"):
            with self.outman.start_snapshot():
                with self.outman.push():
                    self.outman.next_key(12)

    def test_error_for_setting_next_key_without_using_prev_key(self):
        with self.assertRaisesRegex(output.OutputStateError,
                                    "previous key .*foo.* not used .*bar.*"):
            with self.outman.start_snapshot():
                with self.outman.push():
                    self.outman.next_key("foo")
                    self.outman.next_key("bar")

    def test_error_for_key_value_pair_in_a_list(self):
        with self.assertRaisesRegex(output.OutputStateError,
                                    "cannot set a key .* in non-mapping context .*"):
            with self.outman.start_snapshot():
                self.outman.next_key("asdf")

    def test_error_for_adding_value_with_no_key_in_mapping(self):
        with self.assertRaisesRegex(output.OutputStateError,
                                   "Must set a key .*"):
            with self.outman.start_snapshot():
                with self.outman.push():
                    # Do the first key normally
                    self.outman.next_key("llama")
                    self.outman.next_val("elephant")
                    # Now mess up
                    self.outman.next_val("aardvark")


    def test_error_for_defining_same_uid_twice_in_snapshot(self):
        with self.assertRaisesRegex(output.OutputStateError,
                                    "uid .*asdf.* already defined in this snapshot"):
            with self.outman.start_snapshot():
                with self.outman.push():
                    # First widget
                    self.outman.next_key("uid")
                    self.outman.next_val("asdf")
                    self.outman.next_key("type")
                    self.outman.next_val("widget")
                with self.outman.push():
                    self.outman.next_key("uid")
                    self.outman.next_val("asdf")

    def _get_text(self):
        self.tmpfile.seek(0)
        return self.tmpfile.read()

if __name__ == "__main__":
    unittest.main()
