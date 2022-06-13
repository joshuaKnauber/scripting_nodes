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

    print_on_node: bpy.props.BoolProperty(default=True,
                                    name="Print On Node", 
                                    description="Show print results on this node",
                                    update=SN_ScriptingBaseNode._evaluate)
    
    limit_prints: bpy.props.IntProperty(default=0, min=0,
                                    name="Amount of print messages that will be added to this node before a previous one is removed (0 is unlimited)",
                                    update=SN_ScriptingBaseNode._evaluate)
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_string_input()
        self.add_dynamic_string_input()
        self.add_execute_output()

    def evaluate(self, context):
        self.messages.clear()
        values = [inp.python_value for inp in self.inputs[1:-1]]
        self.code_imperative = f"""
        def sn_print(on_node, node, limit, *args):
            print(*args)
            if on_node:
                try:
                    msg = node.messages.add()
                    msg.text = str(args)[1:-1]
                    if limit and len(node.messages) > limit:
                        node.messages.remove(0)
                    for area in bpy.context.screen.areas: area.tag_redraw()
                except:
                    print("Can't add print outputs to the node when the print is run in an interface!")
        """
        self.code = f"""
                    sn_print({self.print_on_node}, bpy.data.node_groups['{self.node_tree.name}'].nodes['{self.name}'], {self.limit_prints}, {", ".join(values)})
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
        layout.prop(self, "print_on_node", text="Print On Node")
        if self.print_on_node:
            layout.prop(self, "limit_prints", text="Limit")
        if self.print_on_node:
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