import bpy

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodeDrawCheckbox(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeDrawCheckbox"
    bl_label = "Draw Checkbox"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.PROPERTY, "Boolean Property")
        inp = self.add_input(sockets.STRING, "Label")
        inp.make_disabled()
        inp = self.add_input(sockets.ICON)
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Toggle Button")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Emboss")
        inp.make_disabled()
        inp = self.add_input(sockets.BOOLEAN, "Invert")
        inp.make_disabled()
        self.add_output(sockets.INTERFACE)

    def generate(self, context, trigger):
        layout = self.inputs["Interface"].get_meta("layout", "self.layout")

        if self.inputs["Boolean Property"].has_next():
            parent = self.inputs["Boolean Property"].get_meta(
                "parent", "bpy.context.scene"
            )
            identifier = self.inputs["Boolean Property"].get_meta(
                "identifier", "not_a_property"
            )
            label = (
                self.inputs["Label"].editable
                and f", text={self.inputs['Label'].get_code()}"
                or ""
            )
            toggle = (
                self.inputs["Toggle Button"].editable
                and f", toggle={self.inputs['Toggle Button'].get_code()}"
                or ""
            )
            emboss = (
                self.inputs["Emboss"].editable
                and f", emboss={self.inputs['Emboss'].get_code()}"
                or ""
            )
            invert = (
                self.inputs["Invert"].editable
                and f", invert_checkbox={self.inputs['Invert'].get_code()}"
                or ""
            )
            icon = (
                self.inputs["Icon"].editable
                and f", {self.inputs['Icon'].get_code()}"
                or ""
            )
            self.code = f"""
                {layout}.prop({parent}, "{identifier}"{label}{toggle}{emboss}{invert}{icon})
                {self.outputs["Interface"].get_code(4)}
            """
        else:
            self.code = f"""
                {layout}.label(text="No property connected!")
                {self.outputs["Interface"].get_code(4)}
            """

        self.outputs["Interface"].set_meta("layout", layout)
