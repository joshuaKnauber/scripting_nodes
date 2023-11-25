import bpy

from .....constants import sockets
from ...base_node import SNA_BaseNode


class SNA_NodeRow(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeRow"
    bl_label = "Row"

    def on_create(self):
        self.add_input(sockets.INTERFACE)

        inp = self.add_input(sockets.STRING, "Heading")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Decorate")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Split Layout")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Active")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Enabled")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Alert")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Align")
        inp.make_disabled()
        inp = self.add_input(sockets.FLOAT_VECTOR, "Scale")
        inp.make_disabled()
        inp.size = 2
        inp.labels = "X,Y"
        inp.value = [1, 1] + [0] * 30
        inp = self.add_input(sockets.STRING, "Alignment")  # ENUM
        inp.make_disabled()
        inp = self.add_input(sockets.STRING, "Context")  # ENUM
        inp.make_disabled()

        self.add_output(sockets.INTERFACE)

    def generate(self, context):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")

        heading = (
            self.inputs["Heading"].editable
            and f", heading={self.inputs['Heading'].get_code()}"
            or ""
        )
        align = (
            self.inputs["Align"].editable and self.inputs["Align"].get_code() or "False"
        )
        props = f"align={align}{heading}"

        self.code = f"""
            row_{self.id} = {layout}.row({props})
            {self.inputs["Decorate"].editable and f"row_{self.id}.use_property_decorate = {self.inputs['Decorate'].get_code()}" or ""}
            {self.inputs["Split Layout"].editable and f"row_{self.id}.use_property_split = {self.inputs['Split Layout'].get_code()}" or ""}
            {self.inputs["Active"].editable and f"row_{self.id}.active = {self.inputs['Active'].get_code()}" or ""}
            {self.inputs["Enabled"].editable and f"row_{self.id}.enabled = {self.inputs['Enabled'].get_code()}" or ""}
            {self.inputs["Alert"].editable and f"row_{self.id}.alert = {self.inputs['Alert'].get_code()}" or ""}
            {self.inputs["Scale"].editable and f"row_{self.id}.scale_x, row_{self.id}.scale_y = {self.inputs['Scale'].get_code()}" or ""}
            {self.outputs["Interface"].get_code(3)}
        """

        self.outputs["Interface"].set_meta("layout", f"row_{self.id}")
