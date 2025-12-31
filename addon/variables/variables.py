import bpy
from ...utils import get_python_name, unique_collection_name
from ..properties.settings.settings import property_icons
from ...nodes.compiler import compile_addon


class SN_VariableProperties(bpy.types.PropertyGroup):

    @property
    def node_tree(self):
        return self.id_data

    # cache python names so they only have to be generated once
    cached_python_names = {}
    cached_python_name: bpy.props.StringProperty()
    cached_human_name: bpy.props.StringProperty()

    @property
    def python_name(self):
        if self.name == self.cached_human_name and self.cached_python_name:
            return self.cached_python_name
        if self.name in self.cached_python_names:
            return self.cached_python_names[self.name]

        names = []
        for var in self.node_tree.variables:
            if var == self:
                break
            names.append(var.python_name)

        name = unique_collection_name(
            f"sna_{get_python_name(self.name, 'sna_new_variable')}",
            "sna_new_variable",
            names,
            "_",
        )
        try:
            self.cached_python_name = name
            self.cached_human_name = self.name
        except AttributeError:
            pass
        self.cached_python_names[self.name] = name
        return name

    @property
    def data_path(self):
        return f"{self.node_tree.python_name}['{self.python_name}']"

    @property
    def icon(self):
        return property_icons[self.variable_type]

    def compile(self, context=None):
        """Registers the variable and unregisters previous version"""
        compile_addon()

    def get_to_update_nodes(self, name=None):
        """Get nodes that reference this variable"""
        if name is None:
            name = self.name
        to_update_nodes = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if getattr(node, "var_name", None) == name:
                        to_update_nodes.append(node)
        return to_update_nodes

    def get_unique_name(self, value):
        names = [v.name for v in self.id_data.variables if v != self]
        return unique_collection_name(value, "New Variable", names, " ")

    def update_name(self, context):
        """Called when name changes - update node references"""
        # Ensure name is unique
        unique_name = self.get_unique_name(self.name)
        if unique_name != self.name:
            self.name = unique_name
            return

        prev_name = self.prev_name
        new_name = self.name

        # Update node references if name actually changed
        if prev_name and prev_name != new_name:
            for node in self.get_to_update_nodes(prev_name):
                node.var_name = new_name

        # Store current name for next update
        self.prev_name = new_name
        self.compile()

    # Track previous name for reference updates
    prev_name: bpy.props.StringProperty()

    name: bpy.props.StringProperty(
        name="Variable Name",
        description="Name of this variable",
        default="New Variable",
        update=update_name,
    )

    def update_variable_type(self, context):
        for node in self.get_to_update_nodes():
            if hasattr(node, "on_var_changed"):
                node.on_var_changed()
        self.compile()

    variable_type: bpy.props.EnumProperty(
        name="Type",
        description="The type of data this variable stores",
        update=update_variable_type,
        items=[
            ("Data", "Data", "Stores any type of data", property_icons["Data"], 0),
            (
                "String",
                "String",
                "Stores a string of characters",
                property_icons["String"],
                1,
            ),
            (
                "Boolean",
                "Boolean",
                "Stores True or False",
                property_icons["Boolean"],
                2,
            ),
            ("Float", "Float", "Stores a decimal number", property_icons["Float"], 3),
            (
                "Integer",
                "Integer",
                "Stores an integer number",
                property_icons["Integer"],
                4,
            ),
            ("List", "List", "Stores a list of data", property_icons["List"], 5),
            (
                "Pointer",
                "Pointer",
                "Stores a reference to certain types of blend data, collection or group properties",
                property_icons["Pointer"],
                6,
            ),
            (
                "Collection",
                "Collection",
                "Stores a list of certain blend data or property groups to be displayed in lists",
                property_icons["Collection"],
                7,
            ),
        ],
    )

    string_default: bpy.props.StringProperty(
        name="Default", description="Default value for the variable", update=compile
    )
    boolean_default: bpy.props.BoolProperty(
        name="Default", description="Default value for the variable", update=compile
    )
    float_default: bpy.props.FloatProperty(
        name="Default", description="Default value for the variable", update=compile
    )
    integer_default: bpy.props.IntProperty(
        name="Default", description="Default value for the variable", update=compile
    )

    @property
    def var_default(self):
        return {
            "Data": None,
            "String": f"'{self.string_default}'",
            "Boolean": self.boolean_default,
            "Float": self.float_default,
            "Integer": self.integer_default,
            "List": [],
            "Pointer": None,
            "Collection": None,
        }[self.variable_type]
