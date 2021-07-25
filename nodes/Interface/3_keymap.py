import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_PasteShortcut(bpy.types.Operator):
    bl_idname = "sn.paste_shortcut"
    bl_label = "Paste Shortcut"
    bl_description = "Paste shortcut in here"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE","HIDDEN"})

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        
        text = context.window_manager.clipboard
        if "keymap" in text and "item" in text:
            data = json.loads(text)
            node.item = data["item"]
            node.keymap = data["keymap"]
        return {"FINISHED"}




class SN_DisplayKeymapItem(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayKeymapItem"
    bl_label = "Keymap Item"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def setup_node(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_string_input("Label")
        self.add_boolean_input("Toggle").set_default(False)
        SN_ScriptingBaseNode.auto_compile()
    

    keymap: bpy.props.StringProperty(update=setup_node)
    item: bpy.props.StringProperty()
    
    show_type: bpy.props.EnumProperty(name="Show Item", description="Show the selected item",
                                    items=[("type","Shortcut","Show Shortcut"),
                                           ("active","Is Active","Show Active Checkbox")],
                                    update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        pass


    def draw_node(self,context,layout):
        if not self.keymap:
            layout.label(text="Only custom shortcuts are supported right now!",icon="ERROR")
            row = layout.row()
            row.enabled = False
            row.scale_y = 1.5
            row.operator("sn.paste_shortcut",icon="PASTEDOWN",text="Paste Shortcut").node = self.name
        else:
            row = layout.row()
            row.enabled = False
            row.label(text="Readd this node when editing your keymap",icon="ERROR")
            layout.prop(self,"show_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

        return {"code": f"""
                if "{self.keymap}" in bpy.context.window_manager.keyconfigs.addon.keymaps:
                    if "{self.item}" in bpy.context.window_manager.keyconfigs.addon.keymaps["{self.keymap}"].keymap_items:
                        kmi = bpy.context.window_manager.keyconfigs.addon.keymaps["{self.keymap}"].keymap_items["{self.item}"]
                        {layout}.prop(kmi, "{self.show_type}", text={self.inputs["Label"].code()}, full_event=True, toggle={self.inputs["Toggle"].code()})
                    else:
                        {layout}.label(text="Couldn't find keymap item!", icon="ERROR")
                else:
                    {layout}.label(text="Couldn't find keymap!", icon="ERROR")
                """}