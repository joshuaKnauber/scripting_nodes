from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
from scripting_nodes.src.lib.utils.code.format import indent
import bpy


class SNA_Node_RemoveFromList(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_RemoveFromList"
    bl_label = "Remove From List"

    def update_method(self, context):
        if self.method == "INDEX":
            if self.inputs[2].bl_idname != "ScriptingIntegerSocket":
                update_socket_type(self.inputs[2], "ScriptingIntegerSocket")
        else:
            if self.inputs[2].bl_idname != "ScriptingDataSocket":
                update_socket_type(self.inputs[2], "ScriptingDataSocket")

    def on_create(self):
        self.add_input("ScriptingProgramSocket", "Program")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Element")
        self.add_output("ScriptingProgramSocket", "Program")
        self.add_output("ScriptingListSocket", "List")

    method: bpy.props.EnumProperty(
        name="Method",
        description="How to find the element to delete",
        items=[
            ("ELEMENT", "Element", "Use the elements value to delete it"),
            ("INDEX", "Index", "Use the elements index to delete it"),
        ],
        update=update_method,
    )

    def draw(self, context, layout):
        layout.prop(self, "method", text="")

    def generate(self):
        list_var = f"list_{self.id}"
        if self.method == "ELEMENT":

            self.code = f"""
                {list_var} = {self.inputs['List'].eval()}
                {list_var}.remove({self.inputs['Element'].eval()})

                {indent(self.outputs[0].eval(), 4)}
            """
        else:

            self.code = f"""
                {list_var} = {self.inputs['List'].eval()}
                del {list_var}[{self.inputs['Element'].eval()}]

                {indent(self.outputs[0].eval(), 4)}
            """

        self.outputs[1].code = list_var
