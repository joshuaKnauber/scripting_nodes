from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.code.format import indent
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
        self.add_input("ScriptingProgramSocket", "Program")
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Item")
        index_input = self.add_input("ScriptingIntegerSocket", "Index")
        index_input.hide = True
        self.add_output("ScriptingProgramSocket", "Program")
        self.add_output("ScriptingListSocket", "Result")

    def draw(self, context, layout):
        layout.prop(self, "operation", text="")

    def generate(self):
        list_input = self.inputs["List"].eval()
        item = self.inputs["Item"].eval()
        result_list = f"list_{self.id}"

        if self.operation == "APPEND":
            self.code = f"""
                {result_list} = {list_input}.copy()
                {result_list}.append({item})
                {indent(self.outputs[0].eval(), 3)}
            """
        elif self.operation == "PREPEND":
            self.code = f"""
                {result_list} = {list_input}.copy()
                {result_list}.insert(0, {item})
                {indent(self.outputs[0].eval(), 3)}
            """
        elif self.operation == "INSERT":
            index = self.inputs["Index"].eval()
            self.code = f"""
                {result_list} = {list_input}.copy()
                {result_list}.insert({index}, {item})
                {indent(self.outputs[0].eval(), 3)}
            """

        self.outputs[1].code = result_list
