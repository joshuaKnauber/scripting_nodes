import bpy
import os
from ..base_node import SN_ScriptingBaseNode



class SN_InterfaceScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InterfaceScriptNode"
    bl_label = "Interface Script"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        
    source: bpy.props.EnumProperty(name="Source",
                            description="The source of where to get the code from",
                            items=[("BLENDER", "Blender", "Blender"),
                                    ("EXTERNAL", "External", "External")],
                            update=SN_ScriptingBaseNode._evaluate)
    
    script: bpy.props.PointerProperty(name="File",
                            type=bpy.types.Text,
                            update=SN_ScriptingBaseNode._evaluate)

    def update_path(self, context):
        if not self.external_script == bpy.path.abspath(self.external_script):
            self.external_script = bpy.path.abspath(self.external_script)
        self._evaluate(context)

    external_script: bpy.props.StringProperty(name="File",
            	                        subtype="FILE_PATH",
                                        description="The external file that holds your script",
                                        update=update_path)

    def evaluate(self, context):
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
            path = self.external_script.replace('\\', '/')
            self.code = f"""
                        if os.path.exists(r"{path}"):
                            with open(r"{path}", "r") as script_file:
                                exec(script_file.read())
                        else:
                            layout.label(text="Couldn't find script path!", icon="ERROR")
                        """

    def evaluate_export(self, context):
        if self.source == "BLENDER":
            if self.script:
                text = "\n".join([line.body for line in bpy.data.texts[self.script.name].lines])

                self.code = f"""
                            {self.indent(text, 7)}
                            """

        elif self.source == "EXTERNAL" and self.external_script:
            text = ""
            if os.path.exists(self.external_script):
                with open(self.external_script, "r") as script_file:
                    text = script_file.read()

            self.code = f"""
                        {self.indent(text, 6)}
                        """
                        
    def draw_node(self, context, layout):
        layout.prop(self, "source", expand=True)
        
        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")
        elif self.source == "EXTERNAL":
            layout.prop(self, "external_script", text="Path")