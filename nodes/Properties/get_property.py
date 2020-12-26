import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_PastePropertyPath(bpy.types.Operator):
    bl_idname = "sn.paste_property_path"
    bl_label = "Paste Property Path"
    bl_description = "Pastes your copies property path into this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()

    def execute(self, context):
        clipboard = bpy.context.window_manager.clipboard
        if "bpy." in clipboard and not ".ops." in clipboard:
            context.space_data.node_tree.nodes[self.node].copied_path = clipboard
        else:
            self.report({"WARNING"},message="Right-Click any property and click 'Copy Property' to get a correct property")
        return {"FINISHED"}




class SN_GetPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPropertyNode"
    bl_label = "Get Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    output_types = {
        "STRING": "SN_StringSocket",
        "BOOLEAN": "SN_BooleanSocket",
        "FLOAT": "SN_FloatSocket",
        "INT": "SN_IntegerSocket",
        "ENUM": "SN_StringSocket"
    }
    
    
    def add_prop_output(self,path):#bpy.data.screens["Layout"].dopesheet.filter_text
        try:
            if "[" in path[-1] and "]" in path[-1]:
                path[-1] = path[-1].split("[")[0]
            prop_path = ".".join(path)
            prop_name = prop_path.split(".")[-1]
            prop_path = (".").join(prop_path.split(".")[:-1])
            idname = "SN_DataSocket"
            if eval(prop_path+".bl_rna.properties['"+prop_name+"'].type") in self.output_types:
                idname = self.output_types[eval(prop_path+".bl_rna.properties['"+prop_name+"'].type")]
            self.add_output(idname,eval(prop_path+".bl_rna.properties['"+prop_name+"'].name"),False)
        except ValueError:
            self.reset_node()
    
    
    def update_path(self,context):
        if self.copied_path:
            try:
                path = self.copied_path.split(".")
                path_combined = ""
                for index, part in enumerate(path):
                    path_combined += "."+part if path_combined else part
                    if "[" and "]" in part and not index == len(path)-1:
                        name = eval(path_combined+".bl_rna.name")
                        if part.split("[")[-1].split("]")[0].isnumeric():
                            self.add_integer_input("Index - "+name)
                        else:
                            if not eval(path_combined+".bl_rna.base.name") in [name, "ID"]:
                                name += f" ({eval(path_combined+'.bl_rna.base.name')})"
                            self.add_blend_data_input(name)
                self.add_prop_output(path)
            except ValueError:
                self.reset_node()
    
    
    copied_path: bpy.props.StringProperty(update=update_path)
    
    
    def reset_node(self):
        self.copied_path = ""
        self.inputs.clear()
        self.outputs.clear()
    
    
    def on_copy(self,node):
        self.reset_node()
        

    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
    

    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"""
                    """
        }