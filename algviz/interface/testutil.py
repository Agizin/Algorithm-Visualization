import contextlib
import tempfile
import unittest
from unittest import mock

class TempFileMixin(object):
    def setup_tempfile(self):
        self.tempfile = tempfile.TemporaryFile("r+")

    def read_tempfile(self):
        self.tempfile.seek(0)
        return self.tempfile.read()

    def teardown_tempfile(self):
        self.tempfile.close()

    def write_tempfile(self, text):
        with self.patch_stdout():
            print(text, end="")

    def open_tempfile_read(self):
        self.tempfile.seek(0)
        return self.tempfile

    @contextlib.contextmanager
    def patch_stdout(self):
        try:
            with mock.patch("sys.stdout", new=self.tempfile):
                yield
        finally:
            pass

class TempFileTestMixin(TempFileMixin):
    """Must precede `unittest.TestCase` in the method resolution order (`mro`).

    (This means it must be listed before `unittest.TestCase` in the subclass
    definition.)
    """
    def setUp(self):
        self.setup_tempfile()
        super().setUp()

    def tearDown(self):
        self.teardown_tempfile()
        super().tearDown()

class TempFileMixinTestCase(TempFileTestMixin, unittest.TestCase):

    def test_patching_stdout(self):

        with self.patch_stdout():
            print("I am a potato")
        self.assertEqual(self.read_tempfile(),
                         "I am a potato\n")

    def test_patching_stdout_error_condition(self):
        class MySillyException(Exception):
            pass
        try:
            with self.patch_stdout():
                print("foo")
                raise MySillyException()
        except MySillyException:
            pass
        # Now make sure stdout is normal again...
        # This means our test may have to print stuff to stdout
        print("excuse me")
        self.assertEqual(self.read_tempfile(),
                         "foo\n")

if __name__ == "__main__":
    unittest.main()
