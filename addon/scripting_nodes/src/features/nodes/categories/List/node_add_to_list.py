# addon/scripting_nodes/src/features/nodes/categories/Data/node_add_to_list.py

from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_AddToList(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_AddToList"
    bl_label = "Add to List"

    def update_operation(self, context):
        self.inputs["Index"].hide = self.operation != "INSERT"
        self._generate()

    operation_options = [
        ("APPEND", "Append", "Add item to the end of the list"),
        ("PREPEND", "Prepend", "Add item to the beginning of the list"),
        ("INSERT", "Insert", "Insert item at a specific index"),
    ]

    operation: bpy.props.EnumProperty(
        items=operation_options,
        name="Operation",
        default="APPEND",
        update=update_operation,
    )

    def on_create(self):
        inp = self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Item")
        index_input = self.add_input("ScriptingIntegerSocket", "Index")
        index_input.hide = True
        self.add_output("ScriptingListSocket", "Result")

    def draw(self, context, layout):
        layout.prop(self, "operation", text="")

    def generate(self):
        list_input = self.inputs["List"].eval()
        item = self.inputs["Item"].eval()

        if self.operation == "APPEND":
            self.outputs[0].code = f"{list_input} + [{item}]"

        elif self.operation == "PREPEND":
            self.outputs[0].code = f"[{item}] + {list_input}"

        elif self.operation == "INSERT":
            index = self.inputs["Index"].eval()
            self.outputs[0].code = (
                f"{list_input}[:{index}] + [{item}] + {list_input}[{index}:]"
            )
