"""Text nodes: Multiline Label, Markdown and Link. Their helpers use
UILayout.label_multiline / label_markdown / link where Blender has them and draw a
simpler version on older Blender."""

import importlib
import sys
import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


def generated_helpers():
    """`_sn_helpers` of the loaded add-on (through its package: names in
    sys.modules can be left over from earlier loads)."""
    package = sys.modules[bpy.context.scene.sna.addon.module_name]
    return importlib.import_module(package.__name__ + "._sn_helpers")


class FakeLayout:
    """Records what the fallbacks draw (older UILayouts)."""

    def __init__(self, calls=None):
        self.calls = calls if calls is not None else []
        self.alignment = "EXPAND"

    def column(self, align=False):
        return FakeLayout(self.calls)

    def label(self, **kwargs):
        self.calls.append(("label", kwargs))

    def separator(self, **kwargs):
        self.calls.append(("separator", kwargs))

    def operator(self, idname, **kwargs):
        props = type("Props", (), {})()
        self.calls.append(("operator", idname, kwargs, props))
        return props


class TextNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Text Test"
        self.tree = helpers.new_tree("Main")
        self.panel = helpers.add_node(self.tree, "SNA_Node_Panel")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        for text in list(bpy.data.texts):
            bpy.data.texts.remove(text)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def add(self, idname):
        node = helpers.add_node(self.tree, idname)
        helpers.link(self.tree, self.panel.outputs["body"], node.inputs[0])
        return node

    def source(self):
        helpers.flush()
        return helpers.tree_source(self.tree)

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    def test_multiline_label(self):
        node = self.add("SNA_Node_MultilineLabel")
        node.socket("text").value = "Some text"
        self.assertIn("sn_label_multiline(self.layout, 'Some text')", self.source())
        node.socket("icon").value = "INFO"
        node.socket("max_lines").value = 2
        node.alignment = "CENTER"
        self.assertIn(
            "sn_label_multiline(self.layout, 'Some text', max_lines=2, "
            "alignment='CENTER', icon='INFO')",
            self.source(),
        )
        self.assertLoaded()

    def test_text_from_a_text_block(self):
        node = self.add("SNA_Node_Markdown")
        text = bpy.data.texts.new("Notes")
        text.write("# Title\n- one")
        node.text_block = text
        helpers.flush()
        self.assertFalse(node.socket("text").enabled)  # the text block replaces it
        self.assertIn(
            "sn_label_markdown(self.layout, '# Title\\n- one')", self.source()
        )
        self.assertLoaded()
        # editing the text rebuilds (no RNA update: watched)
        scheduler = helpers.sn("src.core.scheduler")
        scheduler.run_watchers()
        text.write("\n- two")
        scheduler.run_watchers()
        self.assertIn("- two", self.source())

    def test_link(self):
        node = self.add("SNA_Node_Link")
        node.socket("url").value = "https://example.com"
        self.assertIn("sn_link(self.layout, 'https://example.com')", self.source())
        node.socket("text").value = "Docs"
        node.socket("icon").value = "URL"
        self.assertIn(
            "sn_link(self.layout, 'https://example.com', text='Docs', icon='URL')",
            self.source(),
        )
        self.assertLoaded()

    def test_fallbacks_on_older_blender(self):
        markdown = self.add("SNA_Node_Markdown")  # uses sn_label_multiline too
        link = helpers.add_node(self.tree, "SNA_Node_Link")
        helpers.link(self.tree, markdown.outputs[0], link.inputs[0])
        helpers.flush()
        self.assertLoaded()
        generated = generated_helpers()

        layout = FakeLayout()
        generated.sn_label_multiline(
            layout, "one\ntwo\nthree", max_lines=2, icon="INFO"
        )
        self.assertEqual(
            layout.calls,
            [
                ("label", {"text": "one", "icon": "INFO"}),
                ("label", {"text": "two", "icon": "BLANK1"}),
            ],
        )

        layout = FakeLayout()
        generated.sn_label_markdown(
            layout, "# Title\n\n- **bold** item\n---\nSee [docs](https://x.org)"
        )
        drawn = [
            call[1].get("text", call[0]) if call[0] == "label" else call[0]
            for call in layout.calls
        ]
        self.assertEqual(
            drawn, ["Title", "separator", "• bold item", "separator", "See docs"]
        )

        layout = FakeLayout()
        generated.sn_link(layout, "https://x.org", icon="URL")
        _, idname, kwargs, props = layout.calls[0]
        self.assertEqual(idname, "wm.url_open")
        self.assertEqual(kwargs, {"text": "https://x.org", "icon": "URL"})
        self.assertEqual(props.url, "https://x.org")
