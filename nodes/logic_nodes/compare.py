import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_CompareNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for comparing two values'''
    bl_idname = 'SN_CompareNode'
    bl_label = "Compare Data"
    bl_icon = node_icons["LOGIC"]

    def update_operation(self, context):
        if self.operation == "None":
            self.inputs.clear()
            inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
            inp.display_shape = "SQUARE"
        else:
            self.inputs.clear()
            self.inputs.new('SN_DataSocket', "Data")
            self.inputs.new('SN_DataSocket', "Data")

        update_socket_autocompile(self, context)

    operation: bpy.props.EnumProperty(
        items=[("==", "=", "Equal to"), ("!=", "≠", "Not equal to"),
                (">", ">", "Bigger than"), ("<", "<", "Smaller than"),
                (">=", "≥", "Bigger or equal to"), ("<=", "≤", "Smaller or equal to"),
                ("None", "Existing", "Check if Data exists")],
        name="Operation",
        description="Compare operation for this node",
        update = update_operation
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_DataSocket', "Data")
        self.inputs.new('SN_DataSocket', "Data")
        self.outputs.new('SN_BooleanSocket', "Output")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self,output):
        value1 = "0"
        value2 = "0"

        errors = []

        if self.operation != "None":
            if self.inputs[0].is_linked:
                if self.inputs[0].links[0].from_socket.is_data_socket:
                    value1 = self.inputs[0].links[0].from_socket
                else:
                    errors.append("wrong_socket")
            if self.inputs[1].is_linked:
                if self.inputs[1].links[0].from_socket.is_data_socket:
                    value2 = self.inputs[1].links[0].from_socket
                else:
                    errors.append("wrong_socket")

            return {"code": [value1," ",self.operation," ",value2],"error":errors}
        else:
            if self.inputs[0].is_linked:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    value1 = self.inputs[0].links[0].from_socket
                else:
                    errors.append("wrong_socket")
            
            return {"code": [value1," != ",self.operation],"error":errors}
