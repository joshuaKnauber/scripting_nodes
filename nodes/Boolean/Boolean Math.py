import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BooleanMathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanMathNode"
    bl_label = "Boolean Math"
    node_color = "BOOLEAN"

    def on_create(self, context):
        self.add_boolean_input("Boolean")
        self.add_boolean_input("Boolean")
        self.add_dynamic_boolean_input("Boolean")
        self.add_boolean_output("Boolean")


    def update_operation(self, context):
        for inp in self.inputs[1:]:
            inp.enabled = self.operation != "NOT"
        self._evaluate(context)

    operation: bpy.props.EnumProperty(items=[("AND", "And", "Returns True if both inputs are True"),
                                            ("OR", "Or", "Returns True if one or both inputs are True"),
                                            ("NOT", "Not", "Returns True if the inputs is False and False if the input is True")],
                                    name="Operation",
                                    description="Operation to perform on the input booleans",
                                    update=update_operation)


    def draw_node(self, context, layout):
        layout.prop(self, "operation", text='')

    def evaluate(self, context):
        # not operation
        if self.operation == "NOT":
            self.outputs["Boolean"].python_value = f" not {self.inputs[0].python_value}"
        # and or or operation
        else:
            # get all input values
            values = []
            for inp in self.inputs[:-1]:
                if inp.enabled:
                    values.append(inp.python_value)
            # join input values on operation name
            join_op = f" {'and' if self.operation == 'AND' else 'or'} ".join(values)
            self.outputs["Boolean"].python_value = f"({join_op})"
