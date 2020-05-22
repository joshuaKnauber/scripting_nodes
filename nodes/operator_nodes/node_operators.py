import bpy


class SN_OT_RunFunctionNode(bpy.types.Operator):
    bl_idname = "scripting_nodes.run_function_node"
    bl_label = "Run function"
    bl_description = "Runs this function"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        tree = context.space_data.node_tree
        for node in tree.nodes:
            if node.name == self.node_name:
                function = tree.compiler.get_function_code(node)

                try:
                    exec(function)
                except:
                    self.report({"ERROR"},message="Something went wrong when running this function. Share the code in the console with the devs for help!")
                    print(function)
        return {"FINISHED"}