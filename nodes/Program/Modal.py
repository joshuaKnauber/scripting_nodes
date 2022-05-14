import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, normalize_code, unique_collection_name



class SN_ModalOperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_ModalOperatorNode"
    bl_label = "Modal Operator"
    is_trigger = True
    bl_width_default = 200
    node_color = "PROGRAM"
    collection_key_overwrite = "SN_OperatorNode"

    def on_node_property_change(self, property):
        self.trigger_ref_update({ "property_change": property })

    def on_node_property_add(self, property):
        property.allow_pointers = False
        self.trigger_ref_update({ "property_add": property })

    def on_node_property_remove(self, index):
        self.trigger_ref_update({ "property_remove": index })

    def on_node_property_move(self, from_index, to_index):
        self.trigger_ref_update({ "property_move": (from_index, to_index) })

    def on_node_name_change(self):
        new_name = self.name.replace("\"", "'")
        if not self.name == new_name:
            self.name = new_name
            names = []
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for ref in ntree.node_collection("SN_OperatorNode").refs:
                        names.append(ref.node.name)

            new_name = unique_collection_name(self.name, "My Operator", names, " ", includes_name=True)
            if not self.name == new_name:
                self.name = new_name
            self.trigger_ref_update()
            self._evaluate(bpy.context)

    def on_create(self, context):
        self.add_boolean_input("Disable")
        self.add_execute_output("Before Modal")
        self.add_execute_output("Modal")
        self.add_execute_output("After Modal")
    
    def update_description(self, context):
        self["operator_description"] = self.operator_description.replace("\"", "'")
        self._evaluate(context)

    operator_description: bpy.props.StringProperty(name="Description",
                            description="Description of the operator",
                            update=update_description)
    
    def cursor_items(self, context):
        items = []
        types = ['CROSSHAIR', 'DEFAULT', 'NONE', 'WAIT', 'MOVE_X', 'MOVE_Y', 'KNIFE', 'TEXT', 'PAINT_BRUSH', 'PAINT_CROSS', 'DOT', 'ERASER', 'HAND', 'SCROLL_X', 'SCROLL_Y', 'SCROLL_XY', 'EYEDROPPER', 'PICK_AREA', 'STOP', 'COPY', 'CROSS', 'MUTE', 'ZOOM_IN', 'ZOOM_OUT']
        for cursor in types:
            items.append((cursor, cursor.replace("_", " ").title(), cursor))
        return items

    cursor: bpy.props.EnumProperty(items=cursor_items,
                            name="Cursor",
                            description="The cursor to use while the modal is running",
                            update=SN_ScriptingBaseNode._evaluate)
    
    keep_interactive: bpy.props.BoolProperty(default=True,
                            name="Keep Interactive",
                            description="If this is enabled, the ui is still interactive when the modal is running",
                            update=SN_ScriptingBaseNode._evaluate)
    
    enable_escape: bpy.props.BoolProperty(default=True,
                            name="Default Escape Modal Options",
                            description="Finish the modal automatically when pressing escape or rightclicking. If this is turned off you need to add a way to finish a modal yourself",
                            update=SN_ScriptingBaseNode._evaluate)

    @property
    def operator_python_name(self):
        return get_python_name(self.name, replacement="my_generic_operator") + f"_{self.static_uid.lower()}"

    def draw_node(self, context, layout):
        layout.label(text="ESC or Rightclick to cancel the modal", icon="INFO")
        row = layout.row(align=True)
        row.prop(self, "name")
        python_name = get_python_name(self.name, replacement="my_generic_operator")
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN").name = "sna." + python_name

        layout.label(text="Description: ")
        layout.prop(self, "operator_description", text="")

        layout.prop(self, "cursor")
        layout.prop(self, "keep_interactive")

        layout.prop(self, "enable_escape")

        self.draw_list(layout)

    def evaluate(self, context):
        props_imperative_list = self.props_imperative(context).split("\n")
        props_code_list = self.props_code(context).split("\n")
        props_register_list = self.props_register(context).split("\n")
        props_unregister_list = self.props_unregister(context).split("\n")
        
        escape = """
        if event.type in ['RIGHTMOUSE', 'ESC']:
            return {'CANCELLED'}
        """
        
        self.code = f"""
            {self.indent(props_imperative_list, 3)}
        
            class SNA_OT_{self.operator_python_name.title()}(bpy.types.Operator):
                bl_idname = "sna.{self.operator_python_name}"
                bl_label = "{self.name}"
                bl_description = "{self.operator_description}"
                bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}
                
                {self.indent(props_code_list, 4)}
                
                cursor = "{self.cursor}"

                @classmethod
                def poll(cls, context):
                    return not {self.inputs[0].python_value}

                def __del__(self):
                    context = bpy.context
                    context.window.cursor_set("DEFAULT")
                    {self.indent(self.outputs['After Modal'].python_value, 5)}

                def execute(self, context):
                    return {{"FINISHED"}}
                    
                def modal(self, context, event):
                    context.window.cursor_set('{self.cursor}')
                    {self.indent(self.outputs['Modal'].python_value, 5)}
                    {self.indent(normalize_code(escape), 5) if self.enable_escape else ""}
                    return {"{'PASS_THROUGH'}" if self.keep_interactive else "{'RUNNING_MODAL'}"}

                def invoke(self, context, event):
                    self.start_pos = (event.mouse_x, event.mouse_y)
                    {self.indent(self.outputs['Before Modal'].python_value, 5)}
                    context.window_manager.modal_handler_add(self)
                    return {{'RUNNING_MODAL'}}
            """

        self.code_register = f"""
                {self.indent(props_register_list, 4)}
                bpy.utils.register_class(SNA_OT_{self.operator_python_name.title()})
                """
        self.code_unregister = f"""
                {self.indent(props_unregister_list, 4)}
                bpy.utils.unregister_class(SNA_OT_{self.operator_python_name.title()})
                """