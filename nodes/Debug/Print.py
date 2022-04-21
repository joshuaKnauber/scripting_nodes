import bpy
from ..base_node import SN_ScriptingBaseNode



class PrintProperty(bpy.types.PropertyGroup):

    text: bpy.props.StringProperty()
    
    
    
class SN_OT_ClearPrints(bpy.types.Operator):
    bl_idname = "sn.clear_prints"
    bl_label = "Clear Prints"
    bl_description = "Clear this print nodes messages"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.data.node_groups[self.node_tree].nodes[self.node].messages.clear()
        return {"FINISHED"}




class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    messages: bpy.props.CollectionProperty(type=PrintProperty)
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input()
        self.add_dynamic_string_input()
        self.add_execute_output()

    def evaluate(self, context):
        self.messages.clear()
        values = [inp.python_value for inp in self.inputs[1:-1]]
        self.code = f"""
                    print({", ".join(values)})
                    # This part is only added during development to display the messages on the node
                    try:
                        if '{self.node_tree.name}' in bpy.data.node_groups and '{self.name}' in bpy.data.node_groups['{self.node_tree.name}'].nodes:
                            msg = bpy.data.node_groups['{self.node_tree.name}'].nodes['{self.name}'].messages.add()
                            msg.text = str([{", ".join(values)}])[1:-1]
                        for area in bpy.context.screen.areas: area.tag_redraw()
                    except:
                        print("Can't add print outputs to the node when the print is run in an interface!")
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
                    
    def evaluate_export(self, context):
        self.messages.clear()
        values = [inp.python_value for inp in self.inputs[1:-1]]
        self.code = f"""
                    print({", ".join(values)})
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
        
    def draw_node(self, context, layout):
        if not self.messages:
            box = layout.box()
            box.label(text="Nothing printed!")
        else:
            row = layout.row()
            row.label(text="Messages:")
            op = row.operator("sn.clear_prints", text="", icon="TRASH", emboss=False)
            op.node_tree = self.node_tree.name
            op.node = self.name
            col = layout.column(align=True)
            col.scale_y = 0.9
            for msg in self.messages:
                box = col.box()
                box.label(text=msg.text)