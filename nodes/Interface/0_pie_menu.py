import bpy
import re
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_PieMenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PieMenuNode"
    bl_label = "Pie Menu"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "has_collection": True,
        "collection_name_attr": "label"
    }
    
    
    label: bpy.props.StringProperty(default="New Pie Menu",
                                    name="Label",
                                    description="The label of this pie menu",
                                    update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        self.add_interface_output("Pie Menu").removable=True
        self.add_dynamic_interface_output("Pie Menu")
        
        self.add_boolean_input("Poll").set_default(True)
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"label")
        
        
    def idname(self):
        return "SNA_MT_" + re.sub(r'\W+', '', self.label.replace(" ","_")) + "_" + self.uid
        

    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"""
                    class {self.idname()}(bpy.types.Menu):
                        bl_idname = "{self.idname()}"
                        bl_label = "{self.label}"
                        
                        @classmethod
                        def poll(cls, context):
                            return {self.inputs["Poll"].code()}

                        def draw(self, context):
                            try:
                                layout = self.layout
                                layout = layout.menu_pie()
                                {self.outputs["Pie Menu"].by_name(8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in {self.label} pie menu")

                    """
        }
        
    
    def code_register(self, context):     
        return {
            "code": f"""
                    bpy.utils.register_class({self.idname()})
                    
                    """
        }
        
    
    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.utils.unregister_class({self.idname()})
                    
                    """
        }