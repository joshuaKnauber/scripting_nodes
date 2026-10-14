import bpy

from ....core.context import NodeError
from ....sockets.spec import Data, Flow
from ...base_node import ScriptingBaseNode


def _case_update(self, context):
    """Rebuild when a case changes (the node's own properties do that on
    their own)."""
    pointer = self.as_pointer()
    for node in self.id_data.nodes:
        cases = getattr(node, "cases", ())
        if any(case.as_pointer() == pointer for case in cases):
            node.mark_dirty()
            return


class SNA_SwitchCase(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(name="Value", update=_case_update)


class SNA_OT_SwitchCaseAdd(bpy.types.Operator):
    bl_idname = "sna.switch_case_add"
    bl_label = "Add Case"
    bl_description = "Add a case"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})
    remove: bpy.props.IntProperty(default=-1, options={"HIDDEN"})

    def execute(self, context):
        from ....lib.trees import node_by_id

        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        if self.remove >= 0:
            node.cases.remove(self.remove)
        else:
            node.cases.add().value = f"Case {len(node.cases)}"
        node.mark_dirty()
        return {"FINISHED"}


class SNA_Node_Switch(ScriptingBaseNode, bpy.types.Node):
    """Run the flow of the case matching a value (compared as text, e.g. an
    enum property's item), Default if none matches."""

    bl_idname = "SNA_Node_Switch"
    bl_label = "Switch"
    bl_width_default = 200

    cases: bpy.props.CollectionProperty(type=SNA_SwitchCase)

    def on_create(self):
        for value in ("A", "B"):
            self.cases.add().value = value

    def socket_specs(self):
        outputs = [Flow(f"case_{i}", case.value) for i, case in enumerate(self.cases)]
        outputs += [Flow("default", "Default"), Flow("next", "Finally")]
        return [Flow(), Data("value", "Value")], outputs

    def draw(self, context, layout):
        col = layout.column(align=True)
        for i, case in enumerate(self.cases):
            row = col.row(align=True)
            row.prop(case, "value", text="")
            op = row.operator("sna.switch_case_add", text="", icon="X")
            op.node_id, op.remove = self.id, i
        op = col.operator("sna.switch_case_add", text="Add Case", icon="ADD")
        op.node_id = self.id

    def emit(self, ctx):
        if not self.cases:
            raise NodeError("Add a case")
        value = ctx.var("value")
        branches = []
        for i, case in enumerate(self.cases):
            keyword = "if" if i == 0 else "elif"
            branches.append(f"""
                {keyword} {value} == {case.value!r}:
                    {ctx.flow(f"case_{i}")}
            """)
        ctx.code(f"""
            {value} = str({ctx.input("value")})
            {ctx.join(branches)}
            else:
                {ctx.flow("default")}
            {ctx.flow("next")}
        """)
