"""Pie Menu, Popover, Open Menu, and what Shortcut and Open Menu can open."""

import bpy
import helpers
from flow_case import FlowTestCase, errors


class MenuNodesTest(FlowTestCase):
    addon_name = "Menu Test"

    def label(self, text):
        node = self.add("SNA_Node_Label")
        node.socket("text").value = text
        return node

    def test_pie_menu_slots(self):
        pie = self.add("SNA_Node_PieMenu")
        pie.socket("label").value = "Quick"
        self.link(pie.outputs["top"], self.label("Up").inputs[0])
        self.link(pie.outputs["left"], self.label("West").inputs[0])
        self.assertBuilt()
        source = self.source()
        self.assertIn("class MENU_TEST_MT_quick(bpy.types.Menu):", source)
        # left, right (empty), bottom (empty), top; nothing after the last
        body = source[source.index("menu_pie()") :]
        self.assertEqual(body.count("pie.separator()"), 2)
        self.assertLess(body.index("'West'"), body.index("'Up'"))
        self.assertNotIn("top_left", body)
        self.assertTrue(hasattr(bpy.types, "MENU_TEST_MT_quick"))

    def test_menu_class_exists_without_a_button(self):
        menu = self.add("SNA_Node_Menu")
        menu.socket("label").value = "Lonely"
        self.link(menu.outputs["content"], self.label("Hi").inputs[0])
        self.assertBuilt()
        self.assertTrue(hasattr(bpy.types, "MENU_TEST_MT_lonely"))

    def test_open_menu_calls(self):
        targets = {}
        pie = self.add("SNA_Node_PieMenu")
        pie.socket("label").value = "Pie"
        targets["wm.call_menu_pie(name='MENU_TEST_MT_pie')"] = pie
        menu = self.add("SNA_Node_Menu")
        menu.socket("label").value = "Plain"
        targets["wm.call_menu(name='MENU_TEST_MT_plain')"] = menu
        panel = self.add("SNA_Node_Panel")
        panel.socket("label").value = "Tools"
        targets["wm.call_panel(name='MENU_TEST_PT_tools')"] = panel
        opener = self.then("SNA_Node_OpenMenu")
        helpers.flush()
        self.assertEqual(errors().node_message(opener.id), "Pick a menu")
        for call, target in targets.items():
            with self.subTest(call=call):
                helpers.point(opener, "menu", target)
                helpers.flush()
                self.assertIn(f"bpy.ops.{call}", self.source())
        labels = [label for label, _ in opener.sn_references["menu"].choices(opener)]
        self.assertEqual(sorted(labels), ["Pie", "Plain", "Tools"])

    def test_shortcut_opens_a_pie(self):
        pie = self.add("SNA_Node_PieMenu")
        shortcut = self.add("SNA_Node_Shortcut")
        shortcut.action = "MENU"
        helpers.point(shortcut, "menu", pie)
        self.assertBuilt()
        self.assertIn(
            "'wm.call_menu_pie', 'A', properties={'name': 'MENU_TEST_MT_pie_menu'})",
            self.source(),
        )

    def test_popover(self):
        panel = self.add("SNA_Node_Panel")
        panel.socket("label").value = "Options"
        holder = self.add("SNA_Node_Panel")
        popover = self.add("SNA_Node_Popover")
        self.link(holder.outputs["body"], popover.inputs[0])
        helpers.flush()
        self.assertEqual(errors().node_message(popover.id), "Pick a panel")
        helpers.point(popover, "panel", panel)
        popover.socket("label").value = "More"
        popover.socket("icon").value = "PREFERENCES"
        self.assertBuilt()
        self.assertIn(
            "self.layout.popover('MENU_TEST_PT_options', text='More', icon='PREFERENCES')",
            self.source(),
        )
