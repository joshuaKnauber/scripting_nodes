import os
import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import normalize_code, unique_collection_name, get_python_name


class SN_OT_ReloadScript(bpy.types.Operator):
    bl_idname = "sn.reload_script"
    bl_label = "Reload Script"
    bl_description = "Reloads the script from the choosen source"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        node._evaluate(context)
        return {"FINISHED"}


class SN_RunScriptNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RunScriptNode"
    bl_label = "Run Script"
    node_color = "PROGRAM"
    bl_width_default = 200

    def on_socket_name_change(self, socket):
        if socket in self.inputs[2:-1]:
            socket["name"] = get_python_name(socket.name, "Variable", lower=False)
            socket["name"] = unique_collection_name(socket.name, "Variable", [inp.name for inp in self.inputs[2:-1]], "_", includes_name=True)
        elif socket in self.outputs[1:-1]:
            socket["name"] = get_python_name(socket.name, "Variable", lower=False)
            socket["name"] = unique_collection_name(socket.name, "Variable", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)
            socket.python_value = socket.name
        self._evaluate(bpy.context)

    def on_dynamic_socket_add(self, socket):
        if socket in self.inputs[2:-1]:
            socket["name"] = get_python_name(socket.name, "Variable", lower=False)
            socket["name"] = unique_collection_name(socket.name, "Variable", [inp.name for inp in self.inputs[2:-1]], "_", includes_name=True)
        elif socket in self.outputs[1:-1]:
            socket["name"] = get_python_name(socket.name, "Variable", lower=False)
            socket["name"] = unique_collection_name(socket.name, "Variable", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)
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

    def find_block_bounds(self, lines, name):
        start = -1
        end = -1
        for i, line in enumerate(lines):
            if start < 0 and name in line:
                start = i
            elif start >= 0 and len(line) - len(line.lstrip()) == 0 and line.strip():
                end = i-1
                break
        if end == -1: end = len(lines)-1
        return start, end

    def get_script_code(self, script):
        register = ""
        unregister = ""
        imports = ""

        script = script.split("\n")
        for line in script:
            if line.startswith("import ") or (line.startswith("from ") and "import " in line):
                imports += line+"\n"
                script.remove(line)
        script = "\n".join(script)

        if not "def register()" in script and not "def unregister()" in script:
            return (normalize_code(script), register, unregister, imports)

        lines = script.split("\n")

        if "def register()" in script:
            start, end = self.find_block_bounds(lines, "def register():")
            if start >= 0 and end >= 0:
                lines_register = lines[start:end+1][1:]
                register = normalize_code("\n".join(lines_register))
                after = lines[end+1:]
                lines = lines[:start] + after

        if "def unregister()" in script:
            start, end = self.find_block_bounds(lines, "def unregister():")
            if start >= 0 and end >= 0:
                lines_unregister = lines[start:end+1][1:]
                unregister = normalize_code("\n".join(lines_unregister))
                after = lines[end+1:]
                lines = lines[:start] + after

        if "if __name__ == '__main__'" in script.replace('"', "'"):
            start, end = self.find_block_bounds(lines, "if __name__ == ")
            if start >= 0 and end >= 0:
                after = lines[end+1:]
                lines = lines[:start] + after
        
        script = "\n".join(lines)
        return (normalize_code(script), register, unregister, imports)


    def evaluate(self, context):
        for socket in self.outputs[1:-1]:
            socket.python_value = socket.name
        if self.source == "BLENDER":
            if self.script:
                script = ("", "", "", "")
                text = "\n".join([line.body for line in bpy.data.texts[self.script.name].lines])
                script = self.get_script_code(text)

                self.code_register = f"""{script[1]}"""
                self.code_unregister = f"""{script[2]}"""
                self.code_import = f"""{script[3]}"""
                self.code = f"""
                            {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 7)}
                            {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 7)}
                            {self.indent(script[0], 7)}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """

        elif self.source == "EXTERNAL":
            script = ("", "", "", "")
            if os.path.exists(eval(self.inputs['Script Path'].python_value)):
                with open(eval(self.inputs['Script Path'].python_value), "r") as script_file:
                    text = script_file.read()
                    script = self.get_script_code(text)

            self.code_register = script[1]
            self.code_unregister = script[2]
            self.code_import = script[3]
            self.code = f"""
                        {self.indent([f"{inp.name} = {inp.python_value}" for inp in self.inputs[2:-1]], 6)}
                        {self.indent([f"{out.name} = None" for out in self.outputs[1:-1]], 6)}
                        {self.indent(script[0], 6)}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "source", expand=True)
        op = row.operator("sn.reload_script", text="", icon="FILE_REFRESH")
        op.node = self.name
        op.node_tree = self.node_tree.name

        if self.source == "BLENDER":
            layout.template_ID(self, "script", open="text.open", new="text.new")
        else:
            layout.prop(self.inputs["Script Path"], "value_file_path", text="Path")