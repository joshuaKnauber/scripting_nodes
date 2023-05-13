import bpy


class SN_GroupProperties(bpy.types.PropertyGroup):

    def get_name(self):
        return self["name"] if "name" in self else "Group Category"

    def set_name(self, value):
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree" and ntree.category == self.get_name():
                ntree.category = value
        self["name"] = value

    name: bpy.props.StringProperty(
        name="Name", default="Group Category", get=get_name, set=set_name)
