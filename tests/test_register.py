"""The addon registers cleanly and can be toggled repeatedly."""

import unittest

import bpy
import helpers


class RegisterTest(unittest.TestCase):
    def test_all_classes_registered(self):
        auto_load = helpers.sn("auto_load")
        missing = [
            cls.__name__
            for cls in auto_load.ordered_classes
            if not getattr(cls, "is_registered", False)
        ]
        self.assertEqual(missing, [], "classes failed to register")

    def test_toggle(self):
        for _ in range(2):
            helpers.disable_addon()
            self.assertFalse(hasattr(bpy.types.Scene, "sna"))
            helpers.enable_addon()
            self.assertTrue(hasattr(bpy.types.Scene, "sna"))
        self.test_all_classes_registered()

    def test_node_count(self):
        # sanity check that node discovery works at all
        self.assertGreater(len(helpers.node_classes()), 80)
