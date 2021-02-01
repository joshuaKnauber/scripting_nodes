import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_CreateFolderNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateFolderNode"
    bl_label = "Create Folder"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_execute_input("Create Folder")
        self.add_string_input("Path").subtype = "DIRECTORY"
        self.add_string_input("Name").set_default("New Folder")
        self.add_execute_output("Execute").mirror_name = True
        self.add_string_output("New Path").subtype = "DIRECTORY"


    def code_evaluate(self, context, touched_socket):
        path = self.inputs["Path"].code()
        name = self.inputs["Name"].code()

        if touched_socket == self.outputs[1]:
            if path and name:
                return {
                    "code": f"os.path.join({path},{name})"
                }
        else:
            if path and name:
                return {
                    "code": f"""
                            if not os.path.exists(os.path.join({path},{name})):
                                os.mkdir(os.path.join({path},{name}))
                            {self.outputs[0].code(7)}
                            """
                }
        
        return {"code": f""}