from .....lib.utils.code.format import indent
from .....lib.utils.node_tree.scripting_node_trees import node_by_id
from ...base_node import ScriptingBaseNode
from ....sockets.socket_types import (
    DATA_SOCKET_ENUM_ITEMS,
    DATA_SOCKET_ICONS,
)
import bpy
import os
import json


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

        # Inputs section
        box = layout.box()
        row = box.row()
        row.label(text="Inputs", icon="IMPORT")
        op = row.operator("sna.script_add_variable", text="", icon="ADD", emboss=False)
        op.node_id = self.node_id
        op.is_output = False

        input_vars = [v for v in variables if not v["is_output"]]
        if input_vars:
            for var in input_vars:
                row = box.row(align=True)
                icon = DATA_SOCKET_ICONS.get(var["socket_type"], "DOT")
                row.label(text="", icon=icon)
                row.label(text=var["name"])
                op = row.operator(
                    "sna.script_remove_variable", text="", icon="X", emboss=False
                )
                op.node_id = self.node_id
                op.var_index = variables.index(var)
        else:
            box.label(text="No input variables", icon="INFO")

        # Outputs section
        box = layout.box()
        row = box.row()
        row.label(text="Outputs", icon="EXPORT")
        op = row.operator("sna.script_add_variable", text="", icon="ADD", emboss=False)
        op.node_id = self.node_id
        op.is_output = True

        output_vars = [v for v in variables if v["is_output"]]
        if output_vars:
            for var in output_vars:
                row = box.row(align=True)
                icon = DATA_SOCKET_ICONS.get(var["socket_type"], "DOT")
                row.label(text="", icon=icon)
                row.label(text=var["name"])
                op = row.operator(
                    "sna.script_remove_variable", text="", icon="X", emboss=False
                )
                op.node_id = self.node_id
                op.var_index = variables.index(var)
        else:
            box.label(text="No output variables", icon="INFO")

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
        layout = self.layout
        layout.prop(self, "var_name")
        layout.prop(self, "var_type")

    def execute(self, context):
        node = node_by_id(self.node_id)
        if not node:
            return {"CANCELLED"}

        # Sanitize variable name to be a valid Python identifier
        var_name = self.var_name.strip()
        if not var_name:
            var_name = "variable"
        # Replace invalid chars with underscore
        var_name = "".join(c if c.isalnum() or c == "_" else "_" for c in var_name)
        if var_name[0].isdigit():
            var_name = "_" + var_name

        node.add_variable(var_name, self.var_type, self.is_output)
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
    bl_idname = "SNA_Node_Script"
    bl_label = "Script"

    def update_props(self, context):
        self._generate()

    # Source type: external file or internal text block
    source_type: bpy.props.EnumProperty(
        items=[
            ("INTERNAL", "Internal", "Use a text block from the blend file"),
            ("EXTERNAL", "External", "Use an external Python file"),
        ],
        name="Source",
        description="Where to load the script from",
        default="INTERNAL",
        update=update_props,
    )

    # Internal text block reference
    text_block: bpy.props.PointerProperty(
        type=bpy.types.Text,
        name="Text",
        description="Text block from the blend file",
        update=update_props,
    )

    # External file path
    filepath: bpy.props.StringProperty(
        name="File",
        description="Path to external Python file",
        subtype="FILE_PATH",
        update=update_props,
    )

    # JSON-encoded list of variables: [{"name": str, "socket_type": str, "is_output": bool}, ...]
    variables_json: bpy.props.StringProperty(default="[]")

    def get_variables(self):
        """Get the list of variables as Python list."""
        try:
            return json.loads(self.variables_json)
        except json.JSONDecodeError:
            return []

    def set_variables(self, variables):
        """Set the list of variables from Python list."""
        self.variables_json = json.dumps(variables)

    def add_variable(self, name, socket_type, is_output):
        """Add a new variable and create corresponding socket."""
        variables = self.get_variables()
        variables.append(
            {"name": name, "socket_type": socket_type, "is_output": is_output}
        )
        self.set_variables(variables)
        self._sync_sockets()
        self._generate()

    def remove_variable(self, index):
        """Remove a variable and its corresponding socket."""
        variables = self.get_variables()
        if 0 <= index < len(variables):
            variables.pop(index)
            self.set_variables(variables)
            self._sync_sockets()
            self._generate()

    def _sync_sockets(self):
        """Synchronize sockets with the variables list."""
        variables = self.get_variables()

        # Get expected input/output variable sockets
        input_vars = [v for v in variables if not v["is_output"]]
        output_vars = [v for v in variables if v["is_output"]]

        # Sync input sockets (after the Program input at index 0)
        # First, remove old variable input sockets
        to_remove = []
        for i, socket in enumerate(self.inputs):
            if i == 0:  # Skip Program socket
                continue
            to_remove.append(socket)
        for socket in to_remove:
            self.inputs.remove(socket)

        # Add new input sockets
        for var in input_vars:
            socket = self.add_input(var["socket_type"], var["name"])

        # Sync output sockets (after the Program output at index 0)
        # First, remove old variable output sockets
        to_remove = []
        for i, socket in enumerate(self.outputs):
            if i == 0:  # Skip Program socket
                continue
            to_remove.append(socket)
        for socket in to_remove:
            self.outputs.remove(socket)

        # Add new output sockets
        for var in output_vars:
            socket = self.add_output(var["socket_type"], var["name"])

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_output("ScriptingProgramSocket")

    def draw(self, context, layout):
        # Variables button
        row = layout.row()
        op = row.operator(
            "sna.script_variables_settings", text="Variables", icon="PROPERTIES"
        )
        op.node_id = self.id

        layout.prop(self, "source_type", text="")

        if self.source_type == "INTERNAL":
            layout.prop(self, "text_block", text="")
        else:
            layout.prop(self, "filepath", text="")

    def generate(self):
        is_production = bpy.context.scene.sna.addon.build_with_production_code
        variables = self.get_variables()

        # Build variable assignments for inputs
        input_assignments = []
        input_idx = 1  # Start after Program socket
        for var in variables:
            if not var["is_output"]:
                if input_idx < len(self.inputs):
                    socket = self.inputs[input_idx]
                    input_assignments.append(f"{var['name']} = {socket.eval()}")
                    input_idx += 1

        # Build variable code for outputs (set socket.code)
        output_idx = 1  # Start after Program socket
        for var in variables:
            if var["is_output"]:
                if output_idx < len(self.outputs):
                    socket = self.outputs[output_idx]
                    socket.code = var["name"]
                    output_idx += 1

        input_code = "\n".join(input_assignments) if input_assignments else ""

        if is_production:
            # Production: embed script content directly
            script_content = self._get_script_content()

            if not script_content.strip():
                script_content = "pass"

            self.code = f"""
                {indent(input_code, 4)}
                {indent(script_content, 4)}
                {indent(self.outputs[0].eval(), 4)}
            """
        else:
            # Development: load script content live at runtime
            if self.source_type == "INTERNAL":
                if self.text_block:
                    text_name = self.text_block.name
                    self.code = f"""
                        {indent(input_code, 6)}
                        if bpy.data.texts.get({repr(text_name)}):
                            exec(bpy.data.texts[{repr(text_name)}].as_string(), globals(), locals())
                        {indent(self.outputs[0].eval(), 6)}
                    """
                else:
                    self.code = f"""
                        {indent(input_code, 6)}
                        pass
                        {indent(self.outputs[0].eval(), 6)}
                    """
            else:
                if self.filepath:
                    filepath = bpy.path.abspath(self.filepath)
                    self.code = f"""
                        {indent(input_code, 6)}
                        if os.path.exists({repr(filepath)}):
                            with open({repr(filepath)}, 'r', encoding='utf-8') as _sna_script_file:
                                exec(_sna_script_file.read(), globals(), locals())
                        {indent(self.outputs[0].eval(), 6)}
                    """
                else:
                    self.code = f"""
                        {indent(input_code, 6)}
                        pass
                        {indent(self.outputs[0].eval(), 6)}
                    """

    def _get_script_content(self):
        """Get the script content for production embedding."""
        if self.source_type == "INTERNAL":
            if self.text_block:
                return self.text_block.as_string()
        else:
            if self.filepath:
                filepath = bpy.path.abspath(self.filepath)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            return f.read()
                    except Exception as e:
                        return f"# Error reading file: {e}"
                else:
                    return f"# File not found: {filepath}"
        return ""
