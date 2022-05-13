from email.policy import default
import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyNode import PropertyNode
from ...utils import get_python_name, unique_collection_name



class SN_ModalOperatorNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyNode):

    bl_idname = "SN_ModalOperatorNode"
    bl_label = "Modal Operator"
    is_trigger = True
    bl_width_default = 200
    node_color = "PROGRAM"

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

    def evaluate(self, context):
        self.code = f"""
            class SNA_OT_{self.operator_python_name.title()}(bpy.types.Operator):
                bl_idname = "sna.{self.operator_python_name}"
                bl_label = "{self.name}"
                bl_description = "{self.operator_description}"
                bl_options = {"{" + '"REGISTER", "UNDO"' + "}"}

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
                    context.window.cursor_set("{self.cursor}")
                    {self.indent(self.outputs['Modal'].python_value, 5)}
                    if event.type in {'RIGHTMOUSE', 'ESC'}:
                        return {{'CANCELLED'}}
                    return {"{'PASS_THROUGH'}" if self.keep_interactive else "{'RUNNING_MODAL'}"}

                def invoke(self, context, event):
                    {self.indent(self.outputs['Before Modal'].python_value, 5)}
                    context.window_manager.modal_handler_add(self)
                    return {{'RUNNING_MODAL'}}
            """

        self.code_register = f"""
                bpy.utils.register_class(SNA_OT_{self.operator_python_name.title()})
                """
        self.code_unregister = f"""
                bpy.utils.unregister_class(SNA_OT_{self.operator_python_name.title()})
                """