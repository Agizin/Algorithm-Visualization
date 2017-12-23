import unittest
from . import structures

class DataStructuresTestCase(unittest.TestCase):

    def test_Null(self):
        self.assertIsNot(None, structures.Null)
        self.assertIs(structures.Null,  # can't make a new, distinct Null
                      type(structures.Null)())
        self.assertEqual(structures.Null, structures.Null)
        self.assertNotEqual(structures.Null, None)
        self.assertFalse(structures.Null)
        self.assertEqual(hash(structures.Null), hash(structures.Null))

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
