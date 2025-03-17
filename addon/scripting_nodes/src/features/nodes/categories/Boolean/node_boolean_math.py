from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_BooleanMath(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_BooleanMath"
    bl_label = "Boolean Math"

    def update_data_type(self, context):
        self._generate()

    comparison: bpy.props.EnumProperty(
        items=[
            ("AND", "And", ""),
            ("OR", "Or", ""),
        ],
        name="Comparison",
        default="AND",
        update=update_data_type,
    )

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", "Boolean")
        self.add_input("ScriptingBooleanSocket", "Boolean")
        inp = self.add_input("ScriptingDynamicAddInputSocket", "Add Input")
        inp.add_socket_type = "ScriptingBooleanSocket"
        inp.add_socket_name = "Boolean"
        self.add_output("ScriptingBooleanSocket", "Result")

    def draw(self, context, layout):
        layout.prop(self, "comparison", text="")

    def generate(self):
        boolean_inputs = []
        for socket in self.inputs:
            if socket.bl_idname == "ScriptingBooleanSocket" and socket.is_linked:
                boolean_inputs.append(socket.eval())

        operator = f" {self.comparison.lower()} "
        self.outputs["Result"].code = f"({operator.join(boolean_inputs)})"
