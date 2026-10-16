"""Opens GUI Blender on the Object Toolkit plus a "Problems" tree that breaks
the extensions platform's guidelines, with Addon › Extensions Platform open.
Run by scripts/open_example.py:

    python scripts/open_example.py tests/visual/open_export_check_example.py
"""

import os
import sys
import traceback

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import open_toolkit_example as toolkit  # noqa: E402

helpers = toolkit.helpers


def problems():
    """An operator doing what reviewers reject."""
    tree = helpers.new_tree("Problems")
    op = helpers.add_node(tree, "SNA_Node_Operator", (-900, 300))
    op.inputs["label"].value = "Do Questionable Things"
    previous = op.outputs["execute"]

    def then(idname, location, code=None):
        nonlocal previous
        node = helpers.add_node(tree, idname, location)
        if code is not None:
            node.code = code
            helpers.flush()
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
        return node

    # all objects of the file, and one that may not exist
    cube = helpers.add_node(tree, "SNA_Node_BlendData", (-900, 0))
    cube.paste_path('bpy.data.objects["Cube"].location')
    printer = then("SNA_Node_Print", (-600, 300))
    helpers.link(tree, cube.outputs[0], printer.socket("text"))

    # a preset file next to the add-on's code
    info = helpers.add_node(tree, "SNA_Node_AddonInfo", (-600, -100))
    join = helpers.add_node(tree, "SNA_Node_JoinPath", (-350, -100))
    helpers.link(tree, info.outputs["folder"], join.socket("first"))
    join.socket("part").value = "presets.txt"
    write = then("SNA_Node_WriteTextFile", (-300, 300))
    helpers.link(tree, join.outputs[0], write.socket("path"))
    write.socket("text").value = "preset"

    then("SNA_Node_PythonStatement", (0, 300), "import sys; sys.path.append('/tmp')")
    then(
        "SNA_Node_PythonStatement",
        (300, 300),
        "import urllib.request; urllib.request.urlopen('https://example.com')",
    )
    then(
        "SNA_Node_PythonStatement",
        (600, 300),
        "context.window_manager.clipboard = 'copied'",
    )
    helpers.flush()
    return tree


def open_check_panel():
    """Addon and Extensions Platform start closed: register them open."""
    ui = helpers.sn("src.settings.ui.addon_panel")
    panels = (ui.SNA_PT_Addon_Settings, ui.SNA_PT_Export_Check)
    for cls in reversed(panels):
        bpy.utils.unregister_class(cls)
    for cls in panels:
        cls.bl_options = set(cls.bl_options) - {"DEFAULT_CLOSED"}
        bpy.utils.register_class(cls)


def start():
    try:
        helpers.enable_addon()
        toolkit._toolkit_demo.build()
        bpy.context.scene.sna.addon.author = ""  # missing metadata too
        tree = problems()
        helpers.sn("src.core.export_check").run()
        open_check_panel()
        window, area = toolkit.show(tree)
        bpy.app.timers.register(lambda: toolkit.frame(window, area), first_interval=0.5)
        bpy.ops.wm.save_as_mainfile(filepath=toolkit.OUTPUT)
        print("EXAMPLE READY", toolkit.OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


bpy.app.timers.register(start, first_interval=0.5)
