#!/usr/bin/env python

import sys

sys.path.insert(0, "../src")

import unittest

from rules import NPC


class TestMultiMap(unittest.TestCase):
    def setUp(self):
        char = NPC("NPC", 3, 3, 8, 1)

    def test_get1(self):
        self.assertTrue(np.all(
            self.data.get("day", bird=1) ==
            np.array([np.float(x + 1) for x in range(10)])))
        self.assertTrue(np.all(
            self.data.get("day", bird=2) ==
            np.array([np.float(x + 1) for x in range(10) if x != 1])))


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestMultiMap)
    unittest.TextTestRunner(verbosity=2).run(suite)
