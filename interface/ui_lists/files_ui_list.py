import bpy
import os


ICONS = {
    "py": "FILE_SCRIPT",
    "txt": "FILE_TEXT",
    "json": "FILE_TEXT",
    "blend": "FILE_BLEND",
    "jpg": "FILE_IMAGE",
    "png": "FILE_IMAGE",
}


class SN_FILES_UL_items(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        row = layout.row()
        # loop because factor seems to scale items up vertically
        for _ in range(item.indents * 2):
            row.separator(factor=1)

        if os.path.isdir(item.path):
            row.prop(
                item,
                "folder_expanded",
                text="",
                emboss=False,
                icon="DISCLOSURE_TRI_DOWN"
                if item.folder_expanded
                else "DISCLOSURE_TRI_RIGHT",
            )
        icon = ICONS.get(item.name.split(".")[-1], "")
        if icon:
            row.operator(
                "sn.open_file", text="", icon=icon, emboss=False
            ).path = item.path
        row.prop(
            item,
            "name",
            text="",
            emboss=False,
        )

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_neworder = [i for i in range(len(items))]

        flag = self.bitflag_filter_item
        flt_flags = [flag if item.is_visible else 0 for item in items]

        return flt_flags, flt_neworder
