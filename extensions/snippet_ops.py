import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
import os
import shutil
import json
import zipfile


class SN_SnippetCategory(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()


class SN_BoolCollection(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    enabled: bpy.props.BoolProperty(default=True)

loaded_snippets = [] # temp var for the loaded snippets

def load_snippets():
    global loaded_snippets
    installed_path = os.path.join(os.path.dirname(__file__), "installed.json")
    bpy.context.scene.sn.snippet_categories.clear()
    if os.path.exists(installed_path):
        with open(installed_path, "r") as installed:
            data = json.loads(installed.read())
            loaded_snippets = data["snippets"]
            
            for snippet in data["snippets"]:
                if not type(snippet) == str:
                    item = bpy.context.scene.sn.snippet_categories.add()
                    item.name = snippet["name"]
                    item.path = os.path.join(os.path.dirname(installed_path), "snippets", snippet["name"])
    else:
        loaded_snippets = []



class SN_OT_InstallSnippet(bpy.types.Operator, ImportHelper):
    bl_idname = "sn.install_snippet"
    bl_label = "Install Snippet"
    bl_description = "Install a single or a zip file of snippets"
    bl_options = {"REGISTER", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty( default='*.json;*.zip', options={'HIDDEN'} )

    def execute(self, context):
        _, extension = os.path.splitext(self.filepath)
        if extension in [".json", ".zip"]:
            path = os.path.join(os.path.dirname(__file__), "installed.json")
            if not os.path.exists(path):
                with open(path, "w") as data_file: data_file.write(json.dumps({ "packages": [], "snippets": [] }))
            with open(path, "r+") as data_file:
                data = json.loads(data_file.read())
                name = os.path.basename(self.filepath)
                if not name in data["snippets"]:
                    if extension == ".json":
                        data["snippets"].append(name)
                        shutil.copyfile(self.filepath, os.path.join(os.path.dirname(__file__), "snippets", name))
                    if extension == ".zip":
                        name = name.split(".")[0]
                        path = os.path.join(os.path.dirname(__file__), "snippets", name)
                        with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
                            zip_ref.extractall(path)
                        data["snippets"].append({
                                "name": name,
                                "snippets": os.listdir(path)
                            })
                data_file.seek(0)
                data_file.write(json.dumps(data, indent=4))
                data_file.truncate()
                load_snippets()
                self.report({"INFO"}, message="Snippet installed!")
        else:
            self.report({"ERROR"}, message="Please only install .json files!")
            return {"CANCELLED"}
        return {"FINISHED"}
    
    
    
class SN_OT_UninstallSnippet(bpy.types.Operator):
    bl_idname = "sn.uninstall_snippet"
    bl_label = "Uninstall Snippet"
    bl_description = "Uninstalls this snippet"
    bl_options = {"REGISTER", "INTERNAL"}
    
    index: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        path = os.path.join(os.path.dirname(__file__))
        if not os.path.exists(path):
            with open(path, "w") as data_file: data_file.write(json.dumps({ "packages": [], "snippets": [] }))
        with open(os.path.join(path, "installed.json"), "r+") as data_file:
            data = json.loads(data_file.read())
            snippet = data["snippets"].pop(self.index)
            data_file.seek(0)
            data_file.write(json.dumps(data, indent=4))
            data_file.truncate()
            if type(snippet) == str:
                os.remove(os.path.join(path, "snippets", snippet))
            else:
                shutil.rmtree(os.path.join(path, "snippets", snippet["name"]))
            load_snippets()
            self.report({"INFO"}, message="Snippet uninstalled!")
        return {"FINISHED"}
    
    
    
class SN_OT_AddSnippet(bpy.types.Operator):
    bl_idname = "sn.add_snippet"
    bl_label = "Add Snippet"
    bl_description = "Adds this snippets node"
    bl_options = {"REGISTER", "INTERNAL"}
    
    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_SnippetNode", use_transform=True)
        context.space_data.node_tree.nodes.active.path = self.path
        return {"FINISHED"}

class SN_OT_ExportSnippetDraw(bpy.types.Operator):
    bl_idname = "sn.draw_export_snippet"
    bl_label = "Draw Export Snippet Popup"
    bl_description = "Draw Export Snippet Popup"
    bl_options = {"REGISTER", "INTERNAL"}

    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def get_connected_functions(self, function_node):
        nodes = []
        for node in function_node._get_linked_nodes(started_at_trigger=True):
            if node.bl_idname == "SN_RunFunctionNode":
                parent_tree = node.ref_ntree if node.ref_ntree else node.node_tree
                if node.ref_SN_FunctionNode in parent_tree.nodes:
                    new_node = parent_tree.nodes[node.ref_SN_FunctionNode]
                    nodes.append(new_node)
                    nodes += self.get_connected_functions(new_node)
        return nodes


    def invoke(self, context, event):
        node = context.space_data.node_tree.nodes.active
        function_node = node.node_tree.nodes[node.ref_SN_FunctionNode]
        function_nodes = self.get_connected_functions(function_node)
        vars = []
        props = []
        context.scene.sn.snippet_vars_customizable.clear()
        context.scene.sn.snippet_props_customizable.clear()
        for func_node in function_nodes + [function_node]:
            for some_node in func_node._get_linked_nodes(started_at_trigger=True):
                if hasattr(some_node, "var_name") and hasattr(some_node, "ref_ntree"):
                    var = some_node.get_var()
                    if var:
                        if not var.name in vars:
                            vars.append(var.name)
                            item = context.scene.sn.snippet_vars_customizable.add()
                            item.name = var.name

                if hasattr(some_node, "prop_name"):
                    prop_src = some_node.get_prop_source()
                    if prop_src and some_node.prop_name in prop_src.properties:
                        prop = prop_src.properties[some_node.prop_name]
                        if not prop.name in props:
                            props.append(prop.name)
                            item = context.scene.sn.snippet_props_customizable.add()
                            item.name = prop.name
        
        if len(context.scene.sn.snippet_props_customizable) or len(context.scene.sn.snippet_vars_customizable):
            wm = context.window_manager
            return wm.invoke_popup(self, width=200)

        node = context.space_data.node_tree.nodes.active
        bpy.ops.sn.export_snippet("INVOKE_DEFAULT", node=node.name, tree=node.node_tree.name)
        return self.execute(context)

    def draw(self, context):
        node = context.space_data.node_tree.nodes.active
        layout = self.layout
        if len(context.scene.sn.snippet_vars_customizable):
            layout.label(text="Select editable variables:")
            for var in context.scene.sn.snippet_vars_customizable:
                layout.prop(var, "enabled", text=var.name, toggle=True)
        if len(context.scene.sn.snippet_props_customizable):
            layout.separator()
            layout.label(text="Select editable properties:")
            for prop in context.scene.sn.snippet_props_customizable:
                layout.prop(prop, "enabled", text=prop.name, toggle=True)

        layout.separator()
        row = layout.row()
        row.scale_y = 1.5
        op = row.operator("sn.export_snippet", text="Export Snippet", icon="EXPORT")
        op.node = node.name
        op.tree = node.node_tree.name

    def execute(self, context):
        return {'FINISHED'}


class SN_OT_ExportSnippet(bpy.types.Operator, ExportHelper):
    bl_idname = "sn.export_snippet"
    bl_label = "Export Snippet"
    bl_description = "Export this node as a snippet"
    bl_options = {"REGISTER", "INTERNAL"}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'}, maxlen=255)
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def get_connected_functions(self, function_node):
        nodes = []
        for node in function_node._get_linked_nodes(started_at_trigger=True):
            if node.bl_idname == "SN_RunFunctionNode":
                parent_tree = node.ref_ntree if node.ref_ntree else node.node_tree
                if node.ref_SN_FunctionNode in parent_tree.nodes:
                    new_node = parent_tree.nodes[node.ref_SN_FunctionNode]
                    nodes.append(new_node)
                    nodes += self.get_connected_functions(new_node)
        return nodes

    def get_connected_interface(self, function_node):
        nodes = []
        for node in function_node._get_linked_nodes(started_at_trigger=True):
            if node.bl_idname == "SN_RunInterfaceFunctionNode":
                parent_tree = node.ref_ntree if node.ref_ntree else node.node_tree
                if node.ref_SN_InterfaceFunctionNode in parent_tree.nodes:
                    new_node = parent_tree.nodes[node.ref_SN_InterfaceFunctionNode]
                    nodes.append(new_node)
                    nodes += self.get_connected_functions(new_node)
        return nodes

    def execute(self, context):
        data = {}
        node = bpy.data.node_groups[self.tree].nodes[self.node]
        parent_tree = node.ref_ntree if node.ref_ntree else node.node_tree
        function_node = None
        if node.bl_idname == "SN_RunFunctionNode" and node.ref_SN_FunctionNode in parent_tree.nodes:
            function_node = parent_tree.nodes[node.ref_SN_FunctionNode]
            if not function_node:
                self.report({"ERROR"}, message="No function selected!")
                return {"CANCELLED"}

            data["version"] = 3
            data["name"] = function_node.name
            data["func_name"] = function_node.func_name
            data["inputs"] = []
            data["outputs"] = []
            for inp in node.inputs:
                if not inp.hide:
                    if inp.bl_idname in ["SN_EnumSocket", "SN_EnumSetSocket"]:
                        items = [item[0] for item in inp.get_items(None)]
                        data["inputs"].append({"idname": inp.bl_idname,"name": inp.name,"subtype": inp.subtype, "enum_items": str(items)})
                    elif "Vector" in inp.bl_idname:
                        data["inputs"].append({"idname": inp.bl_idname,"name": inp.name,"subtype": inp.subtype, "size": inp.size})
                    else:
                        data["inputs"].append({"idname": inp.bl_idname,"name": inp.name,"subtype": inp.subtype})

            for out in node.outputs:
                if not out.hide:
                    data["outputs"].append({"idname": out.bl_idname,"name": out.name,"subtype": out.subtype})

            data["function"] = function_node._get_code()
            data["import"] = function_node._get_code_import()
            data["imperative"] = function_node._get_code_imperative()
            data["register"] = function_node._get_code_register()
            data["unregister"] = function_node._get_code_unregister()
            function_nodes = self.get_connected_functions(function_node)
            for func_node in function_nodes:
                data["import"] += ("\n" + func_node._get_code_import()) if func_node._get_code_import() else ""
                data["imperative"] += "\n" + func_node._get_code() + "\n" + func_node._get_code_imperative()
                data["register"] += ("\n" + func_node._get_code_register()) if func_node._get_code_register() else ""
                data["unregister"] += ("\n" + func_node._get_code_unregister()) if func_node._get_code_unregister() else ""

            variables = {}
            used_vars = []
            properties = {}
            data["variables"] = []
            data["properties"] = []
            for func_node in function_nodes + [function_node]:
                for node in func_node._get_linked_nodes(started_at_trigger=True):
                    if hasattr(node, "var_name") and hasattr(node, "ref_ntree"):
                        var = node.get_var()
                        if var:
                            if not var.node_tree.python_name + "_SNIPPET_VARS" in variables:
                                variables[var.node_tree.python_name + "_SNIPPET_VARS"] = {}

                            if not var.name in used_vars:
                                used_vars.append(var.name)
                                customizable = context.scene.sn.snippet_vars_customizable[var.name].enabled
                                data["variables"].append({"name": var.name,"python_name": var.python_name, "tree": var.node_tree.python_name, "type": var.variable_type, "customizable": customizable})
                                variables[var.node_tree.python_name + "_SNIPPET_VARS"][var.python_name] = str(var.var_default)
                                data["function"] = data["function"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")
                                data["imperative"] = data["imperative"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")
                                data["register"] = data["register"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")
                                data["unregister"] = data["unregister"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")

                    if hasattr(node, "prop_name"):
                        prop_src = node.get_prop_source()
                        if prop_src and node.prop_name in prop_src.properties:
                            prop = prop_src.properties[node.prop_name]
                            if not prop.name in properties:
                                properties[prop.python_name] = [prop.register_code.replace(prop.python_name, prop.python_name+"_SNIPPET_VARS"), prop.unregister_code.replace(prop.python_name, prop.python_name+"_SNIPPET_VARS")]
                                customizable = context.scene.sn.snippet_props_customizable[prop.name].enabled
                                data["properties"].append({"name": prop.name, "python_name": prop.python_name, "type": prop.property_type, "attach_to": prop.attach_to, "customizable": customizable})
                                data["function"] = data["function"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")
                                data["imperative"] = data["imperative"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")
                                data["register"] = data["register"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")
                                data["unregister"] = data["unregister"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")

            data["variable_defs"] = variables
            data["properties_defs"] = properties
        elif node.bl_idname == "SN_RunInterfaceFunctionNode" and node.ref_SN_InterfaceFunctionNode in parent_tree.nodes:
            function_node = parent_tree.nodes[node.ref_SN_InterfaceFunctionNode]
            if not function_node:
                self.report({"ERROR"}, message="No function selected!")
                return {"CANCELLED"}

            data["version"] = 3
            data["name"] = function_node.name
            data["func_name"] = function_node.func_name
            data["inputs"] = []
            data["outputs"] = []
            for inp in node.inputs:
                if not inp.hide:
                    if inp.bl_idname == "SN_EnumSocket":
                        items = [item[0] for item in inp.get_items(None)]
                        data["inputs"].append({"idname": inp.bl_idname,"name": inp.name,"subtype": inp.subtype, "enum_items": str(items)})
                    else:
                        data["inputs"].append({"idname": inp.bl_idname,"name": inp.name,"subtype": inp.subtype})

            data["function"] = function_node._get_code()
            data["import"] = function_node._get_code_import()
            data["imperative"] = function_node._get_code_imperative()
            data["register"] = function_node._get_code_register()
            data["unregister"] = function_node._get_code_unregister()
            function_nodes = self.get_connected_functions(function_node)
            for func_node in function_nodes:
                data["import"] += ("\n" + func_node._get_code_import()) if func_node._get_code_import() else ""
                data["imperative"] += "\n" + func_node._get_code() + "\n" + func_node._get_code_imperative()
                data["register"] += ("\n" + func_node._get_code_register()) if func_node._get_code_register() else ""
                data["unregister"] += ("\n" + func_node._get_code_unregister()) if func_node._get_code_unregister() else ""

            variables = {}
            used_vars = []
            properties = {}
            data["variables"] = []
            data["properties"] = []
            for func_node in function_nodes + [function_node]:
                for node in func_node._get_linked_nodes(started_at_trigger=True):
                    if hasattr(node, "var_name") and hasattr(node, "ref_ntree"):
                        var = node.get_var()
                        if var:
                            if not var.node_tree.python_name + "_SNIPPET_VARS" in variables:
                                variables[var.node_tree.python_name + "_SNIPPET_VARS"] = {}

                            if not var.name in used_vars:
                                used_vars.append(var.name)
                                customizable = context.scene.sn.snippet_vars_customizable[var.name].enabled
                                data["variables"].append({"name": var.name,"python_name": var.python_name, "tree": var.node_tree.python_name, "type": var.variable_type, "customizable": customizable})
                                variables[var.node_tree.python_name + "_SNIPPET_VARS"][var.python_name] = str(var.var_default)
                                data["function"] = data["function"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")
                                data["imperative"] = data["imperative"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")
                                data["register"] = data["register"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")
                                data["unregister"] = data["unregister"].replace(var.node_tree.python_name + "[", var.node_tree.python_name +"_SNIPPET_VARS[")

                    if hasattr(node, "prop_name"):
                        prop_src = node.get_prop_source()
                        if prop_src and node.prop_name in prop_src.properties:
                            prop = prop_src.properties[node.prop_name]
                            if not prop.name in properties:
                                properties[prop.python_name] = [prop.register_code.replace(prop.python_name, prop.python_name+"_SNIPPET_VARS"), prop.unregister_code.replace(prop.python_name, prop.python_name+"_SNIPPET_VARS")]
                                customizable = context.scene.sn.snippet_props_customizable[prop.name].enabled
                                data["properties"].append({"name": prop.name, "python_name": prop.python_name, "type": prop.property_type, "customizable": customizable})
                                data["function"] = data["function"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")
                                data["imperative"] = data["imperative"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")
                                data["register"] = data["register"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")
                                data["unregister"] = data["unregister"].replace(prop.python_name, prop.python_name +"_SNIPPET_VARS")

            data["variable_defs"] = variables
            data["properties_defs"] = properties


        with open(self.filepath, "w") as data_file:
            data_file.seek(0)
            data_file.write(json.dumps(data, indent=4))
            data_file.truncate()
        if data:
            self.report({"INFO"}, message="Snippet exported!")
        bpy.ops.sn.snippet_info("INVOKE_DEFAULT")
        return {"FINISHED"}



class SN_OT_SnippetInfo(bpy.types.Operator):
    bl_idname = "sn.snippet_info"
    bl_label = "Snippet Info"
    bl_description = "Info"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Awesome snippet!", icon="FUND")
        col = layout.column(align=True)
        col.label(text="Do you think others could use this too?")
        col.label(text="Why not share it with the Serpens community?")
        row = col.row()
        row.operator("wm.url_open", text="Upload it to the #marketplace channel!", icon_value=bpy.context.scene.sn_icons["discord"].icon_id).url = "https://discord.com/invite/NK6kyae"
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)