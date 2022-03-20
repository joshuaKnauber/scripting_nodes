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
            socket["name"] = unique_collection_name(socket.name, "variable", [inp.name for inp in self.inputs[2:-1]], "_", includes_name=True)
        elif socket in self.outputs[1:-1]:
            socket["name"] = get_python_name(socket.name, "variable")
            socket["name"] = unique_collection_name(socket.name, "variable", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)

        self._evaluate(bpy.context)

    def on_dynamic_socket_add(self, socket):
        socket = self.outputs[-2] if socket.is_output else self.inputs[-2]
        if socket in self.inputs[2:-1]:
            socket["name"] = get_python_name(socket.name, "variable")
            socket["name"] = unique_collection_name(socket.name, "variable", [inp.name for inp in self.inputs[2:-1]], "_", includes_name=True)
        elif socket in self.outputs[1:-1]:
            socket["name"] = get_python_name(socket.name, "variable")
            socket["name"] = unique_collection_name(socket.name, "variable", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)


    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        inp = self.add_string_input("Script Path")
        inp.subtype = "FILE_PATH"
        inp.set_hide(True)
        self.add_dynamic_data_input("Variable").is_variable = True
        out = self.add_dynamic_data_output("Variable")
        out.is_variable = True
        out.changeable = True

    def update_source(self, context):
        self.inputs["Script Path"].set_hide(self.source == "BLENDER")
        self._evaluate(context)

    source: bpy.props.EnumProperty(name="Source",
                            description="The source of where to get the code from",
                            items=[("BLENDER", "Blender", "Blender"),
                                    ("EXTERNAL", "External", "External")],
                            update=update_source)
    
    script: bpy.props.PointerProperty(name="File", type=bpy.types.Text, update=SN_ScriptingBaseNode._evaluate)


    def _get_code_register(self):
        return super()._get_code_register()

    def evaluate(self, context):
        # TODO import code on export
        if self.source == "BLENDER":
            if self.script:
                self.code_register = f"""
                                    try:
                                        text = "\\n".join([line.body for line in bpy.data.texts["{self.script.name}"].lines])
                                        text = text.split('def register():')[1].split('def unregister(')[0]
                                        exec('def register():' + text + '\\nregister()')
                                    except:
                                        pass
                """
                self.code_unregister = f"""
                                    try:
                                        text = "\\n".join([line.body for line in bpy.data.texts["{self.script.name}"].lines])
                                        text = text.split('def unregister():')[1]
                                        exec('def unregister():' + text + '\\nunregister()')
                                    except:
                                        pass
                """
                self.code = f"""
                            {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 7)}
                            {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 7)}
                            try:
                                text = "\\n".join([line.body for line in bpy.data.texts["{self.script.name}"].lines])
                                exec(text.split('def register(')[0])
                            except:
                                print(text="Error when running script!")
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
        elif self.source == "EXTERNAL":
            self.code_import = "import os"
            self.code_register = f"""
                                if os.path.exists({self.inputs['Script Path'].python_value}):
                                    with open({self.inputs['Script Path'].python_value}, "r") as script_file:
                                        text = script_file.read().split('def register():')[1].split('def unregister(')[0]
                                        exec('def register():' + text + '\\nregister()')
                                """
            self.code_unregister = f"""
                                if os.path.exists({self.inputs['Script Path'].python_value}):
                                    with open({self.inputs['Script Path'].python_value}, "r") as script_file:
                                        text = script_file.read().split('def unregister():')[1]
                                        exec('def unregister():' + text + '\\nunregister()')
                                """
            self.code = f"""
                        {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 7)}
                        {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 7)}
                        if os.path.exists({self.inputs['Script Path'].python_value}):
                            with open({self.inputs['Script Path'].python_value}, "r") as script_file:
                                text = script_file.read().split('def register(')[0]
                                exec(text)
                        else:
                            print(text="Couldn't find script path!")
                        {self.indent(self.outputs[0].python_value, 6)}
                        """

    def draw_node(self, context, layout):
        layout.prop(self, "source", expand=True)
        
        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")