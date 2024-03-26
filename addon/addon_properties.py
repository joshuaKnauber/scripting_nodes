import bpy


from ..core.builder import builder
from ..constants.properties import property_node_items
from .info.info_properties import SNA_AddonInfoProperties
from .references.reference_properties import SNA_Nodes
from ..core.bd_browser import property_search, operator_search


class SNA_AddonProperties(bpy.types.PropertyGroup):
    def _execute_node(
        self, node_tree_id: str, node_id: str, locals: dict, globals: dict
    ):
        """Executes the code for the given node in the given node tree during development"""
        for ntree in bpy.data.node_groups:
            if (
                getattr(ntree, "is_sn_ntree", False)
                and getattr(ntree, "id", "") == node_tree_id
            ):
                ntree._execute_node(node_id, locals, globals)

    def update_active_nodetree_index(self, context: bpy.types.Context):
        try:
            context.space_data.node_tree = bpy.data.node_groups[
                self.active_nodetree_index
            ]
        except IndexError:
            pass

    active_nodetree_index: bpy.props.IntProperty(
        default=0,
        name="Active Node Tree Index",
        description="The index of the active node tree",
        min=0,
        update=update_active_nodetree_index,
    )

    references: bpy.props.PointerProperty(type=SNA_Nodes)

    info: bpy.props.PointerProperty(type=SNA_AddonInfoProperties)

    def update_production_build(self, context: bpy.types.Context):
        builder.build_addon(
            module=builder.dev_module(), prod_build=self.production_build
        )

    production_build: bpy.props.BoolProperty(
        default=False,
        name="Use Production",
        description="Build the addon in production mode. Slower, but the addon uses the same code used when exported. Useful to test the addon before exporting",
        update=update_production_build,
    )

    last_build_was_prod: bpy.props.BoolProperty(
        default=False,
        name="Last Build Was Production",
        description="Internal prop set if the last build was in production mode",
    )

    show_node_code: bpy.props.BoolProperty(
        default=False,
        name="Show Node Code",
        description="Display the code of the selected node",
    )

    show_socket_code: bpy.props.BoolProperty(
        default=False,
        name="Show Socket Code",
        description="Display the code of the selected socket",
    )

    show_register_updates: bpy.props.BoolProperty(
        default=False,
        name="Show Node Updates",
        description="Display the register updates on the nodes",
    )

    show_node_refs: bpy.props.BoolProperty(
        default=False,
        name="Show Node References",
        description="Display the node reference structure",
    )

    draw_errors: bpy.props.BoolProperty(
        default=True, name="Draw Errors", description="Draw errors in the node editor"
    )

    def property_type_items(self, context):
        items = property_node_items(self, context)
        for i, item in enumerate(items):
            item = list(item)
            coll = self.references.get_collection(item[0])
            item[1] += f" ({len(coll.nodes) if coll else 0})"
            items[i] = tuple(item)
        return items

    property_type: bpy.props.EnumProperty(
        items=property_type_items,
        name="Property Type",
        description="The type of property to display",
    )

    def update_active_property_index(self, context: bpy.types.Context):
        pass

    active_property_index: bpy.props.IntProperty(
        default=0,
        name="Active Property Index",
        description="The index of the active property",
        min=0,
        update=update_active_property_index,
    )

    node_search: bpy.props.StringProperty(
        default="",
        name="Node Search",
        description="Search for a node by name or type",
        options={"TEXTEDIT_UPDATE"},
    )

    show_bd_browser: bpy.props.BoolProperty(
        name="Show BD Browser", default=False, description="Show the BD Browser"
    )

    bd_navigation: bpy.props.EnumProperty(
        name="Navigation",
        items=[
            ("PROPERTIES", "Properties", "Properties"),
            ("OPERATORS", "Operators", "Operators"),
        ],
        default="PROPERTIES",
    )

    def update_search(self, _):
        property_search.update_search_results(
            self.blend_data_search,
            list(self.blend_data_filter),
            self.blend_data_groupby,
        )

    blend_data_search: bpy.props.StringProperty(
        default="",
        name="Blend Data Search",
        description="Search for a blend data by name or type",
        # options={"TEXTEDIT_UPDATE"},
        update=update_search,
    )

    blend_data_filter: bpy.props.EnumProperty(
        items=[
            ("STRING", "String", "String"),
            ("INT", "Integer", "Integer"),
            ("FLOAT", "Float", "Float"),
            ("BOOLEAN", "Boolean", "Boolean"),
            ("ENUM", "Enum", "Enum"),
            ("COLLECTION", "Collection", "Collection"),
            ("POINTER", "Pointer", "Pointer"),
        ],
        name="Blend Data Filter",
        description="Filter the blend data search",
        options={"ENUM_FLAG"},
        update=update_search,
    )

    blend_data_groupby: bpy.props.EnumProperty(
        items=[
            ("VALUE", "Value", "Group by value"),
            ("NAME", "Name", "Group by name"),
        ],
        name="Blend Data Group By",
        description="Group the blend data search by value or name",
        update=update_search,
    )

    blend_data_selected_result: bpy.props.StringProperty(default="")

    operator_search: bpy.props.StringProperty(
        default="",
        name="Operator Search",
        description="Search for an operator by name or ID",
        # options={"TEXTEDIT_UPDATE"},
        update=lambda self, _: operator_search.update_search_results(
            self.operator_search
        ),
    )
