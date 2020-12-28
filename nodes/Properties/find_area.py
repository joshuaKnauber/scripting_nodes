import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_FindAreaNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FindAreaNode"
    bl_label = "Find Area"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def area_items(self,context):
        types = ["VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR",
                 "CLIP_EDITOR", "DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR",
                 "TEXT_EDITOR", "CONSOLE", "INFO", "TOPBAR", "STATUSBAR", "OUTLINER",
                 "PROPERTIES", "FILE_BROWSER", "PREFERENCES"]
        items = []
        for a_type in types:
            items.append((a_type,a_type.replace("_"," ").title(),a_type))
        return items
    
    
    area_type: bpy.props.EnumProperty(name="Area Type",
                                      description="The type of area to find",
                                      items=area_items)
    
    def on_create(self,context):
        self.add_blend_data_output("Area")
        self.add_boolean_output("Area exists")
    

    def draw_node(self,context,layout):
        layout.prop(self,"area_type",text="")
    

    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"""
                    """
        }