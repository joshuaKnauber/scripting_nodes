import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name



class SN_DisplayCollectionListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DisplayCollectionListNode"
    bl_label = "Display Collection List"
    node_color = "INTERFACE"
    bl_width_default = 200
    layout_type = "layout"

    def on_create(self, context):
        self.add_interface_input()
        self.add_collection_property_input()
        self.add_property_input("Index Property")
        self.add_integer_input("Rows")
        self.add_dynamic_interface_output("Item Row")
        self.add_property_output("Item")

    def evaluate(self, context):
        if self.inputs["Index Property"].is_linked and self.inputs["Collection Property"].is_linked:
            ui_list_idname = f"SNA_UL_{get_python_name(self.name, 'List')}_{self.static_uid}"
            self.code_imperative = f"""
                                    class {ui_list_idname}(bpy.types.UIList):
                                        def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index_{self.static_uid}):
                                            row = layout
                                            {self.indent([out.python_value for out in self.outputs[:-2]], 11)}
                                    """
            self.code_register = f"""
                                    bpy.utils.register_class({ui_list_idname})
                                    """
            self.code_unregister = f"""
                                    bpy.utils.unregister_class({ui_list_idname})
                                    """
            self.code = f"{self.active_layout}.template_list('{ui_list_idname}', '{self.name}', {self.inputs['Collection Property'].python_source}, '{self.inputs['Collection Property'].python_attr}', {self.inputs['Index Property'].python_source}, '{self.inputs['Index Property'].python_attr}', rows={self.inputs['Rows'].python_value})"
            self.outputs["Item"].python_value = f"{self.inputs['Collection Property'].python_value}[index_{self.static_uid}]"
        else:
            self.code = f"{self.active_layout}.label(text='No Property connected!', icon='ERROR')"