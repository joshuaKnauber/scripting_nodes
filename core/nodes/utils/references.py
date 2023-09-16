import bpy


class NodePointer(bpy.types.PropertyGroup):

    def update_name(self, context):
        """ Update the referenced node """
        sn = context.scene.sn
        ref = sn.references.get_ref_by_node_name(self.name)
        if ref is not None:
            self.id = ref.id
        else:
            self.id = ""
        # TODO mark node as dirty

    name: bpy.props.StringProperty(name="Name", default="", description="Name of the referenced node", update=update_name)
    id: bpy.props.StringProperty(name="ID", default="", description="ID of the referenced node")


def collection(idname: str):
    sn = bpy.context.scene.sn
    return sn.references.get_collection(idname)


def node_search(layout: bpy.types.UILayout, prop: NodePointer, idname: str):
    coll = collection(idname)
    if coll:
        layout.prop_search(prop, "name", coll, "nodes", text="")
    else:  # draw dummy prop search
        subrow = layout.row()
        subrow.enabled = False
        subrow.prop_search(prop, "name", bpy.data.node_groups[0], "nodes", text="")
