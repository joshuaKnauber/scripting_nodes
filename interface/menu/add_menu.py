import bpy
        
        
        
class SN_OT_RunAddMenu(bpy.types.Operator):
    bl_idname = "sn.run_add_menu"
    bl_label = "Run Add Menu"
    bl_description = "Opens the add menu"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self,context,event):
        if event.shift and event.type == "LEFTMOUSE":
            context.scene.compatible_nodes.clear()
            for i in range(20):
                item = context.scene.compatible_nodes.add()
                item.name = str(i)
                item.category = str(i%5)
                item.idname = "SN_BooleanNode"
            
            bpy.ops.wm.call_menu(name="SN_MT_AddNodeMenu")
        return {"FINISHED"}
    


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
        for category in categories:
            layout.label(text=category)
            for item in categories[category]:
                op = layout.operator("node.add_node", text=item.name)
                op.type = item.idname
                op.use_transform = True