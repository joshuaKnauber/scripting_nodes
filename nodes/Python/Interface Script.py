import bpy
import os
from ..base_node import SN_ScriptingBaseNode
from ...utils import unique_collection_name, get_python_name


class SN_InterfaceScriptNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_InterfaceScriptNode"
    bl_label = "Interface Script"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_dynamic_data_input("Variable").is_variable = True

    
    def on_socket_name_change(self, socket):
        socket["name"] = get_python_name(socket.name, "Variable", lower=False)
        socket["name"] = unique_collection_name(socket.name, "Variable", [inp.name for inp in self.inputs[1:-1]], "_", includes_name=True)
        self._evaluate(bpy.context)

    def on_dynamic_socket_add(self, socket):
        socket["name"] = get_python_name(socket.name, "Variable", lower=False)
        socket["name"] = unique_collection_name(socket.name, "Variable", [inp.name for inp in self.inputs[1:-1]], "_", includes_name=True)
        self._evaluate(bpy.context)


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
        script_locals = "script_locals = {"
        for socket in self.inputs[1:-1]:
            script_locals += f"'{socket.name}': {socket.name}, "
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                script_locals += f"'{ntree.python_name}': {ntree.python_name}, "
        script_locals += "}"

        if self.source == "BLENDER":
            if self.script:
                self.code = f"""
                            {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[1:-1]], 7)}
                            {script_locals}
                            script_locals.update(locals())
                            try:
                                exec("\\n".join([line.body for line in bpy.data.texts["{self.script.name}"].lines]), globals(), script_locals)
                            except:
                                layout.label(text="Error when running script!", icon="ERROR")
                            """
        elif self.source == "EXTERNAL":
            self.code_import = "import os"
            path = self.external_script.replace('\\', '/')
            self.code = f"""
                        {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[1:-1]], 6)}
                        {script_locals}
                        script_locals.update(locals())
                        if os.path.exists(r"{path}"):
                            with open(r"{path}", "r") as script_file:
                                try:
                                    exec(script_file.read(), globals(), script_locals)
                                except:
                                    layout.label(text="Error when running script!", icon="ERROR")
                        else:
                            layout.label(text="Couldn't find script path!", icon="ERROR")
                        """

    def evaluate_export(self, context):
        if self.source == "BLENDER":
            if self.script:
                text = "\n".join([line.body for line in bpy.data.texts[self.script.name].lines])

                self.code = f"""
                            {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[1:-1]], 7)}
                            {self.indent(text, 7)}
                            """

        elif self.source == "EXTERNAL" and self.external_script:
            text = ""
            if os.path.exists(self.external_script):
                with open(self.external_script, "r") as script_file:
                    text = script_file.read()

            self.code = f"""
                        {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[1:-1]], 6)}
                        {self.indent(text, 6)}
                        """
                        
    def draw_node(self, context, layout):
        layout.prop(self, "source", expand=True)
        
        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")
        elif self.source == "EXTERNAL":
            layout.prop(self, "external_script", text="Path")