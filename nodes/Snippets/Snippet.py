import bpy
import os
import json

from ...utils import normalize_code, get_python_name
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode

class SN_SnippetVarsPropertyGroup(bpy.types.PropertyGroup):

    og_name: bpy.props.StringProperty(name="Old Var Name")
    python_name: bpy.props.StringProperty(name="Old Python Name")
    tree_name: bpy.props.StringProperty(name="Old Tree Name")
    type: bpy.props.StringProperty(name="Variable Type")

    def var_prop_update(self, context):
        for node in self.id_data.node_collection("SN_SnippetNode").nodes:
            for item in node.var_collection:
                if item == self:
                    node._evaluate(context)
                    return

    attach_to: bpy.props.StringProperty()
    use_custom: bpy.props.BoolProperty(name="Use Custom", description="Use custom variable instead of the standalone snippet variable", default=False)
    var_name: bpy.props.StringProperty(name="Name", update=var_prop_update)
    prop_name: bpy.props.StringProperty(name="Name", update=var_prop_update)
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Node Tree",
                                    description="Node Tree to get the variable from",
                                    poll=lambda _, ntree: ntree.bl_idname == "ScriptingNodesTree",
                                    update=var_prop_update)

    customizable: bpy.props.BoolProperty(default=True)



class SN_SnippetNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SnippetNode"
    bl_label = "Snippet"
    bl_width_default = 200

    def setup_snippet_node(self, data):
        """ This adds all in/outputs and settings to the snippet node """
        self.label = data["name"]
        for inp in data["inputs"]:
            socket = self._add_input(inp["idname"], inp["name"])
            if inp["subtype"] != "NONE":
                socket.subtype = inp["subtype"]
            if "enum_items" in inp:
                socket.subtype = "NONE"
                socket.custom_items_editable = False
                socket.items = inp["enum_items"]
        for out in data["outputs"]:
            socket = self._add_output(out["idname"], out["name"])
            if out["subtype"] != "NONE":
                socket.subtype = out["subtype"]
        for var in data["variables"]:
            item = self.var_collection.add()
            item.ref_ntree = self.node_tree
            item.og_name = var["name"]
            item.python_name = var["python_name"]
            item.tree_name = var["tree"]
            item.type = var["type"]
            if "customizable" in var:
                item.customizable = var["customizable"]
        for prop in data["properties"]:
            item = self.prop_collection.add()
            item.og_name = prop["name"]
            item.python_name = prop["python_name"]
            item.type = prop["type"]
            item.attach_to = prop["attach_to"]
            if "customizable" in prop:
                item.customizable = prop["customizable"]


    def load_snippet_file(self, path):
        _, extension = os.path.splitext(path)
        if extension in [".json", ".zip"]:
            with open(path, "r") as snippet_file:
                self.wrong_version = False
                snippet = json.loads(snippet_file.read())
                if "version" in snippet and snippet["version"] == 3:
                    self.setup_snippet_node(snippet)
                    self.data = json.dumps(snippet)
                else:
                    self.wrong_version = True
                    self.data = ""
        else:
            self.data = ""
            self["path"] = ""

    def update_snippet_path(self, context):
        if not self.path == bpy.path.abspath(self.path):
            self["path"] = bpy.path.abspath(self.path)
        if os.path.exists(self.path):
            self.var_collection.clear()
            self.prop_collection.clear()
            self.load_snippet_file(self.path)

    data: bpy.props.StringProperty(name="Data",
                                description="The data loaded from the last snippet file",
                                update=SN_ScriptingBaseNode._evaluate)

    path: bpy.props.StringProperty(name="Path", subtype="FILE_PATH",
                                description="The path to the snippet json file",
                                update=update_snippet_path)

    wrong_version: bpy.props.BoolProperty(default=False)
    var_collection: bpy.props.CollectionProperty(type=SN_SnippetVarsPropertyGroup)
    prop_collection: bpy.props.CollectionProperty(type=SN_SnippetVarsPropertyGroup)

    def variable_evaluate(self, snippet):
        for var_tree in snippet["variable_defs"]:
            self.code_imperative += var_tree.replace("SNIPPET_VARS", f"vars_{self.static_uid}") + " = {"
            for var in snippet["variable_defs"][var_tree]:
                for col_var in self.var_collection:
                    if var == col_var.python_name:
                        if not col_var.use_custom or (col_var.use_custom and (not col_var.ref_ntree or not col_var.var_name in col_var.ref_ntree.variables or col_var.type != col_var.ref_ntree.variables[col_var.var_name].variable_type)):
                            self.code_imperative += f"'{var}': {snippet['variable_defs'][var_tree][var]}, "
            self.code_imperative += "}\n"

    def property_evaluate(self, snippet):
        for prop in snippet["properties_defs"]:
            for col_prop in self.prop_collection:
                if prop == col_prop.python_name:
                    if not col_prop.use_custom or (col_prop.use_custom and (not col_prop.prop_name in bpy.context.scene.sn.properties or col_prop.type != bpy.context.scene.sn.properties[col_prop.prop_name].property_type or col_prop.attach_to != bpy.context.scene.sn.properties[col_prop.prop_name].attach_to)):
                        self.code_register += snippet["properties_defs"][prop][0].replace("SNIPPET_VARS", f"vars_{self.static_uid}") + "\n"
                        self.code_unregister += snippet["properties_defs"][prop][1].replace("SNIPPET_VARS", f"vars_{self.static_uid}") + "\n"

    def custom_var_props_evaluate(self, code):
        for var in self.var_collection:
            if var.use_custom and (bool(var.ref_ntree) and bool(var.var_name)) and (var.type == var.ref_ntree.variables[var.var_name].variable_type):
                code = code.replace(var.tree_name + f"_vars_{self.static_uid}['" + var.python_name + "']", var.ref_ntree.variables[var.var_name].data_path)
                self.code_register = self.code_register.replace(var.tree_name + f"_vars_{self.static_uid}['" + var.python_name + "']", var.ref_ntree.variables[var.var_name].data_path)
                self.code_unregister = self.code_unregister.replace(var.tree_name + f"_vars_{self.static_uid}['" + var.python_name + "']", var.ref_ntree.variables[var.var_name].data_path)

        for prop in self.prop_collection:
            if prop.use_custom and prop.prop_name in bpy.context.scene.sn.properties and prop.type == bpy.context.scene.sn.properties[prop.prop_name].property_type and prop.attach_to == bpy.context.scene.sn.properties[prop.prop_name].attach_to:
                code = code.replace(prop.python_name + "_vars_" + self.static_uid, bpy.context.scene.sn.properties[prop.prop_name].python_name)
                self.code_register = self.code_register.replace(prop.python_name + "_vars_" + self.static_uid, bpy.context.scene.sn.properties[prop.prop_name].python_name)
                self.code_unregister = self.code_unregister.replace(prop.python_name + "_vars_" + self.static_uid, bpy.context.scene.sn.properties[prop.prop_name].python_name)

        return code

    def evaluate(self, context):
        if self.data:
            snippet = json.loads(self.data)

            self.code_import = snippet["import"]
            self.code_imperative = ""
            self.code_register = ""
            self.code_unregister = ""
            self.variable_evaluate(snippet)
            self.property_evaluate(snippet)

            self.code_register += snippet["register"].replace("SNIPPET_VARS", f"vars_{self.static_uid}")
            self.code_unregister += snippet["unregister"].replace("SNIPPET_VARS", f"vars_{self.static_uid}")

            code = "\n" + normalize_code(snippet["function"])
            code = code.replace(snippet["func_name"], snippet["func_name"]+"_"+self.static_uid)
            code = code + "\n" + snippet["imperative"] + "\n"
            code = code.replace("SNIPPET_VARS", f"vars_{self.static_uid}")

            code = self.custom_var_props_evaluate(code)            
            self.code_imperative += code


            index = 1 if len(self.inputs) and self.inputs[0].bl_idname in ["SN_InterfaceSocket", "SN_ExecuteSocket"] else 0
            if len(self.inputs) and self.inputs[0].bl_idname == "SN_InterfaceSocket":
                inp_values = []
                for inp in self.inputs[1:]:
                    inp_values.append(inp.python_value)
                inp_values = ", ".join(inp_values)

                self.code = f"""
                            layout_function = {self.active_layout}
                            {snippet['func_name']}_{self.static_uid}(layout_function,{inp_values})
                            """

            else:
                inp_values = []
                for inp in self.inputs[index:]:
                    inp_values.append(inp.python_value)
                inp_values = ", ".join(inp_values)
                if len(self.inputs) and self.inputs[0].bl_idname == "SN_ExecuteSocket":
                    return_values = []
                    for i, out in enumerate(self.outputs[1:]):
                        return_values.append(get_python_name(f"{out.name}_{i}_{self.static_uid}", f"parameter_{i}_{self.static_uid}"))
                    return_names = ", ".join(return_values)

                    if return_names:
                        self.code = f"""
                                    {return_names} = {snippet['func_name']}_{self.static_uid}({inp_values})
                                    {self.indent(self.outputs[0].python_value, 9)}
                                    """
                    else:
                        self.code = f"""
                                    {snippet['func_name']}_{self.static_uid}({inp_values})
                                    {self.indent(self.outputs[0].python_value, 9)}
                                    """
                    for i, out in enumerate(self.outputs[1:]):
                        out.python_value = return_values[i]
                else:
                    if len(self.outputs) > 1:
                        for i, out in enumerate(self.outputs):
                            out.python_value = f"{snippet['func_name']}_{self.static_uid}({inp_values})[{i}]"
                    elif len(self.outputs) == 1:
                        self.outputs[-1].python_value = f"{snippet['func_name']}_{self.static_uid}({inp_values})"


    def draw_node(self, context, layout):
        if self.wrong_version:
            row = layout.row()
            row.alert = True
            row.label(text="You need to select a snippet that was created using Serpens 3!")
        if not self.data:
            layout.prop(self, "path")

        for var in self.var_collection:
            if var.customizable:
                row = layout.row(align=True)
                row.prop(var, "use_custom", text="")
                row.label(text=var.og_name)
                if var.use_custom:
                    row = layout.row(align=True)
                    row.prop_search(var, "ref_ntree", bpy.data, "node_groups", text="")
                    col = row.column(align=True)
                    col.enabled = bool(var.ref_ntree)
                    parent_tree = var.ref_ntree if var.ref_ntree else self.node_tree
                    col.prop_search(var, "var_name", parent_tree, "variables", text="")
                    row.operator("sn.tooltip", text="", icon="QUESTION").text = "Choose a '" + var.type + "' variable to assign this snippet variable to."
                    if var.ref_ntree and var.var_name in var.ref_ntree.variables:
                        if var.type != var.ref_ntree.variables[var.var_name].variable_type:
                            row = layout.row()
                            row.alert = True
                            row.label(text=f"Choose a variable of type '{var.type}'")

        for prop in self.prop_collection:
            if prop.customizable:
                row = layout.row(align=True)
                row.prop(prop, "use_custom", text="")
                row.label(text=prop.og_name)
                if prop.use_custom:
                    row = layout.row(align=True)
                    row.prop_search(prop, "prop_name", context.scene.sn, "properties", text="")
                    row.operator("sn.tooltip", text="", icon="QUESTION").text = f"Choose a '{prop.type}' property thats attached to '{prop.attach_to}' to assign this snippet property to."

                    if prop.prop_name in context.scene.sn.properties:
                        if prop.type != context.scene.sn.properties[prop.prop_name].property_type or prop.attach_to != context.scene.sn.properties[prop.prop_name].attach_to:
                            row = layout.row()
                            row.alert = True
                            row.label(text=f"Choose a property of type '{prop.type}', that's attached to '{prop.attach_to}'!")
