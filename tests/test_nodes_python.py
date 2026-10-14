"""Python Expression / Statement, Get / Set Attribute, custom properties and
Set Variable's Change By / Toggle."""

import bpy
import helpers
from flow_case import FlowTestCase, errors


class PythonNodesTest(FlowTestCase):
    addon_name = "Python Test"

    def code_node(self, idname, code):
        node = self.add(idname)
        node.code = code
        helpers.flush()
        return node

    def test_expression_inputs_from_names(self):
        node = self.code_node(
            "SNA_Node_PythonExpression",
            "round(value * factor) + len([o for o in things if o]) + value",
        )
        names = [s.name for s in node.inputs]
        self.assertEqual(names, ["value", "factor", "things"])

    def test_expression_runs_with_inputs_put_in(self):
        node = self.code_node("SNA_Node_PythonExpression", "math.floor(a * 10) + b")
        number = self.add("SNA_Node_Float")
        number.value = 1.25
        self.link(number.outputs["value"], node.socket("name_a"))
        integer = self.add("SNA_Node_Integer")
        integer.value = 5
        self.link(integer.outputs["value"], node.socket("name_b"))
        self.print_value(node.outputs["result"])
        self.assertEqual(self.run_trigger(), ["17"])
        source = self.source()
        self.assertIn("import math", source)
        self.assertIn("math.floor(1.25 * 10) + 5", source)

    def test_expression_keeps_precedence(self):
        node = self.code_node("SNA_Node_PythonExpression", "a * 2")
        math = self.add("SNA_Node_Math")
        math.inputs["a"].value, math.inputs["b"].value = 1, 2  # 1 + 2
        self.link(math.outputs["result"], node.socket("name_a"))
        self.print_value(node.outputs["result"])
        self.assertEqual(self.run_trigger(), ["6.0"])

    def test_context_is_blenders(self):
        node = self.code_node("SNA_Node_PythonExpression", "context.scene.name")
        self.assertEqual(len(node.inputs), 0)
        self.print_value(node.outputs["result"])
        self.assertEqual(self.run_trigger(), ["Scene"])

    def test_statement(self):
        node = self.then("SNA_Node_PythonStatement")
        node.code = "items = [1, 2]; items.append(n); print(sum(items))"
        helpers.flush()
        self.assertEqual([s.name for s in node.inputs[1:]], ["n"])
        integer = self.add("SNA_Node_Integer")
        integer.value = 3
        self.link(integer.outputs["value"], node.socket("name_n"))
        self.assertEqual(self.run_trigger(), ["6"])

    def test_invalid_code(self):
        node = self.code_node("SNA_Node_PythonExpression", "a +")
        self.print_value(node.outputs["result"])
        helpers.flush()
        self.assertEqual(errors().node_message(node.id), "Not valid Python")
        node.code = "layout.label(text='x')"
        helpers.flush()
        self.assertEqual(
            errors().node_message(node.id), "'layout' isn't available here"
        )

    def test_attributes(self):
        setter = self.then("SNA_Node_SetAttribute")
        scene = self.add("SNA_Node_PythonExpression")
        scene.code = "context.scene"
        helpers.flush()
        self.link(scene.outputs["result"], setter.socket("data"))
        self.link(self.string("frame_end"), setter.socket("name"))
        number = self.add("SNA_Node_Integer")
        number.value = 99
        self.link(number.outputs["value"], setter.socket("value"))
        getter = self.add("SNA_Node_GetAttribute")
        self.link(scene.outputs["result"], getter.socket("data"))
        getter.socket("name").value = "frame_end"
        self.print_value(getter.outputs["value"])
        self.print_value(getter.outputs["exists"])
        self.assertEqual(self.run_trigger(), ["99", "True"])

    def test_custom_properties(self):
        scene = self.add("SNA_Node_PythonExpression")
        scene.code = "context.scene"
        helpers.flush()
        setter = self.then("SNA_Node_SetCustomProperty")
        self.link(scene.outputs["result"], setter.socket("data"))
        setter.socket("name").value = "notes"
        self.link(self.string("hello"), setter.socket("value"))
        getter = self.add("SNA_Node_GetCustomProperty")
        self.link(scene.outputs["result"], getter.socket("data"))
        getter.socket("name").value = "notes"
        self.print_value(getter.outputs["value"])
        remove = self.then("SNA_Node_SetCustomProperty")
        remove.operation = "REMOVE"
        self.link(scene.outputs["result"], remove.socket("data"))
        remove.socket("name").value = "notes"
        self.print_value(getter.outputs["exists"])
        self.assertFalse(remove.socket("value").enabled)
        self.assertEqual(self.run_trigger(), ["hello", "False"])
        self.assertNotIn("notes", bpy.context.scene)

    def test_change_and_toggle_variables(self):
        number = self.add("SNA_Node_GlobalVariable")
        number.data_type = "ScriptingIntegerSocket"
        number.label = "count"
        flag = self.add("SNA_Node_GlobalVariable")
        flag.data_type = "ScriptingBooleanSocket"
        flag.label = "flag"
        helpers.flush()
        change = self.then("SNA_Node_SetVariable")
        helpers.point(change, "var", number)
        change.operation = "ADD"
        helpers.flush()
        change.socket("value").value = 5
        toggle = self.then("SNA_Node_SetVariable")
        helpers.point(toggle, "var", flag)
        toggle.operation = "TOGGLE"
        helpers.flush()
        self.assertFalse(toggle.socket("value").enabled)
        for variable in (number, flag):
            get = self.add("SNA_Node_GetVariable")
            helpers.point(get, "var", variable)
            helpers.flush()
            self.print_value(get.outputs["value"])
        self.assertEqual(self.run_trigger(), ["5", "True"])
        self.assertEqual(self.run_trigger(), ["10", "False"])
        self.assertIn("set_count(get_count() + 5)", self.source())
