"""Script node - embeds Python from a Text block or an external file.

Input variables are assigned before the script runs, output variables are
read after it (they are available to the nodes following in the flow).
"""

import json
import os

import bpy

from ....blend_data.path_utils import is_identifier
from ....core import scheduler
from ....core.context import NodeError
from ....core.naming import identifier
from ....lib.code_format import flatten_multiline_strings
from ....lib.trees import node_by_id, scripting_node_trees
from ....sockets.socket_types import (
    DATA_SOCKET_ENUM_ITEMS,
    DATA_SOCKET_ICONS,
    DATA_SOCKET_IDNAMES,
)
from ....sockets.spec import Flow, Socket
from ...base_node import ScriptingBaseNode

VAR_PREFIX = "var_"


class SNA_OT_ScriptVariablesSettings(bpy.types.Operator):
    """Configure script input/output variables"""

    bl_idname = "sna.script_variables_settings"
    bl_label = "Script Variables"
    bl_description = "Configure input and output variables for the script"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        node = node_by_id(self.node_id)
        if not node:
            layout.label(text="Node not found")
            return
        variables = node.get_variables()
        for is_output, title, icon in (
            (False, "Inputs", "IMPORT"),
            (True, "Outputs", "EXPORT"),
        ):
            box = layout.box()
            row = box.row()
            row.label(text=title, icon=icon)
            op = row.operator(
                "sna.script_add_variable", text="", icon="ADD", emboss=False
            )
            op.node_id = self.node_id
            op.is_output = is_output
            found = False
            for index, var in enumerate(variables):
                if var["is_output"] != is_output:
                    continue
                found = True
                row = box.row(align=True)
                row.label(
                    text="", icon=DATA_SOCKET_ICONS.get(var["socket_type"], "DOT")
                )
                row.label(text=var["name"])
                op = row.operator(
                    "sna.script_remove_variable", text="", icon="X", emboss=False
                )
                op.node_id = self.node_id
                op.var_index = index
            if not found:
                box.label(text=f"No {title.lower()}", icon="INFO")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=250)


class SNA_OT_ScriptAddVariable(bpy.types.Operator):
    """Add a variable to the script node"""

    bl_idname = "sna.script_add_variable"
    bl_label = "Add Variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    var_name: bpy.props.StringProperty(name="Name", default="variable")
    var_type: bpy.props.EnumProperty(
        items=DATA_SOCKET_ENUM_ITEMS, name="Type", default="ScriptingDataSocket"
    )
    is_output: bpy.props.BoolProperty()

    def draw(self, context):
        self.layout.prop(self, "var_name")
        self.layout.prop(self, "var_type")

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node:
            return {"CANCELLED"}
        node.add_variable(self.var_name, self.var_type, self.is_output)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SNA_OT_ScriptRemoveVariable(bpy.types.Operator):
    """Remove a variable from the script node"""

    bl_idname = "sna.script_remove_variable"
    bl_label = "Remove Variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    var_index: bpy.props.IntProperty()

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node:
            return {"CANCELLED"}
        node.remove_variable(self.var_index)
        return {"FINISHED"}


class SNA_Node_Script(ScriptingBaseNode, bpy.types.Node):
    """Run Python code from a text block or a file."""

    bl_idname = "SNA_Node_Script"
    bl_label = "Script"

    source_type: bpy.props.EnumProperty(
        items=[
            ("INTERNAL", "Internal", "Use a text block from the blend file"),
            ("EXTERNAL", "External", "Use an external Python file"),
        ],
        name="Source",
        description="Where to load the script from",
        default="INTERNAL",
    )
    text_block: bpy.props.PointerProperty(
        type=bpy.types.Text, name="Text", description="Text block with the script"
    )
    filepath: bpy.props.StringProperty(
        name="File", description="Path to a Python file", subtype="FILE_PATH"
    )
    # [{"name": str, "socket_type": str, "is_output": bool}, ...]
    variables_json: bpy.props.StringProperty(default="[]")

    # -- variables ------------------------------------------------------------

    def get_variables(self):
        try:
            variables = json.loads(self.variables_json)
        except json.JSONDecodeError:
            return []
        return [v for v in variables if isinstance(v, dict) and "name" in v]

    def set_variables(self, variables):
        self.variables_json = json.dumps(variables)  # updates the sockets

    def add_variable(self, name, socket_type, is_output):
        """Add a variable; its name is made a unique Python identifier."""
        variables = self.get_variables()
        name = identifier(name.strip(), "variable")
        taken = {v["name"] for v in variables if v["is_output"] == is_output}
        unique, i = name, 1
        while unique in taken:
            i += 1
            unique = f"{name}_{i}"
        variables.append(
            {"name": unique, "socket_type": socket_type, "is_output": is_output}
        )
        self.set_variables(variables)

    def remove_variable(self, index):
        variables = self.get_variables()
        if 0 <= index < len(variables):
            variables.pop(index)
            self.set_variables(variables)

    def socket_specs(self):
        inputs, outputs = [Flow()], [Flow("next")]
        for var in self.get_variables():
            idname = var.get("socket_type")
            if idname not in DATA_SOCKET_IDNAMES:
                idname = "ScriptingDataSocket"
            spec = Socket(idname, VAR_PREFIX + var["name"], var["name"])
            (outputs if var.get("is_output") else inputs).append(spec)
        return inputs, outputs

    # -- source -----------------------------------------------------------------

    def source_fingerprint(self):
        """Changes whenever the script source changes (see _watch_scripts)."""
        if self.source_type == "INTERNAL":
            return hash(self.text_block.as_string()) if self.text_block else None
        path = bpy.path.abspath(self.filepath) if self.filepath else ""
        try:
            stat = os.stat(path)
            return (path, stat.st_mtime_ns, stat.st_size)
        except OSError:
            return (path, None)

    def script_source(self):
        if self.source_type == "INTERNAL":
            if self.text_block is None:
                raise NodeError("Pick a text block")
            return self.text_block.as_string()
        if not self.filepath:
            raise NodeError("Pick a Python file")
        path = bpy.path.abspath(self.filepath)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as exc:
            raise NodeError(f"Can't read {path}: {exc.strerror or exc}")

    # -- code -------------------------------------------------------------------

    def emit(self, ctx):
        variables = self.get_variables()
        for var in variables:
            if not is_identifier(var["name"]):
                raise NodeError(f"Invalid variable name: {var['name']}")
        assignments = [
            f"{var['name']} = {ctx.input(VAR_PREFIX + var['name'])}"
            for var in variables
            if not var["is_output"]
        ]
        # multi-line strings become single-line literals, so the script can
        # be indented without changing their values
        script = flatten_multiline_strings(self.script_source())
        # before ctx.code(): the nodes after this one are emitted in there
        for var in variables:
            if var["is_output"]:
                ctx.output(VAR_PREFIX + var["name"], var["name"])
        ctx.code(f"""
            {ctx.join(assignments)}
            {ctx.join([script])}
            {ctx.flow("next")}
        """)

    # -- UI -------------------------------------------------------------------

    def draw(self, context, layout):
        op = layout.operator(
            "sna.script_variables_settings", text="Variables", icon="PROPERTIES"
        )
        op.node_id = self.id
        layout.prop(self, "source_type", text="")
        if self.source_type == "INTERNAL":
            layout.template_ID(self, "text_block", new="text.new", open="text.open")
        else:
            layout.prop(self, "filepath", text="")


# node id -> last seen source fingerprint
_fingerprints = {}


def _watch_scripts():
    """Text edits and file saves don't trigger RNA updates; poll for them."""
    seen = set()
    for tree in scripting_node_trees():
        for node in tree.nodes:
            if node.bl_idname != SNA_Node_Script.bl_idname:
                continue
            seen.add(node.id)
            fingerprint = node.source_fingerprint()
            if node.id in _fingerprints and _fingerprints[node.id] != fingerprint:
                node.mark_dirty()
            _fingerprints[node.id] = fingerprint
    for node_id in set(_fingerprints) - seen:
        del _fingerprints[node_id]


def register():
    scheduler.add_watcher(_watch_scripts)


def unregister():
    scheduler.remove_watcher(_watch_scripts)
    _fingerprints.clear()
