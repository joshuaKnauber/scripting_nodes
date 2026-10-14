"""A panel with a Multiline Label, Markdown from a text data-block and a
Link, next to the node tree."""

import bpy
import helpers

WINDOW_SIZE = (1600, 800)
LAYOUT = "split"
SIDEBAR_TAB = "Text"

MARKDOWN = """## Getting started
- Select an object
- Press **Apply** to run the tool
> Settings are saved with the file
---
Read the [manual](https://docs.blender.org) for more."""


def setup():
    bpy.context.scene.sna.addon.addon_name = "Text Demo"
    tree = helpers.new_tree("Interface")
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-900, 100))
    panel.inputs["Label"].value = "Text"
    panel.panel_category = "Text"
    intro = helpers.add_node(tree, "SNA_Node_MultilineLabel", (-600, 150))
    intro.socket("text").value = (
        "This text is longer than the panel is wide, so it wraps over "
        "several lines instead of being cut off."
    )
    intro.socket("icon").value = "INFO"
    notes = bpy.data.texts.new("Notes.md")
    notes.write(MARKDOWN)
    markdown = helpers.add_node(tree, "SNA_Node_Markdown", (-300, 150))
    markdown.text_block = notes
    link = helpers.add_node(tree, "SNA_Node_Link", (0, 150))
    link.socket("url").value = "https://www.blender.org"
    link.socket("text").value = "blender.org"
    link.socket("icon").value = "URL"
    helpers.link(tree, panel.outputs["body"], intro.inputs[0])
    helpers.link(tree, intro.outputs[0], markdown.inputs[0])
    helpers.link(tree, markdown.outputs[0], link.inputs[0])
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
