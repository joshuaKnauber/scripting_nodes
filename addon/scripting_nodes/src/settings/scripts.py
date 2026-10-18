"""The add-on's scripts (Addon Data › Scripts): text blocks or files that are
part of the add-on (core/scripts.py), and the source fields they share with
Inline Script nodes."""

import bpy

from ..core import scheduler
from ..core import scripts as script_list
from ..core.context import NodeError
from ..lib.ids import get_short_id
from ..lib.trees import node_by_id

SCRIPT_TEMPLATE = '''import bpy


def run(context, name: str = "World") -> str:
    """Call it with a Script Function node: parameters are the node's inputs,
    return values its outputs. `context` (also `layout`, `self`, `event`) is
    passed in."""
    message = f"Hello {name} from {context.scene.name}!"
    return message


# Optional: called when the add-on is enabled / disabled
# def register():
#     ...
#
# def unregister():
#     ...
'''


def _changed(self, context):
    script_list.changed(self)


class SNA_Script(script_list.ScriptSource, bpy.types.PropertyGroup):
    """A script of the add-on."""

    id: bpy.props.StringProperty(options={"HIDDEN"})
    source_type: bpy.props.EnumProperty(
        items=[
            ("INTERNAL", "Text", "Use a text block from the blend file"),
            ("EXTERNAL", "File", "Use an external Python file"),
        ],
        name="Source",
        description="Where to load the script from",
        update=_changed,
    )
    text_block: bpy.props.PointerProperty(
        type=bpy.types.Text,
        name="Text",
        description="Text block with the script",
        update=_changed,
    )
    filepath: bpy.props.StringProperty(
        name="File",
        description="Path to a Python file",
        subtype="FILE_PATH",
        update=_changed,
    )

    sn_template = SCRIPT_TEMPLATE
    sn_template_name = "script.py"


def _owner(owner_id):
    """A list script or an Inline Script node with that id."""
    return script_list.find(owner_id) or node_by_id(owner_id)


class SNA_OT_NewScript(bpy.types.Operator):
    """Create a script from a template (into the picked text if it's empty)"""

    bl_idname = "sna.new_script"
    bl_label = "New Script"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    owner_id: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        owner = _owner(self.owner_id)
        if owner is None:
            return {"CANCELLED"}
        owner.source_type = "INTERNAL"
        text = owner.text_block
        if text is None:
            text = bpy.data.texts.new(owner.sn_template_name)
        text.clear()
        text.write(owner.sn_template)
        owner.text_block = text
        return {"FINISHED"}


class SNA_OT_EditScript(bpy.types.Operator):
    """Show the script in a Text Editor (a new window if there is none)"""

    bl_idname = "sna.edit_script"
    bl_label = "Edit Script"
    bl_options = {"REGISTER", "INTERNAL"}

    owner_id: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        owner = _owner(self.owner_id)
        if owner is None or owner.text_block is None:
            return {"CANCELLED"}
        editors = [a for a in context.screen.areas if a.type == "TEXT_EDITOR"]
        if not editors:
            bpy.ops.wm.window_new()
            editors = context.window_manager.windows[-1].screen.areas[:1]
            editors[0].type = "TEXT_EDITOR"
        editors[0].spaces.active.text = owner.text_block
        return {"FINISHED"}


class SNA_OT_AddScript(bpy.types.Operator):
    """Add a script to the add-on"""

    bl_idname = "sna.add_script"
    bl_label = "Add Script"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon = context.scene.sna.addon
        script = addon.scripts.add()
        script.id = get_short_id()
        addon.active_script = len(addon.scripts) - 1
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_RemoveScript(bpy.types.Operator):
    """Remove the selected script from the add-on (its text stays)"""

    bl_idname = "sna.remove_script"
    bl_label = "Remove Script"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon = context.scene.sna.addon
        index = addon.active_script
        if not 0 <= index < len(addon.scripts):
            return {"CANCELLED"}
        callers = script_list.callers(addon.scripts[index])
        addon.scripts.remove(index)
        addon.active_script = min(index, len(addon.scripts) - 1)
        for node in callers:
            node.mark_dirty()
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_AddScriptFunction(bpy.types.Operator):
    """Add a node calling this function"""

    bl_idname = "sna.add_script_function"
    bl_label = "Add Script Function"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    script_id: bpy.props.StringProperty(options={"HIDDEN"})
    function: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        space = context.space_data
        tree = getattr(space, "edit_tree", None)
        if tree is None or script_list.find(self.script_id) is None:
            return {"CANCELLED"}
        bpy.ops.node.add_node(
            "INVOKE_DEFAULT", type="SNA_Node_ScriptFunction", use_transform=True
        )
        node = tree.nodes.active
        node.script_id = self.script_id
        node.function_name = self.function
        node.mark_dirty()
        return {"FINISHED"}


class SNA_UL_Scripts(bpy.types.UIList):
    bl_idname = "SNA_UL_Scripts"

    def draw_item(self, context, layout, data, item, icon, active_data, prop):
        from ..core import errors

        row = layout.row(align=True)
        row.label(text=script_list.label(item), icon="FILE_SCRIPT")
        if errors.node_message(item.id):
            row.label(text="", icon="ERROR")


def draw_source(layout, owner):
    """Text / File and the source field of a list script or an Inline Script
    node. False if there's nothing more to draw (no source, or an empty
    text with the template button)."""
    layout.row().prop(owner, "source_type", expand=True)
    if owner.source_type == "EXTERNAL":
        layout.prop(owner, "filepath", text="")
    else:
        row = layout.row(align=True)
        row.prop(owner, "text_block", text="")
        if owner.text_block is None:
            row.operator("sna.new_script", text="", icon="ADD").owner_id = owner.id
        else:
            op = row.operator("sna.edit_script", text="", icon="TEXT")
            op.owner_id = owner.id
    if owner.source_name() is None:
        return False
    if owner.text_block is not None and not owner.text_block.as_string().strip():
        layout.label(text="The script is empty", icon="INFO")
        op = layout.operator("sna.new_script", text="Add Template", icon="FILE")
        op.owner_id = owner.id
        return False
    return True


def draw_scripts(layout, context):
    """The Scripts panel: the list, the active script, its functions and the
    nodes calling them."""
    from ..core import errors

    addon = context.scene.sna.addon
    row = layout.row()
    row.template_list(
        "SNA_UL_Scripts", "", addon, "scripts", addon, "active_script", rows=3
    )
    col = row.column(align=True)
    col.operator("sna.add_script", text="", icon="ADD")
    col.operator("sna.remove_script", text="", icon="REMOVE")
    if not 0 <= addon.active_script < len(addon.scripts):
        return
    script = addon.scripts[addon.active_script]
    if not draw_source(layout.column(), script):
        return
    message = errors.node_message(script.id)
    if message:
        box = layout.box()
        box.alert = True
        box.label(text=message.splitlines()[-1], icon="ERROR")
    try:
        functions = list(script.script().functions)
    except NodeError:
        return
    if functions:
        col = layout.column(align=True)
        col.label(text="Functions:")
        for name in functions:
            op = col.operator("sna.add_script_function", text=f"{name}()", icon="ADD")
            op.script_id, op.function = script.id, name
    callers = script_list.callers(script)
    if callers:
        box = layout.box()
        col = box.column(align=True)
        for node in callers:
            row = col.row(align=True)
            row.label(text=f"{node.function_used()}()", icon="NODE")
            row.label(text=f"[{node.id_data.name}]")
            op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM")
            op.node_id = node.id
