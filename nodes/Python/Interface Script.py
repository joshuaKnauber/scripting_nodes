import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_InterfaceScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InterfaceScriptNode"
    bl_label = "Interface Script"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        inp = self.add_string_input("Script Path")
        inp.subtype = "FILE_PATH"
        inp.set_hide(True)
        
    def update_source(self, context):
        self.inputs["Script Path"].set_hide(self.source == "BLENDER")
        self._evaluate(context)
        
    source: bpy.props.EnumProperty(name="Source",
                            description="The source of where to get the code from",
                            items=[("BLENDER", "Blender", "Blender"),
                                    ("EXTERNAL", "External", "External")],
                            update=update_source)
    
    script: bpy.props.PointerProperty(name="File", type=bpy.types.Text)

    def evaluate(self, context):
        # TODO import code on export, pointer doesn't update
        if self.source == "BLENDER":
            if self.script:
                self.code = f"""
                            try:
                                exec("\\n".join([line.body for line in bpy.data.texts["{self.script.name}"].lines]))
                            except:
                                layout.label(text="Error when running script!", icon="ERROR")
                            """
        elif self.source == "EXTERNAL":
            self.code_import = "import os"
            self.code = f"""
                        if os.path.exists({self.inputs['Script Path'].python_value}):
                            with open({self.inputs['Script Path'].python_value}, "r") as script_file:
                                exec(script_file.read())
                        else:
                            layout.label(text="Couldn't find script path!", icon="ERROR")
                        """
                        
    def draw_node(self, context, layout):
        layout.prop(self, "source", expand=True)
        
        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")