import os
import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import normalize_code, unique_collection_name, get_python_name



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
            socket.python_value = socket.name

        self._evaluate(bpy.context)

    def on_dynamic_socket_add(self, socket):
        socket = self.outputs[-2] if socket.is_output else self.inputs[-2]
        if socket in self.inputs[2:-1]:
            socket["name"] = get_python_name(socket.name, "variable")
            socket["name"] = unique_collection_name(socket.name, "variable", [inp.name for inp in self.inputs[2:-1]], "_", includes_name=True)
        elif socket in self.outputs[1:-1]:
            socket["name"] = get_python_name(socket.name, "variable")
            socket["name"] = unique_collection_name(socket.name, "variable", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)
            socket.python_value = socket.name


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
        for socket in self.outputs[1:-1]:
            socket.python_value = socket.name
        self.code_imperative = f"""
                                def run_internal_script(name, part, script_locals={{}}):
                                    try:
                                        text = "\\n".join([line.body for line in bpy.data.texts[name].lines])
                                        exec(get_script_code(text)[part], script_locals)
                                    except:
                                        print("Error when registering/unregistering or running script '" + name + "'!")

                                def run_external_script(path, part, script_locals={{}}):
                                    import os
                                    if os.path.exists(path):
                                        with open(path) as script_file:
                                            text = script_file.read()
                                            exec(get_script_code(text)[part], script_locals)
                                    else:
                                        print("Could not find script at '" + path + "'!")

                                def get_script_code(script):
                                    register = ""
                                    unregister = ""

                                    if not "def register()" in script and not "def unregister()" in script:
                                        return (script, register, unregister)
                                    if "def register()" in script:
                                        register = "def register()" + script.split("def register()")[1]
                                        for x, line in enumerate(register.split("\\n")[1:]):
                                            if not len(line) - len(line.lstrip()) and line.strip():
                                                register = "\\n".join(register.split("\\n")[:x])
                                                break
                                        script = script.replace(register, "")
                                        register += "\\nregister()"
                                    if "def unregister()" in script:
                                        unregister = "def unregister()" + script.split("def unregister()")[1]
                                        for x, line in enumerate(unregister.split("\\n")[1:]):
                                            if not len(line) - len(line.lstrip()) and line.strip():
                                                unregister = "\\n".join(unregister.split("\\n")[:x])
                                                break
                                        script = script.replace(unregister, "")
                                        unregister += "\\nunregister()"
                                    return (script, register, unregister)
        """
        script_locals = "script_locals = {"
        for socket in self.inputs[2:-1]+self.outputs[1:-1]:
            script_locals += f"'{socket.name}': {socket.name}, "
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                script_locals += f"'{ntree.python_name}': {ntree.python_name}"
        script_locals += "}"

        if self.source == "BLENDER":
            if self.script:
                self.code = f"""
                            {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 7)}
                            {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 7)}
                            {script_locals}
                            run_internal_script('{self.script.name}', 0, script_locals)
                            {self.indent([f"{socket.name} = script_locals['{socket.name}']" for socket in self.inputs[2:-1] + self.outputs[1:-1]], 7)}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
                self.code_register = f"""
                                    run_internal_script('{self.script.name}', 1)
                                    """
                self.code_unregister = f"""
                                    run_internal_script('{self.script.name}', 2)
                                    """
        elif self.source == "EXTERNAL":
            self.code = f"""
                        {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 6)}
                        {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 6)}
                        run_external_script({self.inputs['Script Path'].python_value}, 0, script_locals)
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
            self.code_register = f"""
                                run_external_script({self.inputs['Script Path'].python_value}, 1)
                                """
            self.code_unregister = f"""
                                run_external_script({self.inputs['Script Path'].python_value}, 2)
                                """

    def get_script_code(self, script):
        register = ""
        unregister = ""

        if not "def register()" in script and not "def unregister()" in script:
            return (normalize_code(script), register, unregister)

        if "def register()" in script:
            register = "def register()" + script.split("def register()")[1]
            register_lines = register.split("\n")
            for x, line in enumerate(register.split("\n")[1:]):
                if not len(line) - len(line.lstrip()) and line.strip():
                    register_lines = register_lines[:x]
                    break
            script = script.replace("\n".join(register_lines), "")
            register = normalize_code("\n".join(register_lines[1:]))

        if "def unregister()" in script:
            unregister = "def unregister()" + script.split("def unregister()")[1]
            unregister_lines = unregister.split("\n")
            for x, line in enumerate(unregister.split("\n")[1:]):
                if not len(line) - len(line.lstrip()) and line.strip():
                    unregister_lines = unregister_lines[:x]
                    break
            script = script.replace("\n".join(unregister_lines), "")
            unregister = normalize_code("\n".join(unregister_lines[1:]))
        
        return (normalize_code(script), register, unregister)


    def evaluate_export(self, context):
        for socket in self.outputs[1:-1]:
            socket.python_value = socket.name
        if self.source == "BLENDER":
            if self.script:
                script = ("", "", "")
                try:
                    text = "\n".join([line.body for line in bpy.data.texts[self.script.name].lines])
                    script = self.get_script_code(text)
                except: pass

                self.code_register = f"""{script[1]}"""
                self.code_unregister = f"""{script[2]}"""
                self.code = f"""
                            {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 7)}
                            {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 7)}
                            {self.indent(script[0], 7)}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """

        elif self.source == "EXTERNAL":
            script = ("", "", "")
            if os.path.exists(eval(self.inputs['Script Path'].python_value)):
                with open(eval(self.inputs['Script Path'].python_value), "r") as script_file:
                    text = script_file.read()
                    script = self.get_script_code(text)

            self.code_register = f"""{script[1]}"""
            self.code_unregister = f"""{script[2]}"""
            self.code = f"""
                        {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 6)}
                        {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 6)}
                        {self.indent(script[0], 6)}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        layout.prop(self, "source", expand=True)
        
        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")
        else:
            layout.prop(self.inputs["Script Path"], "value_file_path", text="Path")