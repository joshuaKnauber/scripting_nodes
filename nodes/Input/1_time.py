import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_TimeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TimeNode"
    bl_label = "Current Time"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "import_once": True
    }


    def on_create(self,context):
        self.add_string_output("Time")
        self.add_integer_output("Hours")
        self.add_integer_output("Minutes")
        self.add_integer_output("Seconds")
        self.add_integer_output("Milliseconds")
        self.add_string_output("Date")
        self.add_integer_output("Year")
        self.add_integer_output("Month")
        self.add_integer_output("Day")


    def code_evaluate(self, context, touched_socket):
        if touched_socket == self.outputs["Time"]:
            time_func = "str(datetime.now().time()).split(\".\")[0]"
        elif touched_socket == self.outputs["Hours"]:
            time_func = "datetime.now().time().hour"
        elif touched_socket == self.outputs["Minutes"]:
            time_func = "datetime.now().time().minute"
        elif touched_socket == self.outputs["Seconds"]:
            time_func = "datetime.now().time().second"
        elif touched_socket == self.outputs["Milliseconds"]:
            time_func = "datetime.now().time().microsecond//1000"

        elif touched_socket == self.outputs["Date"]:
            time_func = "str(datetime.now().date())"
        elif touched_socket == self.outputs["Year"]:
            time_func = "datetime.now().date().year"
        elif touched_socket == self.outputs["Month"]:
            time_func = "datetime.now().date().month"
        elif touched_socket == self.outputs["Day"]:
            time_func = "datetime.now().date().day"

        return {
            "code": f"""{time_func}"""
        }


    def code_imports(self, context):
        return {
            "code": f"""
                    from datetime import datetime
                    """
        }