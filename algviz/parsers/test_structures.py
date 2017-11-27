import structures
import unittest

class DataStructuresTestCase(unittest.TestCase):

    def test_Null(self):
        self.assertIsNot(None, structures.Null)
        self.assertIs(structures.Null,  # can't make a new, distinct Null
                      type(structures.Null)())
        self.assertEqual(structures.Null, structures.Null)
        self.assertNotEqual(structures.Null, None)
        self.assertFalse(structures.Null)
        self.assertEqual(hash(structures.Null), hash(structures.Null))

if __name__ == "__main__":
    unittest.main()
