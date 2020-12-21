import bpy
from ...node_tree.node_categories import get_node_categories
        
        
        
class SN_OT_RunAddMenu(bpy.types.Operator):
    bl_idname = "sn.run_add_menu"
    bl_label = "Run Add Menu"
    bl_description = "Opens the add menu"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self,context,event):
        from_node = context.space_data.node_tree.nodes.active
        if event.shift and event.type == "LEFTMOUSE" and from_node and from_node.select:
            context.scene.compatible_nodes.clear()
            for category in get_node_categories():
                for node in category.items(context):
                    item = context.scene.compatible_nodes.add()
                    item.category = category.name
                    item.name = "  "+node.label
                    item.idname = node.nodetype
            
            bpy.ops.wm.call_menu(name="SN_MT_AddNodeMenu")
        return {"FINISHED"}
    
    

class SN_OT_AddNode(bpy.types.Operator):
    bl_idname = "sn.add_node"
    bl_label = "Add Node"
    bl_description = "Adds this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    idname: bpy.props.StringProperty()

    def execute(self, context):
        from_node = context.space_data.node_tree.nodes.active
        bpy.ops.node.add_node(type=self.idname)
        node = context.space_data.node_tree.nodes.active
        node.location = (node.location[0],node.location[1])
        
        return {"FINISHED"}
    
    def invoke(self,context,event):
        
        return self.execute(context)
    


class SN_MT_AddNodeMenu(bpy.types.Menu):
    bl_idname = "SN_MT_AddNodeMenu"
    bl_label = "Add Compatible"

    def draw(self, context):
        layout = self.layout
        
        categories = {}
        for item in context.scene.compatible_nodes:
            if not item.category in categories:
                categories[item.category] = []
            categories[item.category].append(item)
            
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("node.add_search",text="Search...",icon="VIEWZOOM").use_transform = True
        for category in categories:
            layout.label(text=category)
            for item in categories[category]:
                op = layout.operator("sn.add_node", text=item.name)
                op.idname = item.idname