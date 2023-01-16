import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name



class SN_DisplayCollectionListNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_DisplayCollectionListNodeNew"
    bl_label = "Display Collection List"
    node_color = "INTERFACE"
    bl_width_default = 200
    def layout_type(self, _): return "layout"

    def on_create(self, context):
        self.add_interface_input()
        self.add_collection_property_input()
        self.add_property_input("Index Property")
        self.add_integer_input("Rows")
        self.add_dynamic_interface_output("Item Row")
        self.add_dynamic_interface_output(
            "Interface").passthrough_layout_type = True
        self.add_property_output("Item")
        self.add_integer_output("Item Index")

    def update_function_node(self, context):
        self._evaluate(context)

    ref_SN_FunctionNode: bpy.props.StringProperty(name="Function",
                                                  description="Filter function which should have a single property input and return a boolean (True keeps the item, False removes it)",
                                                  update=update_function_node)

    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                         name="Function Node Tree",
                                         description="The node tree to select the function from",
                                         poll=SN_ScriptingBaseNode.ntree_poll,
                                         update=SN_ScriptingBaseNode._evaluate)

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.label(text="Filter:")
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        subrow.prop_search(self, "ref_SN_FunctionNode", bpy.data.node_groups[parent_tree.name].node_collection(
            "SN_FunctionNode"), "refs", text="")

    def evaluate(self, context):
        if self.inputs["Index Property"].is_linked and self.inputs["Collection Property"].is_linked:
            ui_list_idname = f"SNA_UL_{get_python_name(self.name, 'List')}_{self.static_uid}"

            func = None
            if self.ref_ntree and self.ref_SN_FunctionNode in self.ref_ntree.nodes:
                func = self.ref_ntree.nodes[self.ref_SN_FunctionNode]

            self.code_imperative = f"""
                                    def display_collection_id(uid, vars):
                                        id = f"coll_{{uid}}"
                                        for var in vars.keys():
                                            if var.startswith("i_"):
                                                id += f"_{{var}}_{{vars[var]}}"
                                        return id
                                    
                                    class {ui_list_idname}(bpy.types.UIList):
                                        def draw_item(self, context, layout, data, item_{self.static_uid}, icon, active_data, active_propname, index_{self.static_uid}):
                                            row = layout
                                            {self.indent([out.python_value if out.name == 'Item Row' else '' for out in self.outputs], 11)}

                                        def filter_items(self, context, data, propname):
                                            flt_flags = []
                                            for item in getattr(data, propname):
                                                if not self.filter_name or self.filter_name.lower() in item.name.lower():
                                                    if {f'{func.func_name}(item)' if func else 'True'}:
                                                        flt_flags.append(self.bitflag_filter_item)
                                                    else:
                                                        flt_flags.append(0)
                                                else:
                                                    flt_flags.append(0)
                                            return flt_flags, []
                                    """
            self.code_register = f"""
                                    bpy.utils.register_class({ui_list_idname})
                                    """
            self.code_unregister = f"""
                                    bpy.utils.unregister_class({ui_list_idname})
                                    """
            self.code = f"""
                coll_id = display_collection_id('{self.static_uid}', locals())
                {self.active_layout}.template_list('{ui_list_idname}', coll_id, {self.inputs['Collection Property'].python_source}, '{self.inputs['Collection Property'].python_attr}', {self.inputs['Index Property'].python_source}, '{self.inputs['Index Property'].python_attr}', rows={self.inputs['Rows'].python_value})
                {self.indent([out.python_value if out.name == 'Interface' else '' for out in self.outputs], 4)}
                """
            self.outputs["Item"].python_value = f"item_{self.static_uid}"
            if "Item Index" in self.outputs:
                self.outputs["Item Index"].python_value = f"index_{self.static_uid}"
        else:
            self.code = f"{self.active_layout}.label(text='No Property connected!', icon='ERROR')"
            self.outputs["Item"].reset_value()
            if "Item Index" in self.outputs:
                self.outputs["Item Index"].reset_value()
