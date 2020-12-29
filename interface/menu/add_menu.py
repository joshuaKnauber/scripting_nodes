import bpy
from ...node_tree.node_categories import get_node_categories
from ...node_tree.sockets.base_sockets import can_connect

        
        
        
from_socket = None
        
class SN_OT_RunAddMenu(bpy.types.Operator):
    bl_idname = "sn.run_add_menu"
    bl_label = "Run Add Menu"
    bl_description = "Opens the add menu"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()

    def execute(self, context):
        return {"FINISHED"}
    
    def guess_socket(self,context,from_node,event):
        global from_socket
        loc = from_node.location
        dim = from_node.dimensions
        # self.x & self.y -> region coords
        # loc -> view coords
        
        from_socket = from_node.outputs[0]
        
    
    def is_valid_node(self,context,from_node,idname):
        global from_socket
        if idname in ["NodeReroute","NodeFrame"]: return False
        
        temp_node = context.space_data.node_tree.nodes.new(idname)
        
        is_valid = False
        if from_socket.is_output:
            for inp in temp_node.inputs:
                if can_connect(from_socket.bl_idname,inp.bl_idname):
                    is_valid = True
                    break
        else:
            for out in temp_node.outputs:
                if can_connect(out.bl_idname,from_socket.bl_idname):
                    is_valid = True
                    break
                
        context.space_data.node_tree.nodes.remove(temp_node)
        return is_valid
        

    def invoke(self,context,event):
        from_node = context.space_data.node_tree.nodes.active
        if event.shift and event.type == "LEFTMOUSE" and from_node and from_node.select:
            context.scene.compatible_nodes.clear()
            self.guess_socket(context,from_node,event)
            for category in get_node_categories():
                for node in category.items(context):
                    if self.is_valid_node(context, from_node, node.nodetype):
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