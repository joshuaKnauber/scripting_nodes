import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import unique_collection_name, get_python_name



class SN_RunScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunScriptNode"
    bl_label = "Run Script"
    node_color = "PROGRAM"
    bl_width_default = 200

    def on_socket_name_change(self, socket):
        if socket in self.inputs[2:-1]:
            socket["name"] = get_python_name(socket.name, "variable")
            socket["name"] = unique_collection_name(socket.name, "variable", [inp.name for inp in self.inputs[2:-1]], "_")

    def on_dynamic_socket_add(self, socket):
        self.inputs[-2]["name"] = get_python_name(self.inputs[-2].name, "variable")
        self.inputs[-2]["name"] = unique_collection_name(self.inputs[-2].name, "variable", [inp.name for inp in self.inputs[2:-1]], "_")

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        inp = self.add_string_input("Script Path")
        inp.subtype = "FILE_PATH"
        inp.set_hide(True)
        self.add_dynamic_data_input("Variable").is_variable = True

    def update_source(self, context):
        self.inputs["Script Path"].set_hide(self.source == "BLENDER")
        self._evaluate(context)

    source: bpy.props.EnumProperty(name="Source",
                            description="The source of where to get the code from",
                            items=[("BLENDER", "Blender", "Blender"),
                                    ("EXTERNAL", "External", "External")],
                            update=update_source)
    
    script: bpy.props.PointerProperty(name="File", type=bpy.types.Text, update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        # TODO import code on export
        if self.source == "BLENDER":
            if self.script:
                self.code = f"""
                            try:
                                exec("\\n".join([line.body for line in bpy.data.texts["{self.script.name}"].lines]))
                            except:
                                print(text="Error when running script!")
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
        elif self.source == "EXTERNAL":
            self.code_import = "import os"
            self.code = f"""
                        if os.path.exists({self.inputs['Script Path'].python_value}):
                            with open({self.inputs['Script Path'].python_value}, "r") as script_file:
                                exec(script_file.read())
                        else:
                            print(text="Couldn't find script path!")
                        {self.indent(self.outputs[0].python_value, 6)}
                        """

    def draw_node(self, context, layout):
        layout.prop(self, "source", expand=True)
        
        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")